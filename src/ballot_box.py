import os
import re
import time
import threading
import pyinotify
import traceback
import subprocess

import model.react
import model.observable

# TODO: check age
# Create a twinkle ballot box or append to existing one
# State is:
# (presidentId, raspiId, usdId, ballotBoxId, ballotBoxVersion)
# signed with private key of President.
#
# In detail for every state multiple ballot box files are generated 
# Each file contains a number of votes, ex. 10,50 or 100 votes
# and are preallocated
#
# Since when the election is closed the memory is probably
# limitated in read-only mode, we imagine following possibilities:
# ReadOnly: say('RO Memory, please...')
# Blank: no state stored, so start with first session
# AddSession: 
# AppendSession: same state, use the same ballot file of an existing session
#
# Single vote v0.1
# Could be a single byte
# 0 Not voted yet
# 1 Voted and choice 1
# ...
# 255 Voted but no choice done


def ensure_directory(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def execute_successfully(cmd):
    subproc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, err = subproc.communicate()

    # Ensure no error code returned
    assert err is None, 'cmd(%s) return error(%s)'%(cmd, err)
    return out

def match_one_group(msg, pattern):
    print 'match_one_group',pattern,msg
    ret = None
    m = re.search(pattern, msg)
    print m
    assert m is not None, 'Expected one match, 0 found'
    print m.groups()
    assert len(m.groups()) == 1, 'Expected to match 1 item'
    ret = m.group(1)

    return ret

def get_unique_certificate_id():
    out = execute_successfully('pkcs15-tool --list-certificates')
    cID = match_one_group(out, 'ID\s*: (.*)')

    return cID


def get_unique_certificate():
    # Ensure only one certificate
    cID = get_unique_certificate_id()
    cer = execute_successfully('pkcs15-tool --read-certificate '+cID)

    assert type(cer) is type('') and len(cer)>0, 'Invalid certificate type %s, len %d, %s'%(type(cer), len(cer), cer)
    print cer,len(cer)
    return cer

def save_file(dirname, filename, content):
    ensure_directory(dirname)
    with open(os.path.join(dirname, filename), 'w') as f:
        f.write(content)

def save_certificate(dirname, filename):
    cer = get_unique_certificate()

    save_file(dirname, filename, cer)

def save_processor_serial_number(dirname, filename):
    out = execute_successfully('cat /proc/cpuinfo')
    sID = match_one_group(out, 'Serial\s*:\s(.*)')
    save_file(dirname, filename, sID)
    
def save_processor_info(dirname, filename):
    out = execute_successfully('cat /proc/cpuinfo')

    save_file(dirname, filename, out)
    
def save_program_serial_number(dirname, filename):
    # Get device path of '/'
    out = execute_successfully('udevadm info -a -n /dev/root | grep serial')
    sID = match_one_group(out, 'serial}=="(.*)"')

    save_file(dirname, filename, sID)

def save_ballot_box_serial_number(dirname, filename):
    # Get device path of '/'
    out = execute_successfully('udevadm info -a -n /dev/sda1 | grep serial | head --lines=1')
    sID = match_one_group(out, 'serial}=="(.*)"')

    save_file(dirname, filename, sID)
    


@model.observable.observable('present', False, 'Ballot box presence')
@model.observable.observable('valid', False, 'Ballot box valid')
class ballot_box(pyinotify.ProcessEvent):
    
    class Store(object):
        def __init__(self):
            pass

    def __init__(self):
        print '__init__'
        self.initialized = False
        self.pathname = None
        self.lock = threading.Lock()
        self.wm = pyinotify.WatchManager() # Watch Manager
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
        self.notifier.start()
        self.wdd = self.wm.add_watch('/media', mask, rec=False)

        # Acquire initial state
        with self.lock:
            model.react.register_triggers(self)
            self.evaluate_media()
        print '__init__ DONE'

    def close(self):
        print 'ballot_box.close'
        self.wm.rm_watch(self.wdd.values())
        self.notifier.stop()
        
    def evaluate_media(self):
        L = os.listdir('/media')

        # TODO use the first partition?
        # TODO support redundant ballot_box?
        assert len(L)<=1

        if len(L)==0:
            self.pathname = None
            self.present = False
        elif len(L)==1:
            self.pathname = '/media/'+L[0]
            assert os.path.isdir(self.pathname)
            self.present = True

    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname, event
        with self.lock:
            self.evaluate_media()

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname, event
        with self.lock:
            self.evaluate_media()

    @model.react.to('ballot_box.present')
    def store_changed(self):
        if self.pathname is not None:
            # Storage just inserted
            try:
                self.store_setup()
                self.valid = True
            except:
                traceback.print_exc()

    def store_setup(self):
        print 'store_setup', self.pathname
        curstatedir = os.path.join(self.pathname, 'votanto', 'now')

        # Create base path name
        ensure_directory(curstatedir)

        # Write current files
        save_certificate(curstatedir, 'president.pem')
        save_processor_info(curstatedir, 'cpu.info')
        save_processor_serial_number(curstatedir, 'cpu.serial')
        save_program_serial_number(curstatedir, 'program.serial')
        save_ballot_box_serial_number(curstatedir, 'ballot_box.serial')

        # Look up for existing 
        
    @staticmethod
    def store():
        print 'store'

if __name__ == '__main__':
    ballot_box.store()
    print ballot_box.present

    a = ballot_box()
    time.sleep(15)
    a.close()

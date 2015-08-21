import os
import time
import threading
import pyinotify

import model.observable

# Create a scratch ballot box or append to existing one
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
# AddSessione: 
# AppendSession: same state, use the same ballot file of an existing session
# 
# 
@model.observable.observable('present', False, 'Ballot box presence')
@model.observable.observable('valid', False, 'Ballot box valid')
class ballot_box(pyinotify.ProcessEvent):
    
    def __init__(self):
        print '__init__'
        self.initialized = False
        self.pathname = None
        self.lock = threading.Lock()
        #self.wm = pyinotify.WatchManager() # Watch Manager
        #mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
        #self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
        #self.notifier.start()
        #self.wdd = self.wm.add_watch('/media', mask, rec=False)

        # Acquire initial state
        with self.lock:
            self.evaluate_media()
        print '__init__ DONE'

    def close(self):
        print 'ballot_box.close'
        #self.wm.rm_watch(self.wdd.values())
        #self.notifier.stop()
        
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

    @staticmethod
    def store():
        print 'store'

if __name__ == '__main__':
    ballot_box.store()
    print ballot_box.present

    a = ballot_box()
    time.sleep(15)
    a.close()

import time
import pyinotify

import model.observable

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname
    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

@model.observable.observable('present', False, 'Ballot box presence')
@model.observable.observable('valid', False, 'Ballot box valid')
class ballot_box(pyinotify.P:
    
    def __init__(self):
        self.lock = threading.Lock()
        self.wm = pyinotify.WatchManager() # Watch Manager
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
        notifier = pyinotify.ThreadedNotifier(self.wm, EventHandler())
        notifier.start()
        wdd = wm.add_watch('/media', mask, rec=False)

        # Acquire initial state
        self.lock.acquire()
        self.initial_list()
        self.lock.release()

    def initial_list():
        L = os.listdir('/media')

        if len(L)==1:
            self.present = True

        assert len(L)<=1

    @staticmethod
    def store():
        print 'store'

ballot_box.store()
print ballot_box.present

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname
    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

#log.setLevel(10)
time.sleep(10)
wm.rm_watch(wdd.values())
notifier.stop()

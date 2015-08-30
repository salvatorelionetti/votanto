# TODO: Fire WatchDog if not say 'welcome' in 10/20secs
import gc
import sys
import time
import threading
import traceback

import model.react
import identity
import public
import voting_booth
import ballot_box

class Enum(tuple):
    __getattr__ = tuple.index

States = Enum([
    'None',
    'Started',          # start evaluating read  input events
    'BallotBoxSetup',   # Ballot-Box is setting up
    'Opened',           # A P is selected so ...
    'Voting',           # build-up the democracy
    'Closed',           # Time to go to sleep'''
    # Fault FSM (2FSM work like a stack)
    'HWNotPresentOrNotWorking',
    'BallotBoxAbsent',
    ])

@model.observable.observable('state', States.None, 'State of the entire system from P point of view')
class Votanto(object):
    ident = None
    lastValidNameAndSurname = None
    president = None
    nVoters = 0
    isReaderInserted = None
    isCardInserted = None
    lastMsg = None
    stateKm1 = None
    voting_booth = None
    bbox = None
    closed = False

    def __init__(self):
        model.react.register_triggers(self)
        self.bbox = ballot_box.ballot_box()
        self.ident = identity.Identity(Votanto.identityChanged, self)
        public.welcome()

    def start(self):
        print 'Now state is started'
        self.state = States.Started
        self.evaluate()

    def evaluate(self):

        print 'evaluate'

        if self.state is States.None:
            print 'Do nothing while class is not initialized'
            return

        if self.isReaderInserted and self.state==States.HWNotPresentOrNotWorking:
            # Restart from saved state
            self.state = self.stateKm1

        if self.bbox.present and self.state==States.BallotBoxAbsent:
            # Restart from saved state
            self.state = self.stateKm1

        if not self.isReaderInserted and self.state!=States.HWNotPresentOrNotWorking:
            # Save current state that'll be restored
            # after things come back
            self.stateKm1 = self.state
            self.state = States.HWNotPresentOrNotWorking
            public.incomplete()
        elif self.state==States.Started and not self.isCardInserted:
            public.insertSCP()
        elif not self.bbox.present and self.state!=States.BallotBoxAbsent:
            # Save current state that'll be restored
            # after things come back
            self.stateKm1 = self.state
            self.state = States.BallotBoxAbsent
            public.incomplete()
        else:
            if self.isCardInserted:
                if self.validNameAndSurname(self.lastMsg.nameAndSurname):
                    self.gotIdentity(self.lastMsg.nameAndSurname)
                else:
                    print 'Identity ignored (%s) but card is inserted!'%self.lastMsg.nameAndSurname
            else:
                self.byeIdentity()

        #print 'evaluate new state', self.state

    def close(self):
        if self.closed:
            return

        if self.ident is not None:
            self.ident.close()
            #self.ident = None
        if self.voting_booth is not None:
            self.voting_booth.close()
            #self.voting_booth = None
        if self.bbox is not None:
            self.bbox.close()
            #self.bbox = None

        self.closed = True

    def dump(self):
        print 'state',self.state,States[self.state],'ident',self.ident,'last',self.lastValidNameAndSurname,'lastMsg',self.lastMsg,'stateKm1',self.stateKm1

    def validNameAndSurname(self, nas):
        ret = ((type(nas) == type('')) and len(nas)>0)
        return ret

    def identityChanged(self, msg):
        print 'identityChanged', msg
        if msg.isReader:
            self.isReaderInserted = msg.isInserted
        else:
            self.isCardInserted = msg.isInserted

        self.lastMsg = msg
        self.evaluate()

    def gotIdentity(self, nameAndSurname):
        print "gotIdentity(%s)"%(nameAndSurname)

        if self.president is None:
            # This is our president
            print 'President selected!'
            self.president = nameAndSurname
            if self.bbox.present:
                self.state = States.Opened
            else:
                self.state = States.BallotBoxSetup

        elif self.state == States.Voting:
            if self.president == nameAndSurname:
                # Vote president and close the session
                print 'Please vote president'
                self.voteOpen()
            else:
                # Citizen vote
                print 'Please vote '+nameAndSurname
                self.voteOpen()

        self.lastValidNameAndSurname = nameAndSurname

    def byeIdentity(self):
        print "byeIdentity(%s)"%self.state

        if self.state == States.None:
            return

        if self.state == States.Opened:
            self.state = States.Voting
        elif self.state == States.Voting:
            print 'Lei ha votato'
            self.voteClose()
            self.nVoters += 1
            print '%d votanti fino ad ora'%self.nVoters

            if self.president == self.lastValidNameAndSurname:
                print 'Seggio chiuso'
                self.state = States.Closed

    def voteOpen(self):
        assert self.voting_booth is None
        self.voting_booth = voting_booth.vote()
        self.voting_booth.open()
        #threading.Timer(self.voteOpenedForSecs, self.voteClose).start()


    def voteClose(self):
        assert self.voting_booth is not None
        self.voting_booth.close()
        self.voting_booth = None

    @model.react.to('vote.button_pressed')
    def buttonPressed():
        print 'buttonPressed!!!'

    @model.react.to('ballot_box.present')
    def ballotBoxPresenceChanged(self):
        self.evaluate()

    @model.react.to('Identity.nameAndSurname')
    def getIds():
        try:
            pass
        except:
            traceback.print_exc()

    @model.react.to('Votanto.state')
    def setupBallot(self):
        pass

if __name__ == '__main__':
    #import objgraph
    isDebugOn = False

    votanto = None
    lock = threading.Lock()

    def debug_cycles():
        gc.set_debug(gc.DEBUG_LEAK)
        gc.collect()
        print 'gc.collect() done'
        for obj in gc.garbage:
            print obj
        #objgraph.show_backrefs(gc.garbage, refcounts=True)
        print 'gc debug done'

    def stackTrace():
        if isDebugOn:
            for th in threading.enumerate():
                print(th)
                traceback.print_stack(sys._current_frames()[th.ident])
                print()

            debug_cycles()
        
    done = False
    def dbgRun():
        while not done:
            time.sleep(5)
            stackTrace()
        print 'dbgRun done!'

    t = threading.Thread(target=dbgRun)
    t.start()
    try:
        votanto = Votanto()
        time.sleep(3)
        votanto.start()
        @model.react.to('Votanto.state')
        def ballotClosed():
            if votanto.state == States.Closed:
                print 'Closing '
                votanto.close()
                lock.release()

        lock.acquire()

        # By this way we are able to Ctrl-C main thread
        while not lock.acquire(False):
            time.sleep(5)

    except:
        traceback.print_exc()
    finally:
        if votanto is not None:
            votanto.close()

        done = True
        time.sleep(1)
        stackTrace()

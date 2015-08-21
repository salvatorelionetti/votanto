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
    'Voting',           # build the democracy
    'Closed',           # Time to go to sleep'''
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
    ballot_box = None

    def __init__(self):
        self.ident = identity.Identity(Votanto.identityChanged, self)
        self.ballot_box = ballot_box.ballot_box()
        public.welcome()

    def start(self):
        self.state = 'Started'
        self.evaluate()

    def evaluate(self):

        print 'evaluate, current state', self.state

        if self.state is None:
            print 'Do nothing while class is not initialized'
            return

        if self.isReaderInserted and self.state=='HWNotPresentOrNotWorking':
            # Restart from saved state
            self.state = self.stateKm1

        if not self.isReaderInserted and self.state!='HWNotPresentOrNotWorking':
            # Save current state that'll be restored
            # after things come back
            self.stateKm1 = self.state
            self.state = 'HWNotPresentOrNotWorking'
            public.incomplete()
        elif self.state=='Started' and not self.isCardInserted:
            public.insertSCP()
        else:
            if self.isCardInserted:
                if self.validNameAndSurname(self.lastMsg.nameAndSurname):
                    self.gotIdentity(self.lastMsg.nameAndSurname)
                else:
                    print 'Identity ignored (%s) but card is inserted!'%self.lastMsg.nameAndSurname
            else:
                self.byeIdentity()

        print 'evaluate new state', self.state

    def close(self):
        if self.ident is not None:
            self.ident.close()
        if self.voting_booth is not None:
            self.voting_booth.close()
        if self.ballot_box is not None:
            self.ballot_box.close()

    def dump(self):
        print 'state',self.state,'ident',self.ident,'last',self.lastValidNameAndSurname,'lastMsg',self.lastMsg,'stateKm1',self.stateKm1

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
            if self.ballot_box.present:
                self.state = 'Opened'
            else:
                self.state = 'BallotBoxSetup'

        elif self.president == nameAndSurname:
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

        if self.state == None:
            return

        if self.state == 'Opened':
            self.state = 'Voting'
        else:
            print 'Lei ha votato'
            self.voteClose()
            self.nVoters += 1
            print '%d votanti fino ad ora'%self.nVoters

            if self.president == self.lastValidNameAndSurname:
                print 'Seggio chiuso'
                self.state = 'Closed'

    def voteOpen(self):
        assert self.voting_booth is None
        self.voting_booth = voting_booth.vote()
        self.voting_booth.open()
        #threading.Timer(self.voteOpenedForSecs, self.voteClose).start()


    def voteClose(self):
        assert self.voting_booth is not None
        self.voting_booth.close()
        self.voting_booth = None

    @model.react.to('voting_booth.button_pressed')
    def buttonPressed():
        print 'buttonPressed!!!'

    @model.react.to('ballot_box.present')
    def ballotBoxPresenceChanged():
        print 'present!!!'

    @model.react.to('Identity.nameAndSurname')
    def getIds():
        try:
            print Identity.nameAndSu
        except:
            traceback.print_exc()

    @model.react.to('Votanto.state')
    def setupBallot(self):
        print 'setupBallot', self
        self.dump() 

if __name__ == '__main__':
    votanto = None
    try:
        votanto = Votanto()
        time.sleep(3)
        votanto.start()
        time.sleep(10)
    except:
        traceback.print_exc()
    finally:
        if votanto is not None:
            votanto.close()

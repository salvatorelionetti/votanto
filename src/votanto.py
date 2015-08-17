import time
import threading
import traceback

import identity
import public
import model.react
import voting_booth

def validNameAndSurname(nas):
    ret = ((type(nas) == type('')) and len(nas)>0)
    return ret

class Votanto:
    state = None # Started, Opened, Voting, Closed, HWNotPresentOrNotWorking
    ident = None
    lastValidNameAndSurname = None
    president = None
    nVoters = 0
    isReaderInserted = None
    isCardInserted = None
    lastMsg = None
    stateKm1 = None
    voting_booth = None

    def __init__(self):
        self.ident = identity.Identity(Votanto.identityChanged, self)
        public.welcome()

    def start(self):
        Votanto.state = 'Started'
        self.evaluate()

    def evaluate(self):

        print 'evaluate, current state', Votanto.state

        if Votanto.state is None:
            print 'Do nothing while class is not initialized'
            return

        if Votanto.isReaderInserted and Votanto.state=='HWNotPresentOrNotWorking':
            # Restart from saved state
            Votanto.state = Votanto.stateKm1

        if not Votanto.isReaderInserted and Votanto.state!='HWNotPresentOrNotWorking':
            # Save current state that'll be restored
            # after things come back
            Votanto.stateKm1 = Votanto.state
            Votanto.state = 'HWNotPresentOrNotWorking'
            public.incomplete()
        elif Votanto.state=='Started' and not Votanto.isCardInserted:
            public.insertSCP()
        else:
            if Votanto.isCardInserted:
                if validNameAndSurname(Votanto.lastMsg.nameAndSurname):
                    self.gotIdentity(Votanto.lastMsg.nameAndSurname)
                else:
                    print 'Identity ignored (%s) but card is inserted!'%Votanto.lastMsg.nameAndSurname
            else:
                self.byeIdentity()

        print 'evaluate new state', Votanto.state

    def close(self):
        if self.ident is not None:
            self.ident.close()
        if self.voting_booth is not None:
            self.voting_booth.close()

    def dump(self):
        print 'state',Votanto.state,'ident',self.ident,'last',Votanto.lastValidNameAndSurname,'lastMsg',Votanto.lastMsg,'stateKm1',Votanto.stateKm1

    def identityChanged(self, msg):
        print 'identityChanged',type(self), self, type(msg), msg
        if msg.isReader:
            Votanto.isReaderInserted = msg.isInserted
        else:
            Votanto.isCardInserted = msg.isInserted

        Votanto.lastMsg = msg
        self.evaluate()

    def gotIdentity(self, nameAndSurname):
        print "gotIdentity(%s)"%(nameAndSurname)

        if Votanto.president is None:
            # This is our president
            print 'President selected!'
            Votanto.president = nameAndSurname
            Votanto.state = 'Opened'
        elif Votanto.president == nameAndSurname:
            # Vote president and close the session
            print 'Please vote president'
            self.voteOpen()
        else:
            # Citizen vote
            print 'Please vote '+nameAndSurname
            self.voteOpen()

        Votanto.lastValidNameAndSurname = nameAndSurname

    def byeIdentity(self):
        print "byeIdentity(%s)"%Votanto.state

        if Votanto.state == None:
            return

        if Votanto.state == 'Opened':
            Votanto.state = 'Voting'
        else:
            print 'Lei ha votato'
            self.voteClose()
            Votanto.nVoters += 1
            print '%d votanti fino ad ora'%Votanto.nVoters

            if Votanto.president == Votanto.lastValidNameAndSurname:
                print 'Seggio chiuso'
                Votanto.state = 'Closed'

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
        
votanto = None
try:
    votanto = Votanto()
    time.sleep(3)
    votanto.start()
    time.sleep(30)
except:
    traceback.print_exc()
finally:
    if votanto is not None:
        votanto.close()

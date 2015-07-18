import sys
import subprocess
import re
import time
import traceback
import smartcard
import smartcard.ReaderMonitoring
import smartcard.CardMonitoring
import smartcard.util

class IdentityEvent:
	def __init__(self, isReader, isInserted):
		self.isReader = isReader
		self.isInserted = isInserted

	def __str__(self):
		return 'IdentityEvent<'+["card", "reader"][self.isReader]+' is '+['absent','inserted'][self.isInserted]+'>'

class readerobserver( smartcard.ReaderMonitoring.ReaderObserver ):

    readerInserted = False

    def __init__( self, onChange, onChangeContext=None ):
	smartcard.ReaderMonitoring.ReaderObserver.__init__(self)
	self.onChange = onChange
	self.onChangeContext = onChangeContext

    def update( self, observable, (addedreaders, removedreaders) ):
        try:
            self._update(observable, (addedreaders, removedreaders) )
        except:
            traceback.print_exc()

    def _update( self, observable, (addedreaders, removedreaders) ):
	#print type(observable), observable, dir(observable)
        print "Added readers", addedreaders
        print "Removed readers", removedreaders
	changed=0
        for reader in addedreaders:
            changed+=1
            print "+Reader: ", reader
            readerInserted = True
        for reader in removedreaders:
            changed+=1
            print "-Reader: ", reader
            readerInserted = False

	if changed>0 and self.onChange is not None:
		msg = IdentityEvent(True, readerInserted)
		f = self.onChange
		#f(self.onChangeContext)
		f(msg)

class cardobserver( smartcard.CardMonitoring.CardObserver ):

    cardInserted = False

    def __init__( self, onChange, onChangeContext=None ):
	smartcard.CardMonitoring.CardObserver.__init__(self)
	self.onChange = onChange
	self.onChangeContext = onChangeContext

    def update( self, observable, (addedreaders, removedreaders) ):
        try:
            self._update(observable, (addedreaders, removedreaders) )
        except:
            traceback.print_exc()

# Initial event if no reader is inserted
#CardMonitor
#Added cards []
#Removed cards []

    def _update( self, observable, (addedcards, removedcards) ):
	#print type(observable), observable, dir(observable)
        print "Added cards", addedcards
        print "Removed cards", removedcards
	changed=0
        for card in addedcards:
            changed+=1
            print "+Inserted: ", smartcard.util.toHexString( card.atr )
            cardInserted = True
        for card in removedcards:
            changed+=1
            print "-Removed: ", smartcard.util.toHexString( card.atr )
            cardInserted = False

	if changed>0 and self.onChange is not None:
		msg = IdentityEvent(False, cardInserted)
		f = self.onChange
		#f(self.onChangeContext)
		f(msg)

class Identity:
	nameAndSurname = None

	class Reader:
		class Card:
			pass
		pass

	def __init__(self, onChange, onChangeContext=None):

		self.onChange = onChange
		self.onChangeContext = onChangeContext

		self.readermonitor = smartcard.ReaderMonitoring.ReaderMonitor()
		self.cardmonitor   = smartcard.CardMonitoring.CardMonitor()

		self.readerobserver = readerobserver(self.topographyChanged)
		self.cardobserver = cardobserver(self.topographyChanged)

		self.readermonitor.addObserver( self.readerobserver )
		self.cardmonitor.addObserver( self.cardobserver )

		print 'Init done'

	def close(self):
		self.readermonitor.deleteObserver(self.readerobserver)
		self.cardmonitor.deleteObserver(self.cardobserver)
		print 'close done'

	def topographyChanged(self, msg):
		print msg

		if not msg.isReader and msg.isInserted:
			self.cardInserted()
			msg.nameAndSurname = self.nameAndSurname
		else:
			self.nameAndSurname = None

		if self.onChange is not None:
			self.onChange(self.onChangeContext, msg)

	def cardInserted(self):
		#print type(self), self, dir(self)
		nameAndSurname = None
		cmd = subprocess.Popen("pkcs15-tool -D", shell=True, stdout=subprocess.PIPE)
		out, err = cmd.communicate()
		if err is not None:
			print 'No identity found, cmd return error(%s)', err
		else:
			m = re.search("PKCS#15 Card .(.*).:", out)
			#print m
			if m is not None:
				#print m.groups()
				if len(m.groups())==1:
					nameAndSurname=m.group(1)
				else:
					print "Too many nameAndSurname found!"
			elif out is not None:
				print "No identity found: output format unexpected(%s)%d"%( out, len(out))
		#print "out(%s)"%out
		print "err(%s)"%err
		#for line in cmd:
		#	print "(((%s)))"%cmd
		#if nameAndSurname != self.nameAndSurname:
		#	print '%s->%s'%(self.nameAndSurname,nameAndSurname)
		self.nameAndSurname = nameAndSurname
			
    
identity = None

def onChange():
	print "onChange"

if __name__ == '__main__':
	try:
	    print "Insert or remove a smartcard in the system."
	    print "This program will exit in 10 seconds"
	    print ""

	    identity = Identity(onChange)
	    time.sleep(10)

	    #print 'press Enter to continue'
	    #sys.stdin.readline()

	except:
	    traceback.print_exc()
	    #print sys.exc_info()[0], ': ', sys.exc_info()[1]
	finally:
	    if identity is not None:
		print "Closing identity submodule"
		identity.close()

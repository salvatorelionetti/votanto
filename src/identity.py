import sys
import subprocess
import re
import time
import traceback
import smartcard
import smartcard.ReaderMonitoring
import smartcard.CardMonitoring
import smartcard.util

import model.observable
import model.react

class IdentityEvent:
	def __init__(self, isReader, isInserted):
		self.isReader = isReader
		self.isInserted = isInserted

	def __str__(self):
		return 'IdentityEvent<'+["card", "reader"][self.isReader]+' is '+['absent','inserted'][self.isInserted]+'>'

class readerobserver( smartcard.ReaderMonitoring.ReaderObserver ):

    isReaderInserted = False

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
            isReaderInserted = True
        for reader in removedreaders:
            changed+=1
            print "-Reader: ", reader
            isReaderInserted = False

	if changed>0 and self.onChange is not None:
		msg = IdentityEvent(True, isReaderInserted)
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

@model.observable.observable('nameAndSurname', None, 'Name and Surname from SC')
class Identity(object):
	def __init__(self, onChange, onChangeContext=None):
		print 'Identity.__init__', self

		self.onChange = onChange
		self.onChangeContext = onChangeContext

		self.readermonitor = smartcard.ReaderMonitoring.ReaderMonitor()
		self.cardmonitor   = smartcard.CardMonitoring.CardMonitor()

		self.readerobserver = readerobserver(self.topographyChanged)
		self.cardobserver = cardobserver(self.topographyChanged)

		self.readermonitor.addObserver( self.readerobserver )
		self.cardmonitor.addObserver( self.cardobserver )

	def close(self):
		print 'Identity.close'
		self.readermonitor.deleteObserver(self.readerobserver)
		self.cardmonitor.deleteObserver(self.cardobserver)

	def topographyChanged(self, msg):
		print msg

		if not msg.isReader and msg.isInserted:
			self.annotateNameAndSurname()
			msg.nameAndSurname = self.nameAndSurname
		else:
			self.nameAndSurname = None

		if self.onChange is not None:
		    if self.onChangeContext is not None:
			self.onChange(self.onChangeContext, msg)
                    else:
			self.onChange(msg)

	def annotateNameAndSurname(self):
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
                                        print "nameAndSurname(%s)"%nameAndSurname
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

if __name__ == '__main__':
	try:
	    print "Insert or remove a smartcard in the system."
	    print "This program will exit in 10 seconds"
	    print ""

            class Test(object):
                def __init__(self):
                    pass
                def onChange(self, msg):
                        print "onChange", msg
                        print type(self), self
                        print type(msg), msg

                @model.react.to('Identity.nameAndSurname')
                def nsChanged():
                    print "NSCHANGED!"

            test = Test()
	    identity = Identity(test.onChange)
	    time.sleep(10)

	except:
	    traceback.print_exc()
	finally:
	    if identity is not None:
		identity.close()

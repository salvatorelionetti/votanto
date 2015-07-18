import time
import traceback

import identity
import public

def validNameAndSurname(nas):
	ret = ((type(nas) == type('')) and len(nas)>0)
	return ret

class Votanto:
	state = None # Opened, Voting, Closed
	ident = None
	lastValidNameAndSurname = None
	president = None
	nVoters = 0

	def __init__(self):
		self.ident = identity.Identity(Votanto.identityChanged, self)
		public.welcome()

	def close(self):
		if self.ident is not None:
			self.ident.close()

	def selfCheck(self):
		if not self.readerInserted():
			print 'Oh no, non posso funzionare senza un pezzo'

	def cardInserted(self):
		ret = identity.Identity.cardInserted()
		return ret

	def readerInserted(self):
		ret = identity.Identity.readerInserted()
		return ret

	def dump(self):
		print 'state',self.state,'ident',self.ident,'last',self.lastValidNameAndSurname

	def identityChanged(self, msg):
		print type(self), self, type(msg), msg
		if msg.isReader:
			return

		if msg.isInserted:
			if validNameAndSurname(msg.nameAndSurname):
				self.gotIdentity(msg.nameAndSurname)
			else:
				print 'Identity ignored (%s) but card is inserted!'%msg.nameAndSurname
		else:
			self.byeIdentity()

	def gotIdentity(self, nameAndSurname):
		print "gotIdentity(%s,%s)"%(Votanto.state,nameAndSurname)

		if Votanto.president is None:
			# This is our president
			print 'President selected!'
			Votanto.president = nameAndSurname
			Votanto.state = 'Opened'
		elif Votanto.president == nameAndSurname:
			# Vote president and close the session
			print 'Please vote president'
		else:
			# Citizen vote
			print 'Please vote '+nameAndSurname

		Votanto.lastValidNameAndSurname = nameAndSurname

	def byeIdentity(self):
		print "byeIdentity(%s)"%Votanto.state

		if Votanto.state == None:
			return

		if Votanto.state == 'Opened':
			Votanto.state = 'Voting'
		else:
			print 'Lei ha votato'
			Votanto.nVoters += 1
			print '%d votanti fino ad ora'%Votanto.nVoters

			if Votanto.president == Votanto.lastValidNameAndSurname:
				print 'Seggio chiuso'
				Votanto.state = 'Closed'

votanto = None
try:
	votanto = Votanto()
	time.sleep(30)
except:
	traceback.print_exc()
finally:
	if votanto is not None:
		votanto.close()

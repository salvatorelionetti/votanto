import subprocess

def say(msg):
	#subprocess.call('echo '+msg+'|festival --tts', shell=True)
	echo "say(%s)"%msg

def welcome():
	say('Ciao')
	say('Sono votanto un sistema elettronico di assistenza al voto')
	say('Presidente cortesemente inserisca il pin della sua carta senza essere osservato')

def welcomeP(president):
	say('Buongiorno %s, lei e' il presidente di questa votazione'%president)

def welcomeV(voter):
	say('Benvenuto %s, prego si rechi in cabina per votare, grazie'%voter)

def doneV():
	say('Lei ha votato')

def status(nVoters):
	say('Numero votanti %d'%nVoters)

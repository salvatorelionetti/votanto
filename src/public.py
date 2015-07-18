import subprocess

def say(msg):
	subprocess.call('echo '+msg+'|festival --tts', shell=True)

def welcome():
	say('Eccomi')
	say('Sono votanto un sistema elettronico di assistenza al voto')


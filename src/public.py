import subprocess

def say(msg):
    #subprocess.call('echo '+msg+'|festival --tts --language italian', shell=True)
    print "say(%s)"%msg

def welcome():
    say('Ciao')
    say('Sono votanto un sistema elettronico di assistenza al voto')

def insertSCP():
    say('Presidente cortesemente inserisca la sua tessera elettronica')

def insertPINP():
    say('Presidente cortesemente inserisca il pin senza essere osservato')

def welcomeP(president):
    say('Buongiorno %s, lei e il presidente di questa votazione'%president)

def welcomeV(voter):
    say('Benvenuto %s, prego si rechi in cabina per votare, grazie'%voter)

def doneV():
    say('Lei ha votato')

def status(nVoters):
    say('Numero votanti %d'%nVoters)

def noreader():
    say('Sistema non completo')
    say('Presidente, colleghi cortesemente il lettore di smartcard')

def sayPairingFrom(btAddr, btName, passKey):
    say('Richiesta di accoppiamento via bluetooth')
    say('device %s'%btName)
    say('indirizzo %s'%btAddr)
    say('chiave %s'%passKey)

def incomplete():
    say('Il sistema e fermo, in attesa che tutti i suoi componenti siano collegati e funzionanti')

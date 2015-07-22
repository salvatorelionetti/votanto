import singleton
import obsub

@singleton.singleinstance
class Auditors(object):
    def __init__(self):
        print 'Auditor.__init__'
        self.L = []

    @obsub.event
    def add(self, auditorAddress):
        print 'Auditors:add',auditorAddress
        if auditorAddress not in self.L:
            self.L.append(auditorAddress)
        print 'auditors L', self.L

if __name__ == '__main__':
    a = Auditors()
    print a
    a.add('00:11:22:33:44:55')
    b = Auditors()
    print a,b

chain = {}

def notify(event_path):
    print 'react.notify', event_path
    if event_path in chain:
        for f in chain[event_path]:
            f()

class to(object):
    def __init__(self, event_path):
        print 'react.__init__', event_path
        self.event_path = event_path

    def __call__(self, obj):
        # Inject post set   
        print 'react.__call__', obj
        #print type(self.event_path), self.event_path
        #print type(obj), obj
        if self.event_path in chain:
            chain[self.event_path].append(obj)
        else:
            chain[self.event_path] = [obj]

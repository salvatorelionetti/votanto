import traceback

import react

def object_eq(a, b):
    return type(a)==type(b) and a==b

def assert_eq(a, b):
    assert object_eq(a,b)

class observable(object):
    def __init__(self, var_name, var_value, description):
        print 'observable.__init__', self, var_name, var_value, description
        self.var_name = var_name
        self.var_value = var_value
        self.var_description = description
        self.__doc__ = description

    def __get__(self, obj, cls):
        try:
            #print self, type(obj), obj, cls
            assert type(obj).__name__ == self.cls_name
            #print 'observable.__get__', self.event_path, self.var_value
            return self.var_value
        except:
            traceback.print_exc()
            raise

    def __set__(self, obj, val):
        try:
            #print self, type(obj), obj, type(val)
            s = 'observable.__set__'
            assert type(obj).__name__ == self.cls_name
            valKm1 = self.var_value
            if not object_eq(valKm1, val):
                print s, self.event_path, valKm1,'->',val
                self.var_value = val
                react.notify(self.event_path)
            else:
                print s, self.event_path, 'IGNORING', valKm1,'->', val
        except:
            traceback.print_exc()
            raise

    def __delete__(self, obj):
        try:
            print 'observable.__delete__', self, obj
            del self.var_name
            del self.var_value
            del self.var_descriptor
            if hasattr(self, 'cls_name'):
                del self.cls_name
                del self.event_path
        except:
            traceback.print_exc()
            raise

    def __call__(self, cls):
        print 'observable.__call__', self, cls
        # If cls is a 'classobj', setattr()'ll fail silently,
        # (get/set not called)
        s = "%s is of type %s: required <type 'type'>"
        assert isinstance(cls, type), s%(cls,type(cls))
        self.event_path = cls.__name__ + '.' + self.var_name
        self.cls_name = cls.__name__
        setattr(cls, self.var_name, self)
        return cls

if __name__ == '__main__':
    @observable('aX', None, 'Sampling delta')
    @observable('aY', 20, 'Sampling 2elta')
    @observable('aZ', 30, 'Used for function<->self bounding')
    class cA(object):
        def __init__(self):
            print 'cA.__init__', self
            react.register_triggers(self)

        def check1(self):
            print "cA.check1"
            print 'self.aY'
            a = self.aY
            #print 'self.aY', type(a), a
            self.aY = 111
            print 'self.aX'
            a = self.aX
            #print 'self.aX', type(a), a
            self.aX = 222

        def check2(self):
            print "cA.check2"
            print 'cA.aY'
            a = cA.aY
            #print 'cA.aY', type(a), a
            cA.aY = 1111
            print 'cA.aX'
            a = cA.aX
            #print 'cA.aX', type(a), a
            cA.aX = 2222

        def checkDoc(self):
            print 'cA.checkDoc()'
            print getattr(self, 'aX')
            print self.aX.__doc__
            print cA.aY.__doc__

        @react.to('cA.aZ')
        def aXChanged(self):
            print 'aXChanged', self

        def checkBound(self):
            self.aZ = 12321
            
    @react.to('cA.aX')
    def reactionA():
        print 'reactionA to aX!!!'

    @react.to('cA.aY')
    def reactionB():
        print 'reactionB to aY!!!'

    @react.to('cA.aX')
    def reactionC():
        print 'reactionC to aX!!!'

    ca = cA()
    #ca.checkDoc()
    ca.check1()
    #ca.check2()
    #ca.check1()
    ca.checkBound()

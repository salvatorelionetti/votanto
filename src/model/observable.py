import traceback

import react

# TODO add event coalescing like LowPass 
def object_eq(a, b):
    return type(a)==type(b) and a==b

def assert_eq(a, b):
    assert object_eq(a,b)

def class_path(object):
    print 'class_path', type(object)

class observable(object):
    def __init__(self, variable_name, initial_value, description):
        print 'observable.__init__', self, variable_name, initial_value, description
        self.variable_name = variable_name
        self.variable_value = initial_value
        self.variable_description = description
        self.__doc__ = description

    def get_attr_list(self):
        return [self.variable_name, self.variable_value, self.variable_description]

    def __get__(self, obj, cls):
        try:
            #print self, type(obj), obj, cls
            print 'observable.__get__', type(cls).__name__+"."+self.variable_name, self.variable_value
            return self.variable_value
        except:
            traceback.print_exc()
            raise

    def __set__(self, obj, val):
        try:
            #print self, type(obj), obj, type(val)
            valKm1 = self.variable_value
            if not object_eq(valKm1, val):
                print 'observable.__set__', type(obj).__name__+"."+self.variable_name, valKm1,'->',val
                self.variable_value = val
                react.notify(type(obj).__name__ + "." + self.variable_name)
            else:
                print 'observable.__set__', type(obj).__name__+"."+self.variable_name, 'IGNORING', valKm1,'->',val
        except:
            traceback.print_exc()
            raise

    def __call__(self, cls):
        print 'observable.__call__', type(cls), cls, self
        # If cls is a 'classobj', setattr()'ll fail silently (get/set not called)
        assert isinstance(cls, type), "%s is of type %s: required <type 'type'>"%(cls,type(cls))
        self.cls = cls
        setattr(cls, self.variable_name, self)
        var_name = self.variable_name

        if not hasattr(cls, '__original_init__'):
            cls.__original_init__ = cls.__init__

            def __inject_method_bound__(self, *p, **k):
                    print 'inject method bounds', self
                    for attr_name in dir(type(self)):
                        s = "('%s' in %s.__dict__) and isinstance(%s.__dict__['%s'], observable)"%(attr_name, type(self).__name__, type(self).__name__, attr_name)
                        #print 'evaluating', attr_name, s
                        #print eval(s)
                        if eval(s):
                            event_path = observable.event_path_from(type(self),attr_name) 
                            react.add_observable(self, event_path)
                    type(self).__original_init__(self, *p, **k)

            cls.__init__ = __inject_method_bound__

        return cls

    def event_path(self):
        return event_path_from(type(self), self.variable_name)

    @staticmethod
    def event_path_from(cls, var_name):
        return cls.__name__ + "." + var_name

import inspect
if __name__ == '__main__':
    @observable('aX', None, 'Sampling delta')
    @observable('aY', 20, 'Sampling 2elta')
    @observable('aZ', 30, 'Used for function<->self bounding')
    class cA(object):
        def __init__(self):
            print 'cA.__init__', self

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
            #print inspect.getmro(type(self))

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
            #print inspect.getmro(type(self))

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
            
    #@react.to('cA.aX')
    #def reactionA():
    #    print 'reactionA to aX!!!'

    #@react.to('cA.aY')
    #def reactionB():
    #    print 'reactionB to aY!!!'

    #@react.to('cA.aX')
    #def reactionC():
    #    print 'reactionC to aX!!!'

    ca = cA()
    #ca.checkDoc()
    #ca.check1()
    #ca.check2()
    #ca.check1()
    ca.checkBound()

    class A:
        pass
    class B(A, object):
        pass

    class C:
        pass

    class D(B,C):
        pass

    #print inspect.getmro(cA)
    #print inspect.getmro(D)
    #print ca.__class__
    #print cA.__name__

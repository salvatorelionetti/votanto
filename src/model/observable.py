import react

def object_eq(a, b):
    return type(a)==type(b) and a==b

def assert_eq(a, b):
    assert object_eq(a,b)

def class_path(object):
    print 'class_path', type(object)

class observable(object):
    def __init__(self, variable_name, initial_value, description):
        #print 'observable.__init__'
        #print variable_name, initial_value, description
        self.variable_name = variable_name
        self.variable_value = initial_value
        self.variable_description = description
        self.__doc__ = description

    def get_attr_list(self):
        return [self.variable_name, self.variable_value, self.variable_description]

    def __get__(self, obj, objtype):
        print 'observable.__get__', self.variable_name, type(self.variable_value), self.variable_value
        return self.variable_value

    def __set__(self, obj, val):
        valKm1 = self.variable_value
        if not object_eq(valKm1, val):
            print 'observable.__set__', self.variable_name, type(val), valKm1, '->', val
            self.variable_value = val
            react.notify(type(obj).__name__ + "." + self.variable_name)
        else:
            print 'observable.__set__','IGNORING', valKm1,'->',val

    def __call__(self, cls):
        setattr(cls, self.variable_name, self)
        return cls

import inspect
if __name__ == '__main__':
    @observable('aX', 10, 'Sampling delta')
    @observable('aY', 20, 'Sampling 2elta')
    class cA(object):
        def __init__(self):
            print 'cA.__init__'

        def check1(self):
            print "cA.check1"
            a = self.aY
            print 'self.aY', type(a), a
            self.aY = 111
            a = self.aX
            print 'self.aX', type(a), a
            self.aX = 222
            #print inspect.getmro(type(self))

        def check2(self):
            print "cA.check2"
            a = cA.aY
            print 'cA.aY', type(a), a
            self.aY = 1111
            a = cA.aX
            print 'cA.aX', type(a), a
            self.aX = 2222
            #print inspect.getmro(type(self))

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
    ca.check1()
    ca.check2()

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

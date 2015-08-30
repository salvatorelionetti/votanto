# Assumption
#  class methods, once parsed, are no more modified by the interpreter
# TODO add event coalescing like LowPass

chain = {}

objs = {}

class_of = {}

def func_analyze(f):
    nargs = f.func_code.co_argcount
    only_self_arg = nargs==1 and f.func_code.co_varnames[0] == 'self'

    return (nargs, only_self_arg)

def notify(event_path):
    #print 'react.notify', event_path
    #print chain
    if event_path in chain:
        for f in chain[event_path]:
            nargs, only_self_arg = func_analyze(f)
            #print f
            if nargs == 0:
                f()
            elif only_self_arg:
                assert f in class_of, 'Method registered but not resolved to a class. Forgot to call register_triggers()?'
                cls_name = class_of[f]
                for obj in objs[cls_name]:
                    bounded_f = getattr(obj, f.func_name)
                    #print bounded_f
                    bounded_f()
            else:
                assert False

def register_triggers(obj):
    print 'register_triggers', obj
    cls_name = obj.__class__.__name__

    for event_path in chain:
        for f in chain[event_path]:
            nargs, only_self_arg = func_analyze(f)
            if nargs==1 and only_self_arg and hasattr(obj, f.func_name):
                bounded_f = getattr(obj, f.func_name)
                if bounded_f.im_func is f:
                    #print 'FOUND: %s -> %s.%s'%(event_path,obj.__class__.__name__,f.func_name)
                    if cls_name in objs:
                        objs[cls_name].append(obj)
                    else:
                        objs[cls_name] = [obj]

                    if f in class_of:
                        assert cls_name==class_of[f]
                    else:
                        class_of[f] = cls_name
                    #print objs
                    #print class_of

def unregister_triggers(obj):
    print 'unregister_triggers', obj
    cls_name = obj.__class__.__name__

    if cls_name in objs:
        assert obj in objs[cls_name], 'Unregistering an unregistered object %s'%obj
        objs[cls_name].remove(obj)

def to(event_path):
    def add(dotpath, f, chain):
        if dotpath in chain:
            chain[dotpath].append(f)
        else:
            chain[dotpath] = [f]

    def decorator(f):
        print '__react__.to', event_path, f
        nargs, only_self_arg = func_analyze(f)

        if nargs == 0:
            # Unbound method
            #print 'Unbound method'
            add(event_path, f, chain)
        elif only_self_arg:
            # Not yet bounded (Python is still decoding classes)
            # Take note for later
            #print 'Bounded method to self'
            add(event_path, f, chain)
        else:
            assert False, 'Function %s has unknown parameter to trigger'%f.func_name

        return f

    return decorator

if __name__ == '__main__':
    class Test:
        def __init__(self):
            print 'Test.__init__()', self
            register_triggers(self)

        @to('Test.aX')
        def reactionA(self):
            print 'Test.reactionA()', self

        @staticmethod
        @to('Test.aY')
        def reactionB():
            print 'Test.reactionB()'


    def reactionC():
        print 'reactionC'

    #to('Test.aY').triggering(reactionC)
    t = Test()
    t1 = Test()
    t2 = Test()
    notify('Test.aX')
    notify('Test.aY')
    assert chain['Test.aY'][0] is Test.reactionB
    #assert chain['Test.aY'][1] is reactionC
    unregister_triggers(t)
    unregister_triggers(t1)
    unregister_triggers(t2)

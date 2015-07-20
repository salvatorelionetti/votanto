"""
Annotation that could convert a class to a monostate.
Borg is the name given by David Ascher to following implementation:

class Borg:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
    # and whatever else you want in your class -- that's all!

This annotation is based on such a Monostate.
After implemented i verify that Max Egger imagine the same 'shortcut'
1 years ago.
Actual solution follow the 'new' operator solution provided by Oren Tirosh
"""

def objectsKm1(class_):
        class_.__shared_state = {}
        class_.__original_init__ = class_.__init__

        def __init_borg__(self, *p, **k):
                self.__dict__ = self.__shared_state
                class_.__original_init__(self,*p,**k)

        class_.__init__ = __init_borg__

        return class_

def objects(class_):
    def __new_once__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
	
    class_.__new__ = __new_once__
    return class_

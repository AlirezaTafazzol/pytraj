# distutils: language = c++
from cython.operator cimport dereference as deref


cdef class Action_DSSP (Action):
    def __cinit__(self):
        self.baseptr = <_Action*> new _Action_DSSP()
        self.thisptr = <_Action_DSSP*> self.baseptr

    def __dealloc__(self):
        if self.baseptr is not NULL:
            del self.baseptr

    def alloc(self):
        """return a function-pointer object to be used with ActionList class
        """
        cdef FunctPtr func = FunctPtr()
        func.ptr = &(self.thisptr.Alloc)
        return func
        
    def help(self):
        self.thisptr.Help()

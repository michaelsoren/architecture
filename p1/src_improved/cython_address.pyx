# Michael LeMay, 1/19/19

#NOTE: This file is written in cython for performance reasons.
#      Most of these functions are straightforward math, which
#      made converting to C wrapped in python a natural and relatively
#      easy choice. The old address.py file is still in the project, if you want
#      a general look at the origins prior to my attempt to increase performance.
#      This change had a marked effect on performance, essentially doubling
#      performance in most cases.

from libc.math cimport log2
from libc.math cimport ceil

cdef class Cython_address:

    cdef public int addr
    cdef readonly int addrBits
    cdef readonly int numSets
    cdef readonly int numBlocks

    cdef readonly int numBlockOffsetBits
    cdef readonly int numSetBits
    cdef readonly int numTagBits


    cpdef int getTag(self, int addr):
        """Returns the tag bits with bitmasking"""
        cdef int mask = (1 << self.numTagBits) - 1
        mask = mask << (self.numSetBits + self.numBlockOffsetBits)
        return (addr & mask) >> (self.numSetBits + self.numBlockOffsetBits)

    cpdef int getIndex(self, int addr):
        """Returns the index bits with bitmasking"""
        cdef int mask = (1 << self.numSetBits) - 1
        mask = mask << self.numBlockOffsetBits
        return (addr & mask) >> self.numBlockOffsetBits


    cpdef int getOffset(self, int addr):
        """Returns the offset bits with bitmasking"""
        cdef int mask = (1 << self.numBlockOffsetBits) - 1
        return addr & mask

    cdef int countBits(self, int n):
        """Counts the number of bits used."""
        cdef int count = 0
        while n:
            count += 1
            n = n >> 1
        return count

    cdef int calcNumBlockOffsetBits(self):
        """Calculate and return the number of offset bits"""
        return self.countBits(self.numBlocks) - 1


    cdef int calcNumSetBits(self):
        """Calculate and return the number of set bits"""
        return self.countBits(self.numSets) - 1

    cdef int calcNumTagBits(self):
        """Calculate and return the number of tag bits"""
        return self.addrBits - self.numBlockOffsetBits - self.numSetBits

    def __cinit__(self, addrBits, numSets, numBlocks):
        """Initiates an address and all of its parameters. Parameters
        are needed in order to know the size of each field of the address.
        """
        self.addrBits = addrBits
        self.numSets = numSets
        self.numBlocks = numBlocks

        self.numBlockOffsetBits = self.calcNumBlockOffsetBits()
        self.numSetBits = self.calcNumSetBits()
        self.numTagBits = self.calcNumTagBits()

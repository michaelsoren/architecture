# Michael LeMay, 1/19/19

import numpy as np
import math

class Address:


    def __init__(self, newAddr, addrBits, numSets, numBlocks):
        """Initiates an address and all of its parameters. Parameters
        are needed in order to know the size of each field of the address.
        """
        self.addr = newAddr
        self.addrBits = addrBits;
        self.numSets = numSets;
        self.numBlocks = numBlocks;

        self.numBlockOffsetBits = self.calcNumBlockOffsetBits()
        self.numSetBits = self.calcNumSetBits()
        self.numTagBits = self.calcNumTagBits()


    def getTag(self):
        """Returns the tag bits with bitmasking"""
        mask = (1 << self.numTagBits) - 1
        mask = mask << (self.numSetBits + self.numBlockOffsetBits)
        return (self.addr & mask) >> (self.numSetBits + self.numBlockOffsetBits)


    def getIndex(self):
        """Returns the index bits with bitmasking"""
        mask = (1 << self.numSetBits) - 1
        mask = mask << self.numBlockOffsetBits
        return (self.addr & mask) >> self.numBlockOffsetBits


    def getOffset(self):
        """Returns the offset bits with bitmasking"""
        mask = (1 << self.numBlockOffsetBits) - 1
        return self.addr & mask


    def calcNumBlockOffsetBits(self):
        """Calculate and return the number of offset bits"""
        return int(math.ceil(math.log(float(self.numBlocks), 2)))


    def calcNumSetBits(self):
        """Calculate and return the number of set bits"""
        return int(math.ceil(math.log(float(self.numSets), 2)))


    def calcNumTagBits(self):
        """Calculate and return the number of tag bits"""
        return self.addrBits - self.numBlockOffsetBits - self.numSetBits

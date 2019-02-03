# Michael LeMay, 1/19/19

import cache


class Cpu:


    def __init__(self, numSets, numBlocksPerSet,
                 replacementPolicy, writePolicy, blockSize, ramSize, addrObj):
        """Creates the cpu and its parameters. Creates the cache.
        Cpu also counts the number of instructions it receives.
        """
        self.numSets = numSets
        self.numBlocksPerSet = numBlocksPerSet
        self.ramSize = ramSize
        self.replacementPolicy = replacementPolicy
        self.writePolicy = writePolicy
        self.blockSize = blockSize
        self.counterOn = False

        self.cache = cache.Cache(numSets, numBlocksPerSet,
                                 replacementPolicy, writePolicy,
                                 blockSize, ramSize, addrObj)

        self.instructionCount = 0


    def turnOnCounter(self):
        """Turns on the counter here and in the cache"""
        self.counterOn = True
        self.cache.counterOn = True

    def turnOffCounter(self):
        """Turns off the counter here and in the cache"""
        self.counterOn = False
        self.cache.counterOn = False

    def loadDouble(self, addr):
        """Increments instruction count and tells cache to return a value at
        an address.
        """
        if self.counterOn:
            self.instructionCount += 1
        return self.cache.getDouble(addr)


    def storeDouble(self, addr, value):
        """Increments instruction count and tells cache to set an address
        to a given value.
        """
        if self.counterOn:
            self.instructionCount += 1
        self.cache.setDouble(addr, value)


    def addDouble(self, v1, v2):
        """Adds two doubles together and increments instruction count"""
        if self.counterOn:
            self.instructionCount += 1
        return v1 + v2


    def multDouble(self, v1, v2):
        """Multiplies two doubles and increments instruction count"""
        if self.counterOn:
            self.instructionCount += 1
        return v1 * v2


    def cpuStats(self):
        """Gets stats from cache and prints out the hits, misses, miss rate, and
        instruction count.
        """
        ret = {}
        ret["instructionCount"] = self.instructionCount
        cacheStats = self.cache.countingInfo
        ret["readHits"] = cacheStats["readHits"]
        ret["readMisses"] = cacheStats["readMisses"]
        ret["writeHits"] = cacheStats["writeHits"]
        ret["writeMisses"] = cacheStats["writeMisses"]
        print("Instructions Run:", ret["instructionCount"])
        print("Read hits:       ", cacheStats["readHits"])
        print("Read misses:     ", cacheStats["readMisses"])
        if (ret["readHits"] + cacheStats["readMisses"]) != 0:
            print("Read miss rate:  ", cacheStats["readMisses"] /
                  (cacheStats["readHits"] + cacheStats["readMisses"]))
        print("Write hits:      ", cacheStats["writeHits"])
        print("Write misses:    ", cacheStats["writeMisses"])
        if (ret["writeHits"] + cacheStats["writeMisses"]) != 0:
            print("Write miss rate: ", cacheStats["writeMisses"] /
                  (cacheStats["writeHits"] + cacheStats["writeMisses"]))

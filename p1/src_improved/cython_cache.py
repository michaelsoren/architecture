# Michael LeMay, 1/19/19

import numpy as np
import random as rand
import datablock
import ram
import cython_address
import copy

class Cache:

    def __init__(self, numSets, numBlocksPerSet,
                 replacementPolicy, writePolicy, blockSize, ramSize, addrObj):
        """Initiates the cache. Creates ram, the numpy arrays that store
        the valid bits, tags, and blocks. Also makes the lists that store
        the lru and fifo queue. Also creates the counting info.
        """
        self.numSets = numSets
        self.numBlocksPerSet = numBlocksPerSet
        self.replacementPolicy = replacementPolicy
        self.writePolicy = writePolicy
        #Cache storage. Tuple is in order: Block, valid bit, tag, dirty bit
        self.blocks = \
            np.empty((numSets, numBlocksPerSet), dtype=datablock.Datablock)

        self.validBits = np.zeros((numSets, numBlocksPerSet), dtype=bool)
        self.tags = np.zeros((numSets, numBlocksPerSet), dtype=int)
        #self.dirtyBits = np.zeros((numSets, numBlocksPerSet), dtype=bool)

        #https://stackoverflow.com/questions/29806226/list-of-variable-length-lists
        #queue used for both fifo and lru. It stores addresses.
        self.queue = lists = [[] for _ in range(numSets)]

        self.ram = ram.Ram(ramSize, blockSize)
        self.addrObj = addrObj

        #counting info
        self.countingInfo = {}
        self.countingInfo["readHits"] = 0
        self.countingInfo["readMisses"] = 0
        self.countingInfo["writeHits"] = 0
        self.countingInfo["writeMisses"] = 0


    def getDouble(self, addr):
        """Given an address, gets the relevant block from the cache
        then returns the double in the block given the address offset.
        """
        blockAtAddr = self.getBlock(addr, "read")
        addrBlockOffset = self.addrObj.getOffset(addr)
        return blockAtAddr.data[addrBlockOffset]


    def setDouble(self, addr, value):
        """Gets the relevant block from the cache. If the cache does not
        have the block, getBlock will handle the miss. Then mark the returned
        block as valid. Set the value of the block. Then set it in memory.
        """
        blockAtAddr = self.getBlock(addr, "write")

        #blockAtAddr.valid = True
        blockAtAddr.data[self.addrObj.getOffset(addr)] = value
        self.setBlock(addr, blockAtAddr)


    def getBlock(self, addr, rOrW):
        """Gets the relevant block from the cache.
        First search for the address in the cache. If in the cache, update
        counting info and recently used list (if needed) and return it.
        If not in the cache, look for a vacancy in the set. If no valid vacancy
        can be found, eject a block from the cache. Otherwise, put the new block
        in the valid vacancy slot and update the relevant info (fifo, lru).
        rOrW is for the counting info.
        """
        addrSetIndex = self.addrObj.getIndex(addr)
        addrTag = self.addrObj.getTag(addr)
        #search cache for independent block
        foundTagInCache = False
        blockSearchIndex = 0
        dimension = self.blocks.shape[1]
        while blockSearchIndex < dimension and not foundTagInCache:
            if self.validBits[addrSetIndex][blockSearchIndex] and \
               self.tags[addrSetIndex][blockSearchIndex] == addrTag:
                foundTagInCache = True
            else:
                blockSearchIndex += 1

        if not foundTagInCache:
            #Tag is not in cache. Cache miss.
            if rOrW == "read":
                self.countingInfo["readMisses"] += 1
            else:
                self.countingInfo["writeMisses"] += 1
            missingBlock = self.ram.getBlock(addr)
            #look for empty slot to put block in
            foundEmptyValidSlot = False
            emptySearchIndex = 0
            while emptySearchIndex < dimension and not \
                  foundEmptyValidSlot:
                if not self.validBits[addrSetIndex][emptySearchIndex]:
                    foundEmptyValidSlot = True
                else:
                    emptySearchIndex += 1
            if foundEmptyValidSlot:
                #found valid empty slot, store new block
                self.blocks[addrSetIndex][emptySearchIndex] = missingBlock
                self.validBits[addrSetIndex][emptySearchIndex] = True
                self.tags[addrSetIndex][emptySearchIndex] = addrTag
                #self.dirtyBits[addrSetIndex][emptySearchIndex] = False
                #update the lru and fifo queues, if necessary
                if self.replacementPolicy == "lru":
                    self.queue[addrSetIndex].append(addr)
                elif self.replacementPolicy == "fifo":
                    self.queue[addrSetIndex].append(addr)
            else:
                #did not find empty valid slot, must evict a block.
                if self.replacementPolicy == "lru":
                    self.updateBlocksAndLruMiss(addrSetIndex, addr, missingBlock)
                elif self.replacementPolicy == "fifo":
                    self.updateBlocksAndFifo(addrSetIndex, addr, missingBlock)
                else:
                    rm = rand.randint(0, self.numBlocksPerSet - 1)
                    #check if dirty and write if so
                    '''if self.dirtyBits[addrSetIndex][rm]:
                        reconstructedAddrVal = \
                            (self.tags[addrSetIndex][rm] << \
                            (addr.numSetBits + addr.numBlockOffsetBits)) + \
                            (addrSetIndex << (addr.numBlockOffsetBits))
                        reconstructedAddr = address.Address(reconstructedAddrVal,
                                                            addr.addrBits,
                                                            addr.numSets,
                                                            addr.numBlocks)
                        self.ram.setBlock(reconstructedAddr,
                                          self.blocks[addrSetIndex][rm])'''
                    self.blocks[addrSetIndex][rm] = missingBlock
                    self.validBits[addrSetIndex][rm] = True
                    self.tags[addrSetIndex][rm] = addrTag
                    #self.dirtyBits[addrSetIndex][rm] = False
            return missingBlock
        else:
            #Found the block in the cache, update info and return it
            if rOrW == "read":
                self.countingInfo["readHits"] += 1
            else:
                self.countingInfo["writeHits"] += 1
            #tag is in cache. if lru, update lru
            if self.replacementPolicy == "lru":
                self.updateLruHit(addrSetIndex, addr)
            return self.blocks[addrSetIndex][blockSearchIndex]


    def setBlock(self, addr, block):
        """Sets a block of a given address with a block. Note that because
        set is only called after get is called, set cannot actually miss. This
        makes set very straightforward. I find the block in the cache, then
        depending on the write policy I update the block
        """
        addrSetIndex = self.addrObj.getIndex(addr)
        addrTag = self.addrObj.getTag(addr)
        #search cache for independent block
        foundTagInCache = False
        blockSearchIndex = 0
        while blockSearchIndex < self.blocks.shape[1] and not foundTagInCache:
            if self.validBits[addrSetIndex][blockSearchIndex] and \
               self.tags[addrSetIndex][blockSearchIndex] == addrTag:
                foundTagInCache = True
            else:
                blockSearchIndex += 1
        #since getBlock was called to get block, we know it is in the cache.
        #If not, this assert prevents further error
        assert foundTagInCache, "Error, tag not found"
        #set the block in the cache
        self.blocks[addrSetIndex][blockSearchIndex] = block
        self.validBits[addrSetIndex][blockSearchIndex] = True
        self.tags[addrSetIndex][blockSearchIndex] = addrTag
        #if self.writePolicy != "write_through":
        #    self.dirtyBits[addrSetIndex][blockSearchIndex] = True
        #else:
        #    self.dirtyBits[addrSetIndex][blockSearchIndex] = False
        #    self.ram.setBlock(addr, block)


    def updateBlocksAndFifo(self, addrSetIndex, addr, missingBlock):
        """updates both cache memory and the fifo queue for the given
        address and missing block
        """
        oldAddr = self.queue[addrSetIndex].pop(0)
        rmAddrTag = self.addrObj.getTag(oldAddr)
        #find the block to remove
        searchIndex = 0
        numBlocksPerSet = self.numBlocksPerSet
        tags = self.tags
        while searchIndex < numBlocksPerSet and \
              tags[addrSetIndex][searchIndex] != rmAddrTag:
            searchIndex += 1
        #check if block is dirty and write if so
        #if self.dirtyBits[addrSetIndex][searchIndex]:
        #    self.ram.setBlock(oldAddr, self.blocks[addrSetIndex][searchIndex])
        #remove old block
        self.blocks[addrSetIndex][searchIndex] = missingBlock
        self.validBits[addrSetIndex][searchIndex] = True
        self.tags[addrSetIndex][searchIndex] = self.addrObj.getTag(addr)
        #self.dirtyBits[addrSetIndex][searchIndex] = False
        #append new address to back of queue
        self.queue[addrSetIndex].append(addr)
        #self.printFifo()


    def updateBlocksAndLruMiss(self, addrSetIndex, addr, missingBlock):
        """updates both cache memory and the lru queue for the given
        address and missing block.
        """
        #remove from back, least recently used
        oldAddr = self.queue[addrSetIndex].pop(0)

        rmAddrTag = self.addrObj.getTag(oldAddr)
        #find block to remove in blocks
        searchIndex = 0
        numBlocksPerSet = self.numBlocksPerSet
        tags = self.tags
        while searchIndex < numBlocksPerSet and \
              tags[addrSetIndex][searchIndex] != rmAddrTag:
            searchIndex += 1

        #check if block is dirty and write if so
        #if self.dirtyBits[addrSetIndex][searchIndex]:
        #    self.ram.setBlock(oldAddr, self.blocks[addrSetIndex][searchIndex])

        #remove old block
        self.blocks[addrSetIndex][searchIndex] = missingBlock
        self.validBits[addrSetIndex][searchIndex] = True
        self.tags[addrSetIndex][searchIndex] = self.addrObj.getTag(addr)
        #self.dirtyBits[addrSetIndex][searchIndex] = False

        #Put on top since it is most recently used
        self.queue[addrSetIndex].append(addr)


    def updateLruHit(self, addrSetIndex, addr):
        """updates the lru queue given a cache hit. Just takes whatever
        address and moves it to the front of the queue/moves everything else
        back a spot
        """
        addrTag = self.addrObj.getTag(addr)
        done = False
        index = 0
        for i, tempAddr in enumerate(self.queue[addrSetIndex]):
            if done:
                break
            if self.addrObj.getTag(tempAddr) == addrTag:
                index = i
                done = True
        tempAddr = self.queue[addrSetIndex][-1]
        self.queue[addrSetIndex][-1] = self.queue[addrSetIndex][index]
        self.queue[addrSetIndex][index] = tempAddr


    def getCacheCountingInfo(self):
        """returns the counting info parameter, left over from
           the c++ implementation I tried at first
        """
        return self.countingInfo


    def printLru(self):
        """Prints out the LRU queue for debugging purposes."""
        print("LRU Queue:")
        for setIndex in range(self.numSets):
            print("\tsetIndex:", setIndex)
            for address in self.queue[setIndex]:
                print("\t\taddress:", address.addr)


    def printFifo(self):
        """Prints out the fifo queue for debugging purposes"""
        print("Fifo Queue:")
        for setIndex in range(self.numSets):
            print("\tsetIndex:", setIndex)
            for address in self.queue[setIndex]:
                print("\t\taddress:", address.addr)


    def printCache(self):
        """Prints out the cache. Used for debugging"""
        print("Cache value:")
        for setId in range(self.numSets):
            print("\tSetId", setId)
            for blockId in range(self.numBlocksPerSet):
                print("\t\tblockId", blockId, self.blocks[setId][blockId].id,
                      self.validBits[setId][blockId], self.tags[setId][blockId])

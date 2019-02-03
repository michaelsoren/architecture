# Michael LeMay, 1/19/19

import numpy as np
import datablock
import address

class Ram:
    def __init__(self, ramSize, blockSize):
        """Initiates ram and ram parameters. Creates all the data blocks
        in ram and gives them their index
        """
        self.ramSize = ramSize
        self.data = np.empty(ramSize, dtype=datablock.Datablock)
        self.blockSize = blockSize
        #initialize all of ram
        for index in range(ramSize):
            self.data[index] = datablock.Datablock(self.blockSize, index)


    def getBlock(self, addr):
        """Gets a block from ram. Which block depends on which block size.
        """
        return self.data[addr // self.blockSize]

    def setBlock(self, addr, value):
        """Sets a block from ram. Which block depends on block size.
        Value is a block.
        """
        self.data[addr // self.blockSize] = value

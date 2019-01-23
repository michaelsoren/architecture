# Michael LeMay, 1/19/19

import numpy as np

class Datablock:


    def __init__(self, size, id):
        """Initiates the block parameters. Base is a numpy array
        of a given size. I am storing doubles in this implementation.
        """
        self.size = size
        self.data = np.zeros(size)
        #self.valid = False
        self.id = id


    def printBlock(self):
        """Prints out all the doubles stored in this block"""
        print("Block is valid:", self.valid)
        for i in range(self.size):
            print("Datablock at", i, ": ", self.data[i])

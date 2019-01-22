# Michael LeMay, 1/19/19

import cpu
import address
import sys
import random as rand
import numpy as np
import time


def main():
    """Overall main function, takes in command line args, loads the args
    dictionary with defaults, prints the arguments, and runs the simulation.
    """
    #arg dictionary
    args = {}
    #default arguments
    args["cacheSizeBytes"] = 65536
    args["blockSizeBytes"] = 64
    args["cacheAssociativity"] = 2
    args["replacementPolicy"] = "lru"
    args["algorithm"] = "mxm_block"
    args["dimension"] = 480
    args["printingEnabled"] = False
    args["blockingFactor"] = 32


    #NOTE: I assume the arguments are passed in correctly.
    for index, arg in enumerate(sys.argv):
        if index != 0:
            if str(arg) == "-c":
                args["cacheSizeBytes"] = int(sys.argv[index + 1])
            elif str(arg) == "-b":
                args["blockSizeBytes"] = int(sys.argv[index + 1])
            elif str(arg) == "-n":
                args["cacheAssociativity"] = int(sys.argv[index + 1])
            elif str(arg) == "-r":
                args["replacementPolicy"] = str(sys.argv[index + 1]).lower()
            elif str(arg) == "-a":
                args["algorithm"] = str(sys.argv[index + 1]).lower()
            elif str(arg) == "-d":
                args["dimension"] = int(sys.argv[index + 1])
            elif str(arg) == "-p":
                args["printingEnabled"] = True
            elif str(arg) == "-f":
                args["blockingFactor"] = int(sys.argv[index + 1])
    args["writePolicy"] = "write_through"
    mySim = CacheSim(args)
    mySim.printArgs()
    #Sanity check is used to do a basic check. Leave commented out
    #for performance.
    #mySim.basicCacheSanityCheck()
    mySim.runSim()


if __name__== "__main__":
    main()


class CacheSim:


    def __init__(self, args):
        """Sets up the cache sim object with arguments. Then uses those
        args to create the cpu
        """
        self.args = args
        self.ramSize = self.args["dimension"] * self.args["dimension"] * 3
        numBlocksInCache = (args["cacheSizeBytes"] //
                            args["blockSizeBytes"]) // 8
        numSets = numBlocksInCache // self.args["cacheAssociativity"]
        #some basic asserts to make sure the input wasn't incorrect.
        assert numSets <= numBlocksInCache
        assert numBlocksInCache > 0
        assert numSets > 0
        self.cpu = cpu.Cpu(numSets,
                           numBlocksInCache // numSets,
                           args["replacementPolicy"],
                           args["writePolicy"],
                           int(args["blockSizeBytes"] / 8),
                           self.ramSize)
        self.addressSize = 32


    def printArgs(self):
        """Simple function that prints out the arguments for a given
        simulation.
        """
        print("Inputs\n---------------------------------------")
        print("Ram size:                     ", self.ramSize)
        print("Cache size:                   ", self.args["cacheSizeBytes"])
        print("Block size:                   ", self.args["blockSizeBytes"])
        numBlocksInCache = (self.args["cacheSizeBytes"] //
                           self.args["blockSizeBytes"]) // 8
        print("Total blocks in cache:        ", numBlocksInCache)
        print("Associativity:                ", self.args["cacheAssociativity"])
        numSets = numBlocksInCache // self.args["cacheAssociativity"]
        print("Number of sets:               ", numSets)
        print("Replacement policy:           ", self.args["replacementPolicy"])
        print("Algorithm:                    ", self.args["algorithm"])
        print("Blocking Factor:              ", self.args["blockingFactor"])
        print("Matrix or vector dimensions:  ", self.args["dimension"])
        print("---------------------------------------")


    def basicCacheSanityCheck(self):
        """Basic check that just loads some number of values into memory.
        I then used prints and other checks to verify that my cache was
        performing in the correct manner.
        """
        numBlocksInCache = (self.args["cacheSizeBytes"] //
                            self.args["blockSizeBytes"]) // 8
        numSets = numBlocksInCache // self.args["cacheAssociativity"]
        numBlocks = numBlocksInCache // numSets
        blockSize = self.args["blockSizeBytes"] // 8
        print("input addr size:", 32, "numSets:", numSets,
              "blockSize:", blockSize)
        for i in range(50000):
            newAddr = address.Address(rand.randint(0, self.ramSize),
                                      self.addressSize, numSets, blockSize)
            self.cpu.storeDouble(newAddr,i)
        self.cpu.cache.printCache()
        self.cpu.cpuStats()


    def runSim(self):
        """Generates the random input and then runs whichever algorithm. Then
        prints the relevant statistics. I used ints to avoid precision errors when
        comparing with the numpy result to check correctness (numpy may do things to
        preserve precision that I am not bothering to do). I use random.choice
        to generate random integer matrixes of the correct size. The values (1, 2)
        were chosen to reduce the chance of overflow.
        """
        overallStart = time.time()
        if self.args["algorithm"] == "mxm":
            x = np.random.choice([1, 2],
                                 size=(self.args["dimension"],
                                       self.args["dimension"]), p=[1./2, 1./2])
            y = np.random.choice([1, 2],
                                 size=(self.args["dimension"],
                                       self.args["dimension"]), p=[1./2, 1./2])
            self.runMxm(x, y)
        elif self.args["algorithm"] == "mxm_block":
            x = np.random.choice([1, 2],
                                  size=(self.args["dimension"],
                                        self.args["dimension"]), p=[1./2, 1./2])
            y = np.random.choice([1, 2],
                                  size=(self.args["dimension"],
                                        self.args["dimension"]), p=[1./2, 1./2])
            self.runMxmBlock(x, y)
        elif self.args["algorithm"] == "daxpy":
            x = np.random.choice([1, 2, 4],
                                  size=(self.args["dimension"],
                                        self.args["dimension"]),
                                  p=[1./3, 1./3, 1./3])
            y = np.random.choice([1, 2, 4],
                                  size=(self.args["dimension"],
                                        self.args["dimension"]),
                                  p=[1./3, 1./3, 1./3])
            d = np.random.randInt(1, 100) #randomly chosen d
            self.runDaxpy(x, y, d)

        print("---------------------------------------")
        print("Result of", self.args["algorithm"], "simulation:")
        self.cpu.cpuStats()
        overallEnd = time.time()
        print("---------------------------------------")
        print("Overall time elapsed:", overallEnd - overallStart)


    def runDaxpy(self, x, y, d):
        """Runs daxpy with a given d, x, and y. First loads the two matrixes into
        cpu memory. Then it does the calcuation in the cpu. Then checks itself
        with numpy to verify correctness.
        """
        addressSize = self.addressSize
        numBlocksInCache = (self.args["cacheSizeBytes"] //
                            self.args["blockSizeBytes"]) // 8
        numSets = numBlocksInCache // self.args["cacheAssociativity"]
        numBlocks = numBlocksInCache // numSets
        blockSize = self.args["blockSizeBytes"] // 8
        n = self.args["dimension"]
        #store all of x and y in memory
        addressInt = 0
        matrixSize = x.shape[0] * x.shape[1]
        loadDataStart = time.time()
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, x[rowIndex, colIndex])
                newAddr = address.Address(addressInt + matrixSize,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, y[rowIndex, colIndex])
                addressInt += 1
        loadDataEnd = time.time()
        print("Time to load data:", loadDataEnd - loadDataStart)
        addressInt = 0
        register0 = d #arbitrary choice of d, passed in
        calculationStart = time.time()
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt,
                                          addressSize, numSets, blockSize)
                register1 = self.cpu.loadDouble(newAddr)
                newAddr = address.Address(addressInt + matrixSize,
                                          addressSize, numSets, blockSize)
                register2 = self.cpu.loadDouble(newAddr)
                register3 = self.cpu.multDouble(register0, register1)
                register4 = self.cpu.addDouble(register3, register2)
                newAddr = address.Address(addressInt + matrixSize * 2,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, register4)
                addressInt += 1
        calculationEnd = time.time()
        print("Time to calculate daxpy:", calculationEnd - calculationStart)
        checkStart = time.time()
        addressInt = 0
        solution = (d * x) + y
        #Check my solution for correctness (and print if flagged)
        allCorrect = True
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt + 2 * matrixSize,
                                          addressSize, numSets, blockSize)
                register0 = self.cpu.loadDouble(newAddr)
                if register0 != solution[rowIndex][colIndex]:
                    allCorrect = False
                if self.args["printingEnabled"]:
                    print(register0, end=' ')
                addressInt += 1
            if self.args["printingEnabled"]:
                print("")
        if allCorrect:
            print("All Correct")
        else:
            print("Something went wrong, answers wrong")
        checkEnd = time.time()
        print("Time to check/print result:", checkEnd - checkStart)


    def runMxmBlock(self, x, y):
        """Runs matrix multiply between x and y. First loads the two matrixes into
        cpu memory, then does the optimized matrix operation using blocking. The
        blocking factor is passed in. Then checks itself with numpy to verify correctness.
        """
        #constants used below
        addressSize = self.addressSize
        numBlocksInCache = (self.args["cacheSizeBytes"] //
                            self.args["blockSizeBytes"]) // 8
        numSets = numBlocksInCache // self.args["cacheAssociativity"]
        numBlocks = numBlocksInCache // numSets
        blockSize = self.args["blockSizeBytes"] // 8
        blockingFactor = self.args["blockingFactor"]
        n = self.args["dimension"]
        matrixSize = x.shape[0] * x.shape[1]
        #store all of x and y in memory
        addressInt = 0
        loadDataStart = time.time()
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, x[rowIndex, colIndex])
                newAddr = address.Address(addressInt + matrixSize,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, y[rowIndex, colIndex])
                addressInt += 1
        loadDataEnd = time.time()
        print("Time to load data:", loadDataEnd - loadDataStart)
        #Compute cache blocked dgemm
        printOn = True
        calculationStart = time.time()
        for blockRow in range(0, n + (n % blockingFactor), blockingFactor):
            for blockColumn in range(0, n + (n % blockingFactor), blockingFactor):
                for blockSum in range(0, n + (n % blockingFactor), blockingFactor):
                    for rowIndex in range(blockingFactor):
                        for colIndex in range(blockingFactor):
                            if rowIndex + blockRow < n and blockColumn + colIndex < n:
                                cIndex = (rowIndex + blockRow) * n +
                                         blockColumn + colIndex + 2 * matrixSize
                                cAddr = address.Address(cIndex, addressSize,
                                                        numSets, blockSize)
                                registerSum = self.cpu.loadDouble(cAddr)
                                for sumIndex in range(blockingFactor):
                                    #calculateIndicies
                                    if sumIndex + blockSum < n:
                                        xIndex = (rowIndex + blockRow) * n +
                                                  sumIndex + blockSum
                                        yIndex = (sumIndex + blockSum) * n +
                                                 colIndex + blockColumn + matrixSize
                                        xAddr = address.Address(xIndex, addressSize,
                                                                numSets, blockSize)
                                        registerX = self.cpu.loadDouble(xAddr)
                                        yAddr = address.Address(yIndex, addressSize,
                                                                numSets, blockSize)
                                        registerY =
                                            self.cpu.loadDouble(yAddr)
                                        #Take product
                                        registerProd =
                                            self.cpu.multDouble(registerX,
                                                                registerY)
                                        #add product to current sum
                                        registerSum =
                                            self.cpu.addDouble(registerSum,
                                                               registerProd)
                                self.cpu.storeDouble(cAddr, registerSum)
        calculationEnd = time.time()
        print("Time to calculate mxm_blocked:", calculationEnd - calculationStart)
        #Check my solution for correctness (and print if flagged)
        checkStart = time.time()
        solution = np.dot(x, y)
        allCorrect = True
        addressInt = 0
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt + 2 * matrixSize,
                                          addressSize, numSets, blockSize)
                register0 = self.cpu.loadDouble(newAddr)
                if register0 != solution[rowIndex][colIndex]:
                    allCorrect = False
                if self.args["printingEnabled"]:
                    print(register0, end=' ')
                addressInt += 1
            if self.args["printingEnabled"]:
                print("")
        if allCorrect:
            print("All Correct")
        else:
            print("Something went wrong, answers wrong")
        checkEnd = time.time()
        print("Time to check/print result:", checkEnd - checkStart)


    def runMxm(self, x, y):
        """Runs matrix multiply between x and y. First loads the two matrixes into
        cpu memory, then does the unoptimized matrix operation. Then checks itself
        with numpy to verify correctness.
        """
        #constants used below
        addressSize = self.addressSize
        numBlocksInCache = (self.args["cacheSizeBytes"] //
                            self.args["blockSizeBytes"]) // 8
        numSets = numBlocksInCache // self.args["cacheAssociativity"]
        numBlocks = numBlocksInCache // numSets
        blockSize = self.args["blockSizeBytes"] // 8
        n = self.args["dimension"]
        matrixSize = x.shape[0] * x.shape[1]
        #store all of x and y in memory
        addressInt = 0
        loadDataStart = time.time()
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, x[rowIndex, colIndex])
                newAddr = address.Address(addressInt + matrixSize,
                                          addressSize, numSets, blockSize)
                self.cpu.storeDouble(newAddr, y[rowIndex, colIndex])
                addressInt += 1
        loadDataEnd = time.time()
        print("Time to load data:", loadDataEnd - loadDataStart)
        #compute MxM, no optimizations.
        calculationStart = time.time()
        for rowIndex in range(n):
            for colIndex in range(n):
                resIndex = (rowIndex) * n + colIndex + 2 * matrixSize
                resAddr = address.Address(resIndex, addressSize,
                                          numSets, blockSize)
                registerSum = self.cpu.loadDouble(resAddr)
                for sumIndex in range(n):
                    #calculate indicies
                    xIndex = n * rowIndex + sumIndex
                    yIndex = colIndex + n * sumIndex
                    xAddr = address.Address(xIndex, addressSize,
                                            numSets, blockSize)
                    registerX = self.cpu.loadDouble(xAddr)
                    yAddr = address.Address(yIndex + matrixSize, addressSize,
                                            numSets, blockSize)
                    registerY = self.cpu.loadDouble(yAddr)
                    #Take product
                    registerProd = self.cpu.multDouble(registerX, registerY)
                    #add product to current sum
                    registerSum = self.cpu.addDouble(registerSum, registerProd)
                #Set value in memory
                self.cpu.storeDouble(resAddr, registerSum)
        calculationEnd = time.time()
        print("Time to calculate mxm:", calculationEnd - calculationStart)
        #print out resulting matrix
        checkStart = time.time()
        addressInt = 0
        #calculates correct solution with numpy
        solution = np.dot(x, y)
        #Check my solution for correctness (and print if flagged)
        allCorrect = True
        for rowIndex in range(n):
            for colIndex in range(n):
                newAddr = address.Address(addressInt + 2 * matrixSize,
                                          addressSize, numSets, blockSize)
                register0 = self.cpu.loadDouble(newAddr)
                if register0 != solution[rowIndex][colIndex]:
                    allCorrect = False
                if self.args["printingEnabled"]:
                    print(register0, end=' ')
                addressInt += 1
            if self.args["printingEnabled"]:
                print("")
        if allCorrect:
            print("All Correct")
        else:
            print("Something went wrong, answers wrong")
            print("X:", x, "\nY:", y)
        checkEnd = time.time()
        print("Time to check/print result:", checkEnd - checkStart)

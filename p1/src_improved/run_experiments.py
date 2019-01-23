# Michael LeMay, 1/19/19

import cache_sim
import subprocess as sb

with open('data.txt', "w") as outfile:
    #empty the data file
    sb.run(["echo", "Simulation Data"], stdout=outfile)
    #skips two lines
    sb.run(["echo", " "], stdout=outfile)
    sb.run(["echo", " "], stdout=outfile)

    #sb.run(["python", "cache_sim.py", "-c", "", "-b", "", "-n", "",
    #        "-r", "", "-a", "", "-d", "", "-f", ""], stdout=outfile)
    #Skip a line
    #sb.run(["echo", " "], stdout=outfile)

    print("Starting experiments")

    #Associativity
    associativities = ["1", "2", "4", "8", "16", "128"]
    for associativity in associativities:
        sb.run(["python", "cache_sim.py", "-n", associativity,
                ">>", "data.txt"], stdout=outfile)
        #Skip a line
        sb.run(["echo", "----------------"], stdout=outfile)
    print("Finished Associativy, 1/5")
    sb.run(["echo", " "], stdout=outfile)
    sb.run(["echo", "----------------"], stdout=outfile)
    sb.run(["echo", " "], stdout=outfile)

    blockSizeBytes = ["8", "16", "32", "64", "128", "256", "512", "1024"]
    for blockSize in blockSizeBytes:
        sb.run(["python", "cache_sim.py", "-b", blockSize], stdout=outfile)
        #Skip a line
        sb.run(["echo", "----------------"], stdout=outfile)
    print("Finished block size, 2/5")
    sb.run(["echo", " "], stdout=outfile)
    sb.run(["echo", "----------------"], stdout=outfile)
    sb.run(["echo", " "], stdout=outfile)

    totalCacheSizeBytes = ["4096", "8192", "16384", "32768", "65536", "131072", "262144", "524288"]
    for totalCacheSize in totalCacheSizeBytes:
        sb.run(["python", "cache_sim.py", "-c", totalCacheSize], stdout=outfile)
        #Skip a line
        sb.run(["echo", "----------------"], stdout=outfile)
    print("Finished cache size, 3/5")
    sb.run(["echo", " "], stdout=outfile)
    sb.run(["echo", "----------------"], stdout=outfile)
    sb.run(["echo", " "], stdout=outfile)

    associativities_second = ["2", "8", "128"]
    problemSizes = [("480", "mxm"), ("480", "mxm_block"), ("488", "mxm"), ("488", "mxm_block"), ("512", "mxm"), ("512", "mxm_block")]
    for associativity in associativities_second:
        for problemSize in problemSizes:
            sb.run(["python", "cache_sim.py", "-n", associativity,
                    "-a", "daxpy", "-d", problemSize[0]], stdout=outfile)
            #Skip a line
            sb.run(["echo", "----------------"], stdout=outfile)
    print("Finished problem size/associativity, 4/5")
    sb.run(["echo", " "], stdout=outfile)
    sb.run(["echo", "----------------"], stdout=outfile)
    sb.run(["echo", " "], stdout=outfile)

    replacementPolicies = ["random", "FIFO", "LRU"]
    for replacementPolicy in replacementPolicies:
        sb.run(["python", "cache_sim.py", "-r", replacementPolicy], stdout=outfile)
        #Skip a line
        sb.run(["echo", "----------------"], stdout=outfile)
    print("Finished replacement policy, 5/5")

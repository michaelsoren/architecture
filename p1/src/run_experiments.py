# Michael LeMay, 1/19/19

import cache_sim
import subprocess as sb

#empty the data file
sb.run(["echo", "\"Simulation", "Data\"", ">", "data.txt"])
#skips two lines
sb.run(["echo", " ", ">>", "data.txt"])
sb.run(["echo", " ", ">>", "data.txt"])

#sb.run(["python", "cache-sim", "-c", "", "-b", "", "-n", "",
#        "-r", "", "-a", "", "-d", "", "-f", "", ">>", "data.txt"])
#Skip a line
#sb.run(["echo", " ", ">>", "data.txt"])

#Associativity
associativities = ["1", "2", "4", "8", "16", "1024"]
for associativity in associativities:
    sb.run(["python", "cache-sim", "-n", associativity,
            ">>", "data.txt"])
    #Skip a line
    sb.run(["echo", " ", ">>", "data.txt"])

sb.run(["echo", " ", ">>", "data.txt"])
sb.run(["echo", " ", ">>", "data.txt"])

blockSizesBytes = ["8", "16", "32", "64", "128", "256", "512", "1024"]
for blockSize in blockSizeBytes:
    sb.run(["python", "cache-sim", "-b", blockSize, ">>", "data.txt"])
    #Skip a line
    sb.run(["echo", " ", ">>", "data.txt"])

sb.run(["echo", " ", ">>", "data.txt"])
sb.run(["echo", " ", ">>", "data.txt"])

totalCacheSizeBytes = ["4096", "8192", "16384", "32768", "65536", "131072", "262144", "524288"]
for totalCacheSize in totalCacheSizeBytes:
    sb.run(["python", "cache-sim", "-c", totalCacheSize, ">>", "data.txt"])
    #Skip a line
    sb.run(["echo", " ", ">>", "data.txt"])

sb.run(["echo", " ", ">>", "data.txt"])
sb.run(["echo", " ", ">>", "data.txt"])

associativities_second = ["2", "8", "128"]
problemSizes = [("480", "mxm"), ("480", "mxm_block"), ("488", "mxm"), ("488", "mxm_block"), ("512", "mxm"), ("512", "mxm_block")]
for associativity in associativities_second:
    for problemSize in problemSizes:
        sb.run(["python", "cache-sim", "-c", "", "-b", "", "-n", associativity,
                "-a", problemSize[1], "-d", problemSize[0], ">>", "data.txt"])
        #Skip a line
        sb.run(["echo", " ", ">>", "data.txt"])

sb.run(["echo", " ", ">>", "data.txt"])
sb.run(["echo", " ", ">>", "data.txt"])

replacementPolicies = ["random", "FIFO", "LRU"]
for replacementPolicy in replacementPolicies:
    sb.run(["python", "cache-sim", "-r", replacementPolicy, ">>", "data.txt"])
    #Skip a line
    sb.run(["echo", " ", ">>", "data.txt"])

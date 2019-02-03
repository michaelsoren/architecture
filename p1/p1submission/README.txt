Assignment: p1
By: Michael LeMay (mjlemay)

This cache simulator is implemented in python, with a bit of cython included
for efficiency. This readme will describe the code and how to run it.

Implementation:

The code is the described cache simulator. It consists of 7 files
(cache-sim.py, cython_address.pyx, cache.py, cpu.py, datablock.py, ram.py,
and setup.py). The layout of the project matches the vague outline of figure 1
in the assignment.

cache-sim.py implements the command line interface and the
algorithms (mxm, daxpy, and mxm_block) I was asked to implement.

cython_address.pyx is the address class. An address class for me is a set of
constant information for a cache (the number of set and tag bits, etc) that is
used to bitmask different parts of an integer address. The implementation is
a cython file (.pyx) which is then compiled by setup.py to C. This is written
as a cython file in order to increase runtime performance by a factor of 2.
The c output is then imported into the rest of the python code, and saves all
of the type and error checking that would otherwise be needed.

cache.py is where the bulk of the code is, and is my implementation of the
cache. It should be a standard implementation, with the one exception that
I also implemented the capability to run the cache as write back instead of
write through. The cache's data is stored in a 2d numpy array of datablocks
that are based around the set in the first dimension, then are iterable from
in the second dimension. The cache implements the same methods as described in
figure 1. The cache uses a queue that is either an LRU queue or FIFO queue
when appropriate that stores addresses (for me, an address is just an integer).
It also stores a single address class instance, which is then used to calculate
the relevant fields for a given integer address.

cpu.py is my cpu, and it just has a cache and implements the basic functions
as described in figure one of the assignment.

datablock.py is implemented using doubles, rather than bytes, so that I could
use numpy for increased efficiency and ease. A numpy array is the backbone
of each datablock. If I had more time, this file could probably have been
implemented in cython as well, but it wouldn't have had as large a performance
boost as turning address.py into cython.

ram.py is also quite straightforward. It has a 1d numpy array of datablocks and
uses the block size to index the address in correctly.

setup.py is a basic file used to compile the cython file. More on how to use
that after.

The code should be commented pretty thoroughly. I wasn't sure how much was
too much, but it should be clear.

As far as I can tell, the code works and runs perfectly. The algorithms
generate the correct answer, I check with numpy, and the cache seems to behave
correctly, both upon manual inspection and in the data output itself.

One thing to note: in order to really get solid assurance my code was working,
I ran my tests with randomly generated X and Y matrixes. I am not quite
clear on if this was correct or not. But I felt it was a defensible choice, since
it only makes it more likely my cache works.

Running:

Running the code is straightforward. First you must run

      python setup.py build_ext --inplace

inside the src folder. This builds the cython file into cython_address.c.

Then just run

      python cache-sim.py [whatever flags you want, if any]

and it should run perfectly.

The output should just be printed out, for redirection or whatever.
I included timers as well in the output. They shouldn't get in the way
and help capture the other aspect of cache performance
(and simulator performance).

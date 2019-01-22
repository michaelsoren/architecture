all: cache-sim

cache-sim: cache-sim.o cpu.o address.o datablock.o ram.o cache.o
	g++ -o cache-sim cache-sim.o cpu.o address.o datablock.o ram.o cache.o

cache-sim.o: cache-sim.cpp cpu.h
	g++ -c cache-sim.cpp

address.o: address.cpp address.h
	g++ -c address.cpp

cache.o: cache.cpp ram.h datablock.h address.h
	g++ -c cache.cpp

cpu.o: cpu.cpp cpu.h cache.h address.h
	g++ -c cpu.cpp

datablock.o: datablock.cpp datablock.h
	g++ -c datablock.cpp

ram.o: ram.cpp ram.h datablock.h address.h
	g++ -c ram.cpp

clean:
	rm -rf *o cache-sim

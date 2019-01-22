/* Michael LeMay, 1/13/19 */

#include "cpu.h"
#include "address.h"
#include "cache.h"
#include <iostream>
#include <string>


/* CPU implementation */

/*
 * Constructor for CPU. Initiates ram and cache.
 */
Cpu::Cpu(int newNumSets, int newNumBlocks,
         std::string theReplacementPolicy,
	 std::string theWritePolicy) {
  /*Load in private variables*/
  numSets = newNumSets;
  numBlocks = newNumBlocks;
  replacementPolicy = theReplacementPolicy;
  writePolicy = theWritePolicy;

  /*Create the associated cache object the cpu needs*/
  cache = Cache(newNumSets, newNumBlocks, replacementPolicy, writePolicy);
}

/*
 * This gets a double from ram or cache based on the address
 */
double Cpu::loadDouble(Address addr) {
  /*Ask for value from Cache at addr*/
  double doubleAtAddr = cache.getDouble(addr);
  /*Return the desired double*/
  return doubleAtAddr;
}


/*
 * Loads a double into cache, or ram
 */
void Cpu::storeDouble(Address addr, double value) {
  cache.setDouble(addr, value);
}


/*
 * Add two doubles together
 */
double Cpu::addDouble(double value1, double value2) {
  return value1 + value2;
}


/*
 * Multiply two doubles together
 */
double Cpu::multDouble(double value1, double value2) {
  return value1 * value2;
}

/* Michael LeMay, 1/13/19 */


#include <iostream>
#include <cmath>
#include "address.h"


/* Address implementation */

/*
 * Basic constructor
 */
Address::Address(int newAddr, int newAddrBits, int newNumSets, int newNumBlocks) {
  addr = newAddr;
  addrBits = newAddrBits;
  numSets = newNumSets;
  numBlocks = newNumBlocks;

  /*Calculate the number of bits*/
  calcNumBlockOffsetBits();
  calcNumSetBits();
  calcNumTagBits();
}


/*
 * Grabs first numBits bits of the address.
 * numBits must be a valid number of bits to request
 */
int Address::getTag() {
  /*Creates the mask of correct size*/
//  std::cout << "ex: "  << ~0 << ", " << ~0 << (sizeof(int) - numBits);
  int mask = (1 <<  numTagBits) - 1;
  mask = mask << (numSetBits + numBlockOffsetBits);
  printf("mask: %d", mask);
  return (addr & mask) >> (numSetBits + numBlockOffsetBits);
}


/*
 * Grabs middle set index from addr
 * numBits must be a valid number of bits to request
 */
int Address::getIndex() {
  /*Creates the mask of correct size*/
  int mask = (1 << numSetBits) - 1;
  /*Shifts mask over to cover the set index*/
  mask = mask << numBlockOffsetBits;
  return (addr & mask) >> numBlockOffsetBits;
}


/*
 * Grabs last numBits bits of addr.
 * numBits must be a valid number of bits to request
 */
int Address::getOffset() {
  /*Creates the mask of correct size*/
  int mask = (1 << numBlockOffsetBits) - 1;
  return addr & mask;
}


/*Calculate number of bits for each part of address, load them in object*/

/*
 * Calculates number of offset bits with log base 2 rounded up
 */
void Address::calcNumBlockOffsetBits() {
   numBlockOffsetBits = (int) ceil(log2((double) numBlocks));
}


/*
 * Calculate the number of set index bits with log base 2 rounded up
 */
void Address::calcNumSetBits() {
   numSetBits = (int) ceil(log2((double) numSets));
}


/*
 * Calculate the number of tag bits as the difference between addr bits
 * and the set bits and block offset bits
 */
void Address::calcNumTagBits() {
  numTagBits = addrBits - numBlockOffsetBits - numSetBits;
}

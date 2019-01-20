/* Michael LeMay, 1/13/19 */

#include "ram.h"
#include "datablock.h"
#include "address.h"
#include <iostream>
#include <vector>


/* Ram implementation */

int main() {
  return 0;
}

/*
 * Basic constructor for ram
 */
Ram::Ram(int newNumBlocks) {
  numBlocks = newNumBlocks;
  std::vector<Datablock> temp(numBlocks, Datablock());
  temp.resize(numBlocks);
  data = temp;
}

/*
 * fetches a block based on an address
 * NOTE: This might be wrong. Does address index
 *       cleanly into ram? Or no. Want part without
 *       the block offset.
 */
Datablock Ram::getBlock(Address addr) {
  return data[addr.addr / data[0].size];
}

/*
 * Sets the datablock at a given address
 * NOTE: This might be wrong. Does address index
 *       cleanly into Ram? Or no.
 */
void Ram::setBlock(Address addr, Datablock value) {
  data[addr.addr / data[0].size] = value;
}

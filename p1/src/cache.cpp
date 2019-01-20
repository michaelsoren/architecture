/* Michael LeMay, 1/14/19 */

#include "datablock.h"
#include "address.h"
#include "ram.h"
#include "cache.h"
#include <string>
#include <vector>
#include <algorithm>
#include <queue>

/*Cache implementation*/

/*
 * Default constructor, needed for compilation elsewhere.
 */
Cache::Cache() {
  numSets = 1;
  numBlocks = 1;
  replacementPolicy = "";
  writePolicy = "";
  /*Initiate cache storage*/
  std::vector<std::vector<Datablock> >
       tempBlocks(numSets, std::vector<Datablock>(numBlocks));
  blocks = tempBlocks;
  /*Valid bit storage*/
  std::vector<std::vector<bool> >
       tempValidBits(numSets, std::vector<bool>(numBlocks));
  validBits = tempValidBits;
  /*Tag storage*/
  std::vector<std::vector<int> >
       tempTags(numSets, std::vector<int>(numBlocks));
  tags = tempTags;
  /*Dirty bit storage*/
  std::vector<std::vector<bool> >
       tempDirty(numSets, std::vector<bool>(numBlocks));
  dirty = tempDirty;

  /*Initiate ram*/
  ram = Ram(numBlocks);
  std::vector<std::vector<Address> >
       tempLru(numSets, std::vector<Address>(numBlocks));
  lruQueue = tempLru;
  std::vector<std::queue<Address> >
       tempFifo(numSets, std::queue<Address>());
  fifoQueue = tempFifo;
}


/*
 * Custom constructor, sets up all the variables.
 */
Cache::Cache(int newNumSets, int newNumBlocks,
             std::string newReplacementPolicy,
	     std::string newWritePolicy) {
  numSets = newNumSets;
  numBlocks = newNumBlocks;
  replacementPolicy = newReplacementPolicy;
  writePolicy = newWritePolicy;

  /*Initiate cache storage*/
  std::vector<std::vector<Datablock> >
       temp(numSets, std::vector<Datablock>(numBlocks));
  blocks = temp;

  /*Initiate ram*/
  ram = Ram(numBlocks);
}

/*
 * Get a specific address from a cache or RAM, if not in cache
 * This is a cache read
 */
double Cache::getDouble(Address addr) {
  /*Grab the relevant block from the cache (could be null if miss)*/
  Datablock blockAtAddr = getBlock(addr);
  //if (blockAtAddr == NULL) {
    /*Not in cache or ram, error*/
  //  return -1.0;
  //}
  int addrBlockOffset = addr.getOffset();
  /*Return the double stored in the block offset of the block*/
  return blockAtAddr.data[addrBlockOffset];
}

/*
 * Set a specific address in the cache, or ram, to a value.
 */
void Cache::setDouble(Address addr, double value) {
  /*Get the relevant block from cache or ram*/
  Datablock blockAtAddr = getBlock(addr);
  //if (blockAtAddr == NULL) {
    /*Not in cache or ram, error*/
  //  return;
  //}
  /*Modify the value of the block at the offset*/
  blockAtAddr.data[addr.getOffset()] = value;
  /*Set the block in memory*/
  setBlock(addr, blockAtAddr);
}

/*
 * Returns a specific block from the cache or ram
 */
Datablock Cache::getBlock(Address addr) {
  /* Finds the set index for desired block */
  int addrSetIndex = addr.getIndex();
  /*Gets the address tag*/
  int addrTag = addr.getTag();
  /*Iterate through blocks looking for matching tag*/
  bool foundTag = false;
  int i;
  for (i = 0; i < blocks[addrSetIndex].size() && !foundTag; i++) {
    if (!foundTag && blocks[addrSetIndex][i].blockValid &&
        addrTag == blocks[addrSetIndex][i].blockTag) {
      foundTag = true;
    }
  }
  /*Check if matching and valid tag found*/
  if (!foundTag) {
    /*Record miss, block not in cache*/
    /*Get missing block from ram*/
    Datablock missingBlock = ram.getBlock(addr);
    /*Check to see if there are any potential vacancies in cache
      to put the block*/
    bool foundEmpty = false;
    int j;
    for (j = 0; j < numBlocks && !foundEmpty; j++) {
      if (!validBits[addrSetIndex][j]) {
        foundEmpty = true;
      }
    }
    /*Check if empty block found*/
    if (!foundEmpty) {
      /*If not, then split on replacement policy.
        Make sure to write to memory if changed*/
      if (replacementPolicy == "lru") {
        /*lru ejection, remove the last used address*/
        updateLruWithMiss(addrSetIndex, addr, missingBlock);
      } else if (replacementPolicy == "fifo") {
        /*fifo ejection, remove first address in stack*/
        updateFifo(addrSetIndex, addr, missingBlock);
      } else {
        /*Random ejection*/
        int rm = rand() % numBlocks;
        /*Check if overwritten block is dirty. If so write the block to memory*/
        if (dirty[addrSetIndex][rm]) {
          int reconstructedAddrVal = (tags[addrSetIndex][rm] << (addr.numSetBits +
                                              addr.numBlockOffsetBits)) +
                                  (addrSetIndex << (addr.numBlockOffsetBits));
          Address reconstructedAddr =
              Address(reconstructedAddrVal,
                      addr.addrBits, addr.numSets, addr.numBlocks);
          ram.setBlock(reconstructedAddr, blocks[addrSetIndex][rm]);
        }
        blocks[addrSetIndex][rm] = missingBlock;
        validBits[addrSetIndex][rm] = 1;
        tags[addrSetIndex][rm] = addr.getTag();
      }
    } else {
      /*Empty block found, put block in vacancy and mark fields.*/
      blocks[addrSetIndex][j] = missingBlock;
      validBits[addrSetIndex][j] = true;
      tags[addrSetIndex][j] = addrTag;
    }
    /*Update least recently used/fifo information*/
    if (replacementPolicy == "lru") {
      /*Add least recently used address to back*/
      lruQueue[addrSetIndex].push_back(addr);
    } else if (replacementPolicy == "fifo") {
      /*add recently added*/
      fifoQueue[addrSetIndex].push(addr);
    }
    /*return block*/
    return blocks[addrSetIndex][i];
  } else {
    /*Tag found in cache, update least recently used queue.*/
    /*Lru update. Tag was found*/
    updateLruWithHit(addrSetIndex, addr);
    /*Return block*/
    return blocks[addrSetIndex][i];
  }
}

/*
 * Writes to a specific block, either cache or ram
 */
void Cache::setBlock(Address addr, Datablock block) {
  /*Calculates which set and which block slot*/
  int addrSetIndex = addr.getIndex();
  /*Gets the address tag*/
  int addrTag = addr.getTag();
  /*Iterate through blocks looking for the block*/
  /*If direct mapped length will be one.*/
  bool foundTagInCache = false;
  int i;
  for (i = 0; i < numBlocks && !foundTagInCache; i++) {
    if (!foundTagInCache && !validBits[addrSetIndex][i] &&
        addrTag == tags[addrSetIndex][i]) {
      foundTagInCache = true;
    }
  }
  /*Check if tag found*/
  if (!foundTagInCache) {
    /*Tag not found, record miss
      Need to fetch from memory to write it*/
    /*Look for vacancies to put new block*/
    bool foundEmptyValidSlot = false;
    for (i = 0; i < numBlocks && !foundEmptyValidSlot; i++) {
      if (!validBits[addrSetIndex][i]) {
        foundEmptyValidSlot = true;
      }
    }
    /*Check if empty block found*/
    if (!foundEmptyValidSlot) {
      /*No empty valid space found,
        need to kick out a block based on whatever policy*/
      /*TODO*/
      if (replacementPolicy == "lru") {
        /*lru ejection*/
        updateLruWithMiss(addrTag, addr, block);
      } else if (replacementPolicy == "fifo") {
        /*fifo ejection*/
        updateFifo(addrTag, addr, block);
      } else {
        /*Random ejection*/
        int rm = rand() % numBlocks;
        /*Check if overwritten block is dirty. If so write the block to memory*/
        if (dirty[addrSetIndex][rm]) {
          int reconstructedAddrVal = (tags[addrSetIndex][rm] << (addr.numSetBits +
                                              addr.numBlockOffsetBits)) +
                                  (addrSetIndex << (addr.numBlockOffsetBits));
          Address reconstructedAddr = Address(reconstructedAddrVal,
                                              addr.addrBits, addr.numSets,
                                              addr.numBlocks);
          ram.setBlock(reconstructedAddr, blocks[addrSetIndex][rm]);
        }
        blocks[addrSetIndex][rm] = block;
        validBits[addrSetIndex][rm] = true;
        tags[addrSetIndex][rm] = addrTag;
      }
      /*Modify block in memory*/
    } else {
      /*Otherwise Load into empty slot and update information*/
      blocks[addrSetIndex][i] = block;
      validBits[addrSetIndex][i] = true;
      tags[addrSetIndex][i] = addrTag;
      /*Update block information*/
      if (replacementPolicy == "lru") {
        /*Add least recently used address to back*/
        lruQueue[addrSetIndex].push_back(addr);
      } else if (replacementPolicy == "fifo") {
        /*add recently added*/
        fifoQueue[addrSetIndex].push(addr);
      }
    }
  } else {
    /*Tag found in cache, cache hit.
      Put new block in this slot/overwrite old block*/
    blocks[addrSetIndex][i] = block;
    /*Update valid and tag*/
    validBits[addrSetIndex][i] = true;
    tags[addrSetIndex][i] = addrTag;
    /*Update memory (or not) depending on write policy. Or mark bit*/
    if (writePolicy == "write through") {
      ram.setBlock(addr, block);
    } else {
       dirty[addrSetIndex][i] = true;
    }
  }
}

void Cache::updateFifo(int addrSetIndex,
                       Address addr,
                       Datablock missingBlock) {
  Address oldAddr = fifoQueue[addrSetIndex].front();
  int rmAddrTag = oldAddr.getTag();
  /*Find old address*/
  int i;
  for (i = 0; i < numBlocks &&
       tags[addrSetIndex][i] != rmAddrTag; i++) {}
  if (dirty[addrSetIndex][i]) {
    ram.setBlock(oldAddr, blocks[addrSetIndex][i]);
  }
  /*Removes the block*/
  blocks[addrSetIndex][i] = missingBlock;
  /*Remove the old address from the stack*/
  fifoQueue[addrSetIndex].pop();
  /*Add the new address to the stack*/
  fifoQueue[addrSetIndex].push(addr);
}

void Cache::updateLruWithMiss(int addrSetIndex,
                              Address addr,
                              Datablock missingBlock) {
  int oldInd = 0;
  /*If dirty bit of removing is marked, update memory*/
  Address oldAddr = lruQueue[addrSetIndex][oldInd];
  int rmAddrTag = oldAddr.getTag();
  /*Find old address*/
  int i;
  for (i = 0; i < numBlocks &&
       tags[addrSetIndex][i] != rmAddrTag; i++) {}
  /*Write the block if dirty*/
  if (dirty[addrSetIndex][i]) {
    ram.setBlock(oldAddr, blocks[addrSetIndex][i]);
  }
  /*Removes the block*/
  blocks[addrSetIndex][i] = missingBlock;

  /*Advance everything in line. Guaranteed to remove at index 0.*/
  for (oldInd = 1; oldInd < lruQueue[addrSetIndex].size(); oldInd++) {
    lruQueue[addrSetIndex][oldInd - 1] = lruQueue[addrSetIndex][oldInd];
  }
  /*Set back of the line to the just added block*/
  lruQueue[addrSetIndex][oldInd - 1] = addr;
}

void Cache::updateLruWithHit(int addrSetIndex, Address addr) {
  int oldInd = 0;
  int newInd = 0;
  int addrTag = addr.getTag();
  /*Advance everything in line, but overwrite the recently used address*/
  for (oldInd = 0; oldInd < lruQueue[addrSetIndex].size(); oldInd++) {
    if (lruQueue[addrSetIndex][oldInd].getTag() != addrTag) {
      lruQueue[addrSetIndex][newInd] =
          lruQueue[addrSetIndex][oldInd];
      newInd += 1;
    }
  }
  /*Put recently used address at the back.*/
  lruQueue[addrSetIndex][lruQueue[addrSetIndex].size() - 1] = addr;
}

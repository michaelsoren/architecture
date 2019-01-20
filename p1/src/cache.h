/* Michael LeMay, 1/13/19 */

#ifndef CACHE
#define CACHE

#include "datablock.h"
#include "address.h"
#include "ram.h"
#include <string>
#include <vector>
#include <queue>

/* Cache header*/

class Cache {
  public:
    int numSets;
    int numBlocks;
    std::vector< std::vector<Datablock> > blocks;
    std::vector<std::vector<bool> > validBits;
    std::vector<std::vector<bool> > dirty;
    std::vector<std::vector<int> > tags;
    std::string replacementPolicy;
    std::string writePolicy;

    Cache();
    Cache(int newNumSets, int newNumBlocks,
          std::string replacementPolicy,
          std::string writePolicy);

    double getDouble(Address addr);
    void setDouble(Address addr, double value);
    Datablock getBlock(Address addr);
    void setBlock(Address addr, Datablock block);

  private:
     Ram ram;
     std::vector<std::vector<Address> > lruQueue;
     std::vector<std::queue<Address> > fifoQueue;
     void updateFifo(int addrSetIndex, Address addr, Datablock missingBlock);
     void updateLruWithMiss(int addrSetIndex, Address addr,
                            Datablock missingBlock);
     void updateLruWithHit(int addrSetIndex, Address addr);
};

#endif

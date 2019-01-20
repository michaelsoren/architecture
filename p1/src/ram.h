/* Michael LeMay, 1/13/19 */

#include <vector>
#include "datablock.h"
#include "address.h"

/* ram header */

#ifndef RAM 
#define RAM 

class Ram {

  public:
    int numBlocks;
    std::vector<Datablock> data;

    Ram();
    Ram(int newNumBlocks);
    Datablock getBlock(Address addr);
    void setBlock(Address addr, Datablock value);
};

#endif

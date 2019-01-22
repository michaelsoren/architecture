/* Michael LeMay, 1/13/19 */

#include "cache.h"
#include "ram.h"
#include "address.h"
#include <string>

/* Address header */

#ifndef CPU
#define CPU 

class Cpu {

  public:
    Cpu(int newNumSets, int newNumBlocks,
        std::string replacementPolicy,
	std::string writePolicy);

    double loadDouble(Address addr);
    void storeDouble(Address addr, double value);
    double addDouble(double value1, double value2);
    double multDouble(double value1, double value2);

  private:
    int numSets;
    int numBlocks;
    std::string replacementPolicy;
    std::string writePolicy;
 
    Cache cache;
};

#endif

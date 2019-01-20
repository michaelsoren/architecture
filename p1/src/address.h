/* Michael LeMay, 1/13/19 */

/* Address header */

#ifndef ADDRESS
#define ADDRESS

class Address {

  public:
    int addr;
    int numSets;
    int numBlocks;
    int addrBits;

    int numBlockOffsetBits;
    int numSetBits;
    int numTagBits;

    Address();
    Address(int newAddr, int newAddrBits, int numSets, int numBlocks);
    int getTag();
    int getIndex();
    int getOffset();



  private:
    void calcNumBlockOffsetBits();
    void calcNumSetBits();
    void calcNumTagBits();
};

#endif

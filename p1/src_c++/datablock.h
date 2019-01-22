/* Michael LeMay, 1/13/19 */

/* DataBlock header */

#ifndef DATABLOCK 
#define DATABLOCK

class Datablock {

  public:
    int size;
    double *data;
    int blockTag;
    bool blockValid;

    Datablock(int theSize);
    Datablock();

};

#endif

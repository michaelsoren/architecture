/* Michael LeMay, 1/13/19 */

#include "datablock.h"

/*Datablock implementation*/


Datablock::Datablock(int theSize) {
  size = theSize;
  /*Make sure you delete data before deleting datablock*/
  data = new double[size];
  blockTag = 0;
  blockValid = false;
}

Datablock::Datablock() {
  size = 0;
  data = new double[0];
  blockTag = 0;
  blockValid = false;
}

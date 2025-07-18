#ifndef PHPHYSICSLISTS_HH
#define PHPHYSICSLISTS_HH

#include "G4VModularPhysicsList.hh"
#include "G4EmStandardPhysics.hh"

class PMPhysicsList :  public G4VModularPhysicsList
{
public :
    PMPhysicsList();
    ~PMPhysicsList();
};

#endif
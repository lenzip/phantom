#!/bin/bash

source /cvmfs/projects.cern.ch/intelsw/psxe/linux/all-setup.sh intel64
if [ ! -f libLHAPDF.so.0 ]; then
  ln -s  /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/lhapdf/6.1.6-ikhhed2/lib/libLHAPDF.so libLHAPDF.so.0
fi  

export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH

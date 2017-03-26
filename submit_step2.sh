#!/bin/bash

cd GRID_FOLDER_TEMP ; 
for fil in `find . -name "phavegas*"`  ; do echo `pwd`/$fil ; done > GEN_FOLDER_TEMP/phav.dat ; 
cd .. ; 

cd GEN_FOLDER_TEMP ; 
cp BASE_FOLDER/tools/gendir.scr ./
mkdir gen1
cat TEMPLATE_TEMP >gen1/r.in ; 
echo "nfiles " `wc -l phav.dat` >> gen1/r.in ; 
cat phav.dat >> gen1/r.in ; 
echo ; 
echo "****** ENDIF" >> gen1/r.in ; 
cat ../run.TEMPLATE  | sed -e s%BASE%BASE_FOLDER% | sed -e s%FOLDER%GEN_FOLDER_TEMP/gen1% > GEN_FOLDER_TEMP/gen1/run ;
./gendir.scr -l CERN -q QUEUE_TEMP -d 100 -i  `pwd` ; 
./submitfile

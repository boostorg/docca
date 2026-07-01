#!/bin/bash

date

echo "Copying docca XSLT files..." && \
cp ../include/docca/* build && \

echo "Copying shell scripts..." && \
cp extract-xml-pages.sh \
   assemble-quickbook.sh \
   execute-stages.sh execute-stage1.sh execute-stage2.sh \
build && \

cd build && \

echo "Calling extract-xml-pages.sh..." && \
./extract-xml-pages.sh && \

echo "Running execute-stages.sh..." && \
./execute-stages.sh && \

echo "Calling assemble-quickbook.sh..." && \
./assemble-quickbook.sh && \

echo "Calling the example build to run the Quickbook -> BoostBook -> DocBook -> HTML conversion..." && \
cd .. && \
../../../b2.exe

date

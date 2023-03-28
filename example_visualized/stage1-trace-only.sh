#!/bin/bash

date

echo "Copying docca XSLT files..." && \
cp ../include/docca/* build && \

echo "Copying shell scripts..." && \
cp extract-xml-pages.sh \
   assemble-quickbook.sh \
   prepare-stage1.sh trace-stage1.sh render-stage1.sh \
   execute-stage2.sh \
build && \

cd build && \

echo "Calling extract-xml-pages.sh..." && \
./extract-xml-pages.sh && \

echo "Running prepare-stage1.sh..." && \
./prepare-stage1.sh && \

echo "Running trace-stage1.sh..." && \
./trace-stage1.sh && \

echo "Running render-stage1.sh..." && \
./render-stage1.sh && \

echo "Running execute-stage2.sh..." && \
./execute-stage2.sh && \

echo "Calling assemble-quickbook.sh..." && \
./assemble-quickbook.sh && \

echo "Calling the example build to run the Quickbook -> BoostBook -> DocBook -> HTML conversion..." && \
cd .. && \
../../../b2.exe

date

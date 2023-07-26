!/bin/bash

: ${VISUALIZE:=0}

echo "Copying docca XSLT files..." && \
cp ../include/docca/* build

echo "Copying shell scripts..." && \
cp extract-xml-pages.sh \
   prepare.sh prepare-stage1.sh prepare-stage2.sh \
   trace.sh   trace-stage1.sh   trace-stage2.sh \
   render.sh  render-stage1.sh  render-stage2.sh \
   assemble-quickbook.sh \
build

if [ VISUALIZE != 0 ]; then
    echo "Copying xslt-visualizer..." && \
    rm -rf build/xslt-visualizer && \
    cp -r ../xslt-visualizer build
fi

if [ VISUALIZE = 2 ]; then
    echo "Copying stage2 parameters file..." && \
    cp stage2-params.xml build
fi

cd build && \

echo "Calling extract-xml-pages.sh..." && \
./extract-xml-pages.sh

echo "Removing previous stage1 results..."
rm -rf stage1_visualized/results
mkdir -p stage1_visualized/results

if [ VISUALIZE = 0 ]; then
    STAGE1_EXEC_PARAMS = -xsl:stage1.xsl
else
    # prepare-stage1.sh
    rm -rf stage1_visualized/code-trace-enabled
    java -cp "$CLASSPATH" net.sf.saxon.Transform -s:stage1.xsl -o:stage1_visualized/code-trace-enabled/stage1.xsl -xsl:xslt-visualizer/xsl/trace-enable.xsl

    STAGE1_EXEC_PARAMS = -xsl:xslt-visualizer/xsl/run-trace.xsl trace-enabled-stylesheet-uri=../../stage1_visualized/code-trace-enabled/stage1.xsl
fi

echo "Executing stage1..."
# echo "Tracing stage1..."
java -Xmx1024M -cp "$CLASSPATH" net.sf.saxon.Transform -threads:32 -s:xml-pages -o:stage1_visualized/results $STAGE1_EXEC_PARAMS

if [ VISUALIZE != 0 ]; then
    # render-stage1.sh
    mkdir -p stage1_visualized/visualized/assets
    cp -ru xslt-visualizer/assets/* stage1_visualized/visualized/assets

    echo "Rendering the stage1 visualization results"
    # Create the rendered results (Saxon forces .xml prefix in the output files)
    java -cp "$CLASSPATH" net.sf.saxon.Transform -threads:128 -s:stage1_visualized/results/trace-data -o:stage1_visualized/visualized -xsl:xslt-visualizer/xsl/render.xsl

    echo "Renaming the stage1 visualization files to .html"
    cd stage1_visualized/visualized
    for file in *.xml
    do
      mv "$file" "${file%.xml}.html"
    done
    cd ../..
fi

if [ VISUALIZE = 2 ]; then
    # prepare-stage2.sh
    rm -rf stage2_visualized/code-trace-enabled
    java -cp "$CLASSPATH" net.sf.saxon.Transform -s:stage2.xsl -o:stage2_visualized/code-trace-enabled/stage2.xsl -xsl:xslt-visualizer/xsl/trace-enable.xsl

    # trace-stage2.sh
    echo "Removing previous stage2 result traces..."
    rm -rf stage2_visualized/results/trace-data
    mkdir -p stage2_visualized/results

    echo "Tracing stage2..."
    java -Xmx1024M -cp "$CLASSPATH" net.sf.saxon.Transform -threads:32 -s:stage1_visualized/results -o:stage2_visualized/results -xsl:xslt-visualizer/xsl/run-trace.xsl trace-enabled-stylesheet-uri=../../stage2_visualized/code-trace-enabled/stage2.xsl '?transform-params=doc("stage2-params.xml")' principal-output-method=text

    echo "Copying the stage2 results to .txt files (for easier viewing in the browser)..."
    java -cp "$CLASSPATH" net.sf.saxon.Transform -s:xml-pages.xml -xsl:debug-friendly-quickbook.xsl input-dir=stage2_visualized/results >/dev/null

    # render-stage2.sh
    mkdir -p stage2_visualized/visualized/assets
    cp -ru xslt-visualizer/assets/* stage2_visualized/visualized/assets

    echo "Rendering the stage2 visualization results"
    java -cp "$CLASSPATH" net.sf.saxon.Transform -threads:128 -s:stage2_visualized/results/trace-data -o:stage2_visualized/visualized -xsl:xslt-visualizer/xsl/render.xsl

    echo "Renaming the stage2 visualization files to .html"
    cd stage2_visualized/visualized
    for file in *.xml
    do
      mv "$file" "${file%.xml}.html"
    done
fi

if [ VISUALIZE = 0 ]; then
    # execute-stage2.sh
    mkdir -p stage2

    echo "Executing stage2..."
    java -cp "$CLASSPATH" net.sf.saxon.Transform -threads:128 -s:stage1_visualized/results -o:stage2_visualized/results -xsl:stage2.xsl DEBUG=yes

    echo "Copying the stage2 results to .txt files (for easier viewing in the browser)..."
    java -cp "$CLASSPATH" net.sf.saxon.Transform -s:xml-pages.xml -xsl:debug-friendly-quickbook.xsl input-dir=stage2_visualized/results >/dev/null
fi

echo "Copying a manually-modified xml-pages.xml if present..."
cp ../xml-pages.xml .

echo "Assembling the stage2 results into reference.qbk"
java -cp "$CLASSPATH" net.sf.saxon.Transform -s:xml-pages.xml -xsl:assemble-quickbook.xsl -o:reference.qbk input-dir=stage2_visualized/results

echo "Copying reference.qbk..."
cp reference.qbk ..

echo "Calling the example build to run the Quickbook -> BoostBook -> DocBook -> HTML conversion..." && \
cd .. && \
../../../b2.exe

# Everything below tries to replicate what the b2.exe call does above
#echo "Copying reference.qbk into qbk..." && \
#cp ../reference.qbk ../qbk && \

#echo "Converting QuickBook (main.qbk) to BoostBook (beast_doc.xml)..." && \
#../../../../bin.v2/tools/quickbook/src/msvc-14.2/release/cxxstd-0x-iso/link-static/threading-multi/quickbook.exe --output-file=beast_doc.xml ../qbk/main.qbk && \

#echo "Converting BoostBook (beast_doc.xml) to DocBook (beast_doc.docbook)..." && \
#set XML_CATALOG_FILES=../../../../bin.v2/boostbook_catalog.xml && \
#/usr/bin/xsltproc --stringparam boost.defaults "Boost" --stringparam boost.root "../../../.." --stringparam chapter.autolabel "1" --stringparam chunk.first.sections "1" --stringparam chunk.section.depth "8" --stringparam generate.section.toc.level "8" --stringparam generate.toc "chapter toc,title section nop reference nop" --stringparam toc.max.depth "8" --stringparam toc.section.depth "8" --path "../../../../bin.v2" --xinclude -o beast_doc.docbook ../../../../tools/boostbook/xsl/docbook.xsl beast_doc.xml && \


#echo "Converting DocBook (beast_doc.docbook) to HTML..." && \
#set XML_CATALOG_FILES=../../../../bin.v2/boostbook_catalog.xml && \
#/usr/bin/xsltproc --stringparam boost.defaults "Boost" --stringparam boost.root "../../../.." --stringparam chapter.autolabel "1" --stringparam chunk.first.sections "1" --stringparam chunk.section.depth "8" --stringparam generate.section.toc.level "8" --stringparam generate.toc "chapter toc,title section nop reference nop" --stringparam manifest "beast_HTML.manifest" --stringparam toc.max.depth "8" --stringparam toc.section.depth "8" --path "../../../../bin.v2" --xinclude -o ../html/ ../../../../tools/boostbook/xsl/html.xsl beast_doc.docbook

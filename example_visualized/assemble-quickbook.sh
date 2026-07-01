echo "Copying a manually-modified xml-pages.xml if present..."
cp ../xml-pages.xml .

echo "Assembling the stage2 results into reference.qbk"
java -cp "$CLASSPATH" net.sf.saxon.Transform -s:xml-pages.xml -xsl:assemble-quickbook.xsl -o:reference.qbk input-dir=stage2_visualized/results

echo "Copying reference.qbk..."
cp reference.qbk ..

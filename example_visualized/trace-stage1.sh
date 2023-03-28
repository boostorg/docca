echo "Removing previous stage1 results..."
rm -rf stage1_visualized/results
mkdir -p stage1_visualized/results

echo "Tracing stage1..."
java -Xmx1024M -cp "$CLASSPATH" net.sf.saxon.Transform -threads:32 -s:xml-pages -o:stage1_visualized/results -xsl:xslt-visualizer/xsl/run-trace.xsl trace-enabled-stylesheet-uri=../../stage1_visualized/code-trace-enabled/stage1.xsl

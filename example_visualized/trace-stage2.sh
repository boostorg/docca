#rm -rf stage2_visualized/results

echo "Removing previous stage2 result traces..."
rm -rf stage2_visualized/results/trace-data
mkdir -p stage2_visualized/results

echo "Tracing stage2..."
java -Xmx1024M -cp "$CLASSPATH" net.sf.saxon.Transform -threads:32 -s:stage1_visualized/results -o:stage2_visualized/results -xsl:xslt-visualizer/xsl/run-trace.xsl trace-enabled-stylesheet-uri=../../stage2_visualized/code-trace-enabled/stage2.xsl '?transform-params=doc("stage2-params.xml")' principal-output-method=text

echo "Copying the stage2 results to .txt files (for easier viewing in the browser)..."
java -cp "$CLASSPATH" net.sf.saxon.Transform -s:xml-pages.xml -xsl:debug-friendly-quickbook.xsl input-dir=stage2_visualized/results >/dev/null

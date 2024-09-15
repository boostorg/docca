mkdir -p stage2

echo "Executing stage2..."
java -cp "$CLASSPATH" net.sf.saxon.Transform -threads:128 -s:stage1_visualized/results -o:stage2_visualized/results -xsl:stage2.xsl DEBUG=yes

echo "Copying the stage2 results to .txt files (for easier viewing in the browser)..."
java -cp "$CLASSPATH" net.sf.saxon.Transform -s:xml-pages.xml -xsl:debug-friendly-quickbook.xsl input-dir=stage2_visualized/results >/dev/null

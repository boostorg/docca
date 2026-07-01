mkdir -p stage1_visualized/results

echo "Executing stage1..."
java -cp "$CLASSPATH" net.sf.saxon.Transform -threads:128 -s:xml-pages -o:stage1_visualized/results -xsl:stage1.xsl

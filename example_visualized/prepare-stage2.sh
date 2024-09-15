rm -rf stage2_visualized/code-trace-enabled
java -cp "$CLASSPATH" net.sf.saxon.Transform -s:stage2.xsl -o:stage2_visualized/code-trace-enabled/stage2.xsl -xsl:xslt-visualizer/xsl/trace-enable.xsl

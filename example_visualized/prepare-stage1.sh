rm -rf stage1_visualized/code-trace-enabled
java -cp "$CLASSPATH" net.sf.saxon.Transform -s:stage1.xsl -o:stage1_visualized/code-trace-enabled/stage1.xsl -xsl:xslt-visualizer/xsl/trace-enable.xsl

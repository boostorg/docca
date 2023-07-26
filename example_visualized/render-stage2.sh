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

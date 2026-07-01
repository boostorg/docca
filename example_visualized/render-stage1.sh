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

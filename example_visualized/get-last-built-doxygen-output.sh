echo "Removing a previous build dir, if it exists..."
rm -rf build
mkdir build

echo "Attempting to copy the Doxygen output from the last 'example' build; you likely will need to modify my hard-coded source directory..."
cp ../../../bin.v2/tools/docca/example/*.xml build

echo "Copying custom-overrides.xsl from the build directory..."
cp ../../../bin.v2/tools/docca/example/custom-overrides.xsl build

echo "Adding a customizable copy of index.xml to example_visualized/custom-index.xml..."
cp build/index.xml custom-index.xml

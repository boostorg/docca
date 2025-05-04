echo "Wiping out previous visualizer build results..."
cat .gitignore | xargs rm -r

echo "Getting last-built Doxygen output..."
./get-last-built-doxygen-output.sh &&

echo "Getting qbk pages..."
./get-qbk-pages.sh &&

./run-all.sh


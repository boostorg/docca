The bash scripts in this directory are here for two main purposes:

 1. generating the XSLT visualizations for both stages of page rendering (from XML to XML to QuickBook), and
 2. supporting partial builds (to enable faster iterations for development).

# Architectural Overview
The Boost.Build-based Jamfile in the regular "example" build is sufficient to build all of the HTML
docs using the new XSLT code. It has several phases of processing, each using Saxon-HE:

 1. **extract-xml-pages.xsl**:
    Generate XML page source files, discovered using Doxygen's index.xml.
    This yields a subset of Doxygen's output for each page, gathering together just the info
    needed for that page (along with some annotations like link refids), but otherwise leaving its
    Doxygen-based format unchanged.
 2. **stage1.xsl**:
    Transform each Doxygen-style XML page into a simpler XML page format tailored towards the
    structure and features of the HTML page it will eventually produce.
 3. **stage2.xsl**:
    Transform each tailored XML page into QuickBook format.
 4. **assemble-quickbook.xsl**:
    Gather together all the individual Quickbook-formatted results into a single reference.qbk file,
    which is used by the rest of the build to weave them into the QuickBook->BoostBook->DocBook->HTML process.

These same steps are used in both the "example" and "example_visualized" builds. The difference is that the
latter also includes visualizations, and it uses bash shell scripts to drive the whole thing, including
the part that still depends on Boost.Build (the QuickBook->BoostBook->DocBook->HTML process, defined in
example_visualized/Jamfile).

For a summary of what transient files are used in the example_visualized build (including ones you edit to
configure a partial build), see the .gitignore file in this directory, which also includes comments
explaining each entry.

# Setup (two scripts)
The initial setup depends on the "example" build, first to get the XML files generated by Doxygen,
and second, to simply copy the original qbk and images directories. These steps are independent
of each other, but both of them must be run.

## Getting the Doxygen output
For initial setup, after running a full "example" build (i.e. in boost/tools/docca/example), run the
following script:

  * ./get-last-built-doxygen-output.sh

It will blow away the example_visualized/build directory (if it exists) and create a new one,
populated with all the XML files output by Doxygen, including index.xml. Additionally, it will
copy index.xml to example_visualized/custom-index.xml (which you can customize for partial builds).
If the script fails, you probably will need to modify it, specifically the hard-coded path of
the build dir used by Boost.Build for the regular "example" build.

[FIXME: Don't hard-code the build directory for the "example" build...]

## Copying the manually-authored QuickBook
You also need a copy of the qbk and images directories. Run this script to get those:

 * ./get-qbk-pages.sh


# Running a build (one master script)
Once you've successfully run the above setup scripts, you can now run a full build of all of the pages,
including both the HTML results and the visualizations, by executing this command:

 * ./run-all.sh

The HTML results will appear in the "html" directory, and the XSLT visualizations will appear in
subdirectories of the build directory. To find them, understand that a DEBUG option is set (enabled
in the relevant script, trace.sh, which is automatically invoked by run-all.sh) and which causes
every HTML page in the result to include links (immediately following the page's "brief description")
to both of the XSLT visualizations for that page. When reviewing an HTML page in the browser, look
for the links called "stage1_visualized" and "stage2_visualized". Clicking these will yield the
relevant visualizations for that page. You can use this to better understand how the two stages of
XSLT are used to generate the QuickBook, which can also be helpful for debugging.

NOTE: The stage-two visualizations have become the most time-consuming to generate. For most use cases,
I suspect that ./non-traced-build.sh or ./stage1-trace-only.sh is what you will want to invoke instead of
./run-all.sh (see the sections about this below).

## Running a partial build (editing custom-index.xml)
If you want to only do a partial build, edit the custom-index.xml in the example_visualized directory
and then comment out everything but the pages you want to include in the build. The
extract-xml-pages.sh script (invoked automatically by run-all.sh) will overwrite build/index.xml with your
modified custom-index.xml, using it as input instead. (For that reason, you may want to comment things out so you
can easily uncomment them later, without having to retrieve the Doxygen output again.) After you've created
your pared-down custom-index.xml, simply run run-all.sh again to generate only those pages.

## Including previously-built pages in the HTML output
The aforementioned extract-xml-pages.sh script generates all of the input XML "page" files that are
used as input to stage 1 of the page rendering. It also generates a hierarchical list of pages
in build/xml-pages.xml. This, in turn, is used by assemble-quickbook.sh (automatically invoked by run-all.sh),
to pull all of the reference pages (rendered as QuickBook) together into reference.qbk. If you want to
include previously-built reference pages into reference.qbk even after switching to a different partial
build (by editing your custom-index.xml), you can do this by also supplying a custom xml-pages.xml file
in the example_visualized directory (e.g. the result of a full build from earlier, at build/xml-pages.xml).
The assemble-quickbook.sh script will overwrite build/xml-pages.xml with your modified xml-pages.xml,
using it as input instead. (Unlike build/index.xml, build/xml-pages.xml gets regenerated every time you run run-all.sh.)
The purpose of doing this would be, for example, to always get a full build of the HTML docs (for example,
to test links between all the pages) without having to rebuild the QuickBook (and XSLT visualizations)
for all the reference pages every time.

However, if you want the fastest build possible (to repeatedly render just a subset of the reference pages),
you're best off not using a custom xml-pages.xml file. Just whittling down custom-index.xml to a small subset will
give you the fastest build.

# Running a build without visualizations (one master script)
As a way of speeding things up further, you can run a build that includes everything but the visualizations
(which is the most time-consuming thing to generate). To do this, simply run:

 * ./non-traced-build.sh

in lieu of run-all.sh. The technique for doing partial builds still applies to this build script as well.

# Running a build with visualizations for stage one only (one master script)
As a compromise, you can run a build that includes everything but the stage-two visualization
(which is the most time-consuming thing to generate). To do this, simply run:

 * ./stage1-trace-only.sh

in lieu of run-all.sh. The technique for doing partial builds still applies to this build script as well.
#!/bin/sh

filename=$1
exports=`grep "^environment=" $filename | sed "s/^environment=//" | sed "s/,\s*/  /g"`
echo "======================================================="
echo "Debugging $filename"
echo "======================================================="
echo "Loading exports:"
for e in $exports
do
	echo export $e
	export $e
done
com=`grep "command" $filename | sed "s/^command=//"`
dire=`grep "directory" $filename | sed "s/^directory=//"`
echo Running command: $com
echo PWD=$dire
echo "======================================================="
#export PWD=$dire
cd $dire
$com

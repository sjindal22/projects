#!/bin/bash
echo "This script will exit with a 0 exit status"
EXIT_STATUS=$?

if [ "$EXIT_STATUS" -ne "0" ]
then
	echo "The script did not return a 0 status code"
fi



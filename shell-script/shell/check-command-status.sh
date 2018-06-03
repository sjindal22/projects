#!/bin/bash

cat /etc/shadow
EXIT_STATUS=$?
if [ "$EXIT_STATUS" -ne "0" ]
then 
	echo "Command failed"
	exit 1
else
	echo "Command succeeded"
	exit 0
fi


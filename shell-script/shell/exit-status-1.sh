#!/bin/bash

HOST="google.com"
ping -c 1 $HOST
EXIT_STATUS=$?

if [ "$EXIT_STATUS" -ne "0" ]
then
	echo "$HOST unreachable"
fi




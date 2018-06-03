#!/bin/bash

function echo-names() {
	for NAME in $@
	do 
		echo "Hi $NAME!"
		echo "Time now is $(date +%r)"
	done
}

echo-names Shivika Ryan Andy

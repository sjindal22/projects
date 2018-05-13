#!/bin/bash

read -p "Enter the name of file or directory: " FILE

if [ -f "$FILE" ]
then
    echo "${FILE} is a type of regular file"

elif [ -d "$FILE" ]
then
    echo "${FILE} is a type of directory"

else
    echo "It is netiher of file or directory type"
fi

ls -l $FILE

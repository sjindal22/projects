#!/bin/bash

# When you have to prompt to user for the input
# read -p "Enter the name of file or directory: " FILE

#When you the script to accept variable as an argument
#FILE=$1

#When you the script to accept unlimited variables as an argument
for FILE in $@
do 
    if [ -f "$FILE" ]
    then
        echo "${FILE} is a type of regular file"

    elif [ -d "$FILE" ]
    then
        echo "${FILE} is a type of directory"

    else
        echo "It is neither of file or directory type"
    fi
done

ls -l $FILE

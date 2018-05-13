#!/bin/bash

FILES=$(ls ~/| grep txt)
DATE = $(date +%f)

for file in $FILES

do 
   echo "Renaming ${file} to ${DATE}-${file}"
   mv ${FILES} ${DATE}-${file}
done

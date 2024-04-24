#!/bin/bash

# check if the path is current directory or a parent directory

if [ -f ./update_subnet.sh ]; then
    echo "calling from scripts directory"
    cd ..
fi

echo $(pwd)

git reset --hard
git pull
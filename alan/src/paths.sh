#!/bin/bash

gitdir=$(git rev-parse --show-toplevel) 
mydir='/alan/'
gitdir=$gitdir$mydir

sed_str="s|{gitdir}|${gitdir}|"
echo $sed_str

sed $sed_str <$gitdir/src/mysql/load_CAMEO.raw >$gitdir/src/mysql/load_CAMEO.mysql

pathfile='src/pypaths.py'

echo "project_path='$gitdir'">$gitdir$pathfile

if [[ ":$PYTHONPATH:" == *":$gitdir:"* ]]; then
  echo "Your path is correctly set"
else
  echo "Your PYTHONPATH is missing $gitdir, add it now!!!"
  echo "Add $gitdir to your PYTHONPATH in .bashrc for the future!"
fi

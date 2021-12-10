#!/bin/bash

cd ~

# clone repo
git clone git@github.com:xicodomingues/francinette.git francine

cd ~/francinette

# start a venv inside francinette
python3 -m venv .

# activate venv
source /venv/bin/activate

# install requirements
pip3 install --yes -r requirements.txt

# set up the alias
grep "francinette" ~/.zshrc &> /dev/null
if [[ $? != 0 ]]; then
	echo "not present"
	echo "\nalias francinette=~/francinette/tester.sh" >> ~/.zshrc
fi

# print help
~/francinette/tester.sh

echo "Please close this terminal windown and open it again"
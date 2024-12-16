#!/bin/bash

echo waiting for docker to initialise
sleep 10

echo starting screen
Xvfb :0 -screen 0 1024x768x16 &
export DISPLAY=:0.0 # Select screen 0.
sleep 10

echo installing python
wine python-3.12.8.exe /quiet PrependPath=1
sleep 10

echo installing python dependencies
wine python.exe -m pip install -r requirements.txt
sleep 10

echo exiting

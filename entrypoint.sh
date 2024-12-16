#!/bin/bash

echo waiting for docker to initialise
sleep 10

echo starting screen
Xvfb :1 -screen 1 1024x768x16 &
export DISPLAY=:1.1 # Select screen 0.
sleep 10

echo starting wine
wine "python.exe pactest.py example.pac google.com"
sleep 10

echo exiting

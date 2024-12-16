#!/bin/bash

Xvfb :0 -screen 0 1024x768x16 &
export DISPLAY=:0.0 # Select screen 0.
sleep 30
echo starting wine
#WINEARCH=win32 wine /app/python/python.exe -m pip install &> output01.txt
#WINEARCH=win32 wine /app/python/python.exe pactest.py example.pac google.com &> output02.txt


wine /app/python/python.exe -m pip install -r requirements.txt &> output01.txt

wine /app/python/python.exe pactest.py example.pac google.com &> output02.txt

echo finished running wine
cat output01.txt
cat output02.txt

sleep 1200

#!/bin/bash

echo waiting for docker to initialise
sleep 10

echo starting wine
xvfb-run wine python.exe pactest.py example.pac google.com
sleep 10

echo exiting

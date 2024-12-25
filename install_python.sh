#!/bin/bash

echo waiting for docker to initialise
sleep 10

echo installing python
xvfb-run wine python-3.12.8.exe /quiet PrependPath=1
sleep 10

echo installing python dependencies
xvfb-run wine python.exe -m pip install -r requirements.txt
sleep 10

echo exiting

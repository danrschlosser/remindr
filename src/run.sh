#!/bin/bash

cd ..
grunt noSass
source bin/activate
source src/config/test_config.sh
python src/app.py


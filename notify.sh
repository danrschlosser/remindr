#!/bin/bash

cd github/remindr

source bin/activate
source src/config/deploy_config.sh
python src/notify.py

date >> log.txt


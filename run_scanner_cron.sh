#!/bin/bash
# Script to run the Market Scanner automatically from terminal or cron
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
source venv/bin/activate
python3 main.py --scan

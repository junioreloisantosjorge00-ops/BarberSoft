#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install flask
(sleep 2; open http://127.0.0.1:5000) &
python3 app.py

#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
pip install flask
pip install openai -q
pip install openai
pip install pandas
pip install plotly
pip install scikit-learn
pip install scipy
pip install pyrebase
pip install pyrebase4
pip install matplotlib
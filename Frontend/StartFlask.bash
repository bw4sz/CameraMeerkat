#! /bin/bash 

export FLASK_APP="$(pwd)/autoapp.py"
export FLASK_DEBUG=1
export CAMERAMEERKAT_SECRET='Simon'

flask run
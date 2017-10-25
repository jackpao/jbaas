#!/bin/bash


echo "export Flask APP variable to hello.py"

export FLASK_APP=hello.py

echo "The run flask"

flask run --host=0.0.0.0

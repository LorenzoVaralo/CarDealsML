#!/bin/bash

echo "Model inference Pipeline"

python dataClean.py --inference True
echo "------------------------------"

python NLPformater.py
echo "------------------------------"

python model_inference.py

echo "✔"

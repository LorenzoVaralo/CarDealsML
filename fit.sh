#!/bin/bash

echo "Model training Pipeline"

python dataClean.py
echo "------------------------------"

python NLPformater.py --fit True
echo "------------------------------"

python train.py
echo "------------------------------"

python compareModels.py

echo "✔"
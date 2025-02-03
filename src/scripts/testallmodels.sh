#!/usr/bin/env bash

file1=$(tail -n 1 < python ./ollama_topic_classification.py -m mistral -v 2)
file2=$(tail -n 1 < python ./ollama_topic_classification.py -m llama3.2:1b -v 2)
file3=$(tail -n 1 < python ./ollama_topic_classification.py -m llama3.2 -v 2)

python ./evaluate.py -f "$file1"
python ./evaluate.py -f "$file2"
python ./evaluate.py -f "$file3"

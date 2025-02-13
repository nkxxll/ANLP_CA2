#!/usr/bin/env bash

# python3 ./ollama_topic_classification.py -m mistral -v 3 -n 5
# python3 ./ollama_topic_classification.py -m llama3.2:1b -v 3 -n 5
# python3 ./ollama_topic_classification.py -m llama3.2 -v 3 -n 5
# python3 ./ollama_topic_classification.py -m llama3.2 -v 3 -n 5
# python3 ./ollama_topic_classification.py -m llama3.2 -v 3 -n 5
# python3 ./ollama_topic_classification.py -m llama3.2 -v 3 -n 5

# python3 ./ollama_topic_classification.py -m mistral -v 3
python3 ./ollama_topic_classification.py -m llama3.2:1b -v 3
python3 ./ollama_topic_classification.py -m llama3.2 -v 3
python3 ./ollama_topic_classification.py -m deepseek-r1:7b -v 3
python3 ./ollama_topic_classification.py -m deepseek-r1:1.5b -v 3

#!/bin/bash

pip install -r /path/to/requirements.txt
python -m spacy download ru_core_news_sm

uvicorn main:app
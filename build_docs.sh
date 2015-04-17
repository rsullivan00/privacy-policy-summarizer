#!/bin/bash

NLTK_VERSION=$(python3 -c 'import nltk; print(nltk.__version__)')
NLTK_URL=$(python3 -c 'import nltk; print(nltk.__url__)')
EPYDOC_OPTS = --name=nltk --navlink="nltk ${NLTK_VERSION}"\
              --url=${NLTK_URL} --inheritance=listed --debug

# Rebuild from scratch
[[ -e ~/python-nltk-docs ]] && rm -rf ~/python-nltk-docs

mkdir ~/python-nltk-docs
epydoc ${EPYDOC_OPTS} -o ~/python-nltk-docs ~/nltk_data
#/usr/share/pyshared/nltk

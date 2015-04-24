#!/usr/bin/env bash

# Check code guidelines
echo -e '\e[32mChecking for code style errors \e[0m'
if ! flake8 *.py; then
    exit 1
fi

echo -e '\e[36mAll tests completed successfully\e[0m'

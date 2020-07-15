#!/bin/bash
until python -m bot 2>error_text; do
    sleep 5
done

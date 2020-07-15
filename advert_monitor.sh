#!/bin/bash
until python -m adbot 2>error_text; do
    sleep 5
done

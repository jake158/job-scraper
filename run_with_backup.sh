#!/bin/bash

mkdir -p backups
rm -rf backups/*

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

if [ -f "seen.csv" ]; then
    cp seen.csv "backups/seen_$TIMESTAMP.csv"
    echo "Backed up seen.csv to backups/seen_$TIMESTAMP.csv"
else
    echo "seen.csv does not exist, skipping backup for seen.csv"
fi

if [ -f "new_jobs.csv" ]; then
    cp new_jobs.csv "backups/new_jobs_$TIMESTAMP.csv"
    echo "Backed up new_jobs.csv to backups/new_jobs_$TIMESTAMP.csv"
else
    echo "new_jobs.csv does not exist, skipping backup for new_jobs.csv"
fi

echo "Running scraper..."
python3 main.py
echo "Scraper run over."

echo "Opening GUI"
python3 gui.py

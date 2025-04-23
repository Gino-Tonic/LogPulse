README.md

# A simple log analysis tool using python

Features
- time-based frequency analysis of entries in a log file
- Optional: Exports matched entries JSON export

### Usage
`python3 logpulse.py --log ./sample_logs/auth.log --threshold 5 --json logpulse.json`

    --log Path to the log file 
    --threshold of entries per minute e.g. 60
    --json Optional: output matched log entries to a JSON file


MIT License – do whatever...
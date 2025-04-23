#!/usr/bin/env python3

import argparse
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict

buckets = defaultdict(list)


def parse_log_file(log_path: str, threshold: int) -> list:
    matches = []
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                timestamp_str = line.split()[0]
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
                
                bucket = timestamp.replace(second=0, microsecond=0) # Round down to the nearest minute
                bucket_key = bucket.strftime("%Y-%m-%d %H:%M") #Convert to string if you want cleaner display

                #add to bucket
                buckets[bucket_key].append(line.strip())
                

        for time, lines in sorted(buckets.items()):
            logging.debug(f"{time} → {len(lines)} entries")


    # Error handling in file reading
    except FileNotFoundError:
        logging.error(f"File not found: {log_path}")
    except PermissionError:
        logging.error(f"Permission denied: {log_path}")
    except IsADirectoryError:
        logging.error(f"Expected a file but found a directory: {log_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    # Check if any bucket exceeds the threshold
    for time, lines in buckets.items():
        if len(lines) >= threshold:
            matches.append({
                "timestamp": time,
                "count": len(lines),
                "log_lines": lines
            })  
            logging.info(f"Alert! {len(lines)} entries in {time}")
    return matches


def save_to_json(matches: list, output_path: str) -> None:
    if not matches:
        logging.warning(f"No matches found.")
        return
    try:
        with open(output_path, 'w') as f:
            json.dump(matches, f, indent=4)
        logging.info(f"{len(matches)} results saved to {output_path}")
    except Exception as e:
        logging.error(f"Failed to write to JSON: {e}")

def main():
    parser = argparse.ArgumentParser(description="LogSniff - Simple Log Parser")
    parser.add_argument('--log', required=True, help="Path to the log file")
    parser.add_argument('--threshold', type=int, default=10, help="entries per minute to trigger alert")
    parser.add_argument('--json', help="Optional: output matched lines to a JSON file")
    parser.add_argument('--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level (default: INFO)")
    args = parser.parse_args()

    #Config logging level 
    logging.basicConfig(level=getattr(logging, args.loglevel), format='[%(levelname)s] %(message)s')

    logging.info(f"Scanning {args.log} with threshold: {args.threshold} entries per minute")
    matches = parse_log_file(args.log, args.threshold)

    if args.json and matches:
        save_to_json(matches, args.json)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import json
import os
import sys

STATUS_FILE = '/statuses.json'


def load_statuses():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {"Frank": "Unknown", "Jacob": "Unknown"}


def save_statuses(statuses):
    with open(STATUS_FILE, 'w') as f:
        json.dump(statuses, f)
        f.write('\n')


def print_usage():
    print('Usage: python update_status.py <person> <status>')
    print('Example: python update_status.py Jacob Away')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    person = sys.argv[1]
    status_value = sys.argv[2]

    statuses = load_statuses()
    if person not in statuses:
        print(f'Invalid person: {person}')
        print('Valid people:', ', '.join(statuses.keys()))
        sys.exit(1)

    statuses[person] = status_value
    save_statuses(statuses)
    print(f'Updated {person} to {status_value}')

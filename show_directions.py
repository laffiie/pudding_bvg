#!/usr/bin/env python3
"""
Shows all unique directions for a station to help configure filters
"""
import sys
import json
from bvg_api import BVGClient

def show_directions(station_id: str):
    """Shows all unique line + direction combinations"""
    client = BVGClient()
    print(f"Fetching departures for station {station_id}...\n")
    
    departures = client.get_departures(station_id, duration=120)
    
    if not departures:
        print("❌ No departures found or API error")
        return
    
    # Group by line and direction
    line_directions = {}
    for dep in departures:
        line = dep['line']
        direction = dep['direction']
        key = f"{line}"
        
        if key not in line_directions:
            line_directions[key] = set()
        line_directions[key].add(direction)
    
    print("📊 Available Lines and Directions:\n")
    for line in sorted(line_directions.keys()):
        print(f"  Line {line}:")
        for direction in sorted(line_directions[line]):
            print(f"    → {direction}")
        print()
    
    print("💡 To filter by direction, use 'excludeDirections' in config.json (per station)")
    print("   Example: \"excludeDirections\": [\"Nordbahnhof\", \"Alexanderplatz\"]")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Load from config.json
        try:
            with open('config/config.json', 'r') as f:
                config = json.load(f)
            station_id = config['stations'][0]['id']
            print(f"Using first station from config: {config['stations'][0]['name']}\n")
        except Exception as e:
            print("Usage: python3 show_directions.py <station_id>")
            print("   or: python3 show_directions.py  (uses first station from config)")
            sys.exit(1)
    else:
        station_id = sys.argv[1]
    
    show_directions(station_id)

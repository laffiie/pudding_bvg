# BVG Departure Monitor

Real-time BVG departure display built with Pygame. Shows live departures, delays, and disruptions for configured stations. Designed for Raspberry Pi but runs on any desktop too.

Uses the public [BVG REST API](https://v6.bvg.transport.rest).

## What it does

- Live departures for 1–2 stations, auto-refreshing
- Color-coded times: green (plenty of time), yellow (tight), red (too late) — based on your walking time
- Disruption banners with scrolling text when alerts are active
- Delay indicators per departure
- Filters by line and direction

## Quick start

### 1. Install dependencies

```bash
pip3 install -r requirements.txt
```

On Raspberry Pi you also need SDL2:
```bash
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

Or use the automated Pi setup: `./install_pi.sh`

### 2. Find your station IDs

```bash
python3 find_station.py "Alexanderplatz"
```

### 3. Create your config

Copy the example and edit it:
```bash
cp config.example.json config/config.json
```

Example config:
```json
{
  "stations": [
    {
      "id": "900100003",
      "name": "S+U Alexanderplatz",
      "walkingTime": 5,
      "lines": ["M4", "U2"],
      "excludeDirections": ["Warschauer Str."]
    }
  ],
  "refreshInterval": 30,
  "maxDepartures": 6,
  "displayWidth": 800,
  "displayHeight": 480,
  "fullscreen": false
}
```

**Station fields:**
- `id` — Station ID from `find_station.py`
- `walkingTime` — Minutes to walk there (determines the color coding)
- `lines` — Optional filter, empty = all lines
- `excludeDirections` — Optional list of destinations to hide

**Display fields:**
- `refreshInterval` — Seconds between API calls (default 30)
- `maxDepartures` — Max departures shown per station
- `displayWidth` / `displayHeight` — Window size in pixels
- `fullscreen` — Fullscreen mode
- `testMode` — Injects fake disruptions for testing

### 4. Run

```bash
python3 main.py ./config/config.json
```

Press `q` or `Esc` to quit.

## Raspberry Pi deployment

For always-on operation, run as a systemd service:

```bash
sudo cp bvg-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now bvg-display.service
```

Useful commands:
```bash
sudo systemctl status bvg-display.service   # check status
sudo journalctl -u bvg-display.service -f    # tail logs
sudo systemctl restart bvg-display.service   # restart
```

Run `./disable_screen_blanking.sh` to prevent the display from sleeping.

### Docker

```bash
docker build -t bvg-monitor .
docker run -d --device /dev/vchiq --device /dev/fb0 -v $(pwd)/config:/app/config bvg-monitor
```

## Utilities

- `find_station.py` — Look up station IDs by name
- `show_directions.py` — List all lines/directions for a station (helps configure filters)
- `validate_config.py` — Check your config for errors
- `test_local.py` — Quick local test

## License

MIT

# 🚊 BVG Abfahrtsmonitor

A real-time departure display for Berlin's public transport (BVG) that runs on a Raspberry Pi with a connected screen. Perfect for mounting near your door!

![BVG Display](https://img.shields.io/badge/Platform-Raspberry%20Pi-red)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🚇 **Real-time departures** from 1-2 BVG stations
- 🚶 **Walking time consideration** - color-coded timing
- ⏱️ **Delay display** - shows +/- minutes
- ⚠️ **Disruption warnings** - stay informed
- 🎨 **Minimalist design** - easy to read at a glance
- 📱 **Remote management** - configure via SSH
- 🔄 **Auto-start on boot** - always running
- 💪 **Pi Zero optimized** - runs smoothly even on limited hardware

## 🚀 Quick Start

### Raspberry Pi Deployment (Fastest)

```bash
# 1. From your Mac/Linux, copy to Pi
./deploy_to_pi.sh

# 2. SSH to Pi
ssh pi@raspberrypi.local

# 3. Run setup
cd ~/bvg_abfahrt
./install_pi.sh

# 4. Edit your stations
nano config/config.json

# 5. Test it
python3 main.py ./config/config.json

# 6. Enable auto-start
sudo systemctl enable bvg-display.service
sudo systemctl start bvg-display.service

# 7. Disable screen blanking
./disable_screen_blanking.sh
sudo reboot
```

### Local Testing (Mac/Linux/Windows)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Find your station IDs
python3 find_station.py "Alexanderplatz"

# Configure
cp config.example.json config/config.json
nano config/config.json

# Test
python3 main.py ./config/config.json
```

### Using Make Commands

```bash
make help           # Show all commands
make find-station STATION="Your Station"
make validate       # Check config
make deploy         # Deploy to Pi
make logs          # View logs (on Pi)
make restart       # Restart service (on Pi)
```

## 📁 Project Structure

```
pudding_bvg/
├── main.py                      # Main application
├── bvg_api.py                   # BVG API client
├── display.py                   # Display manager (pygame)
├── find_station.py              # Station ID finder tool
├── validate_config.py           # Config validator
├── requirements.txt             # Python dependencies
├── config/
│   ├── config.json              # Your configuration
│   └── config.example.json      # Example configuration
├── install_pi.sh                # Pi setup script
├── deploy_to_pi.sh              # Deploy from Mac/Linux to Pi
├── disable_screen_blanking.sh   # Prevent screen sleep
└── README.md                    # This file (complete documentation)
```

## ⚙️ Configuration

Edit `config/config.json`:

```json
{
  "stations": [
    {
      "id": "900131508",
      "name": "Friedrich-Engels-Str./Eichenstr.",
      "walkingTime": 5,
      "excludeDirections": [],
      "lines": ["M1"]
    }
  ],
  "refreshInterval": 30,
  "displayLines": [],
  "maxDepartures": 6,
  "displayWidth": 800,
  "displayHeight": 480,
  "fullscreen": true,
  "testMode": false
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `stations` | List of stations to display | `[]` |
| `stations[].excludeDirections` | Hide departures to these destinations (per station) | `[]` |
| `stations[].lines` | Show only these lines (per station) | `[]` |
| `refreshInterval` | Seconds between API updates | `30` |
| `displayLines` | Filter specific lines (global, empty = all) | `[]` |
| `maxDepartures` | Max departures per station | `6` |
| `displayWidth` | Screen width in pixels | `800` |
| `displayHeight` | Screen height in pixels | `480` |
| `fullscreen` | Fullscreen mode | `false` |
| `testMode` | Show test data | `false` |

### Finding Station IDs

```bash
python3 find_station.py "Alexanderplatz"
```

### Finding Direction Names

To see what actual direction names the API returns for your station:

```bash
python3 show_directions.py
# or
python3 show_directions.py 900131508
```

This shows all lines and their destinations, helping you decide what to filter.

### Filtering by Line (Per Station)

You can also specify exactly which lines to show for each station:

```json
{
  "stations": [
    {
      "id": "900131508",
      "name": "Friedrich-Engels-Str./Eichenstr.",
      "lines": ["M1", "247"]
    }
  ]
}
```

This is useful if a station serves many lines (like Alexanderplatz) but you only care about specific ones.

### Filtering by Direction (Exclude Mode)

Since the BVG API only provides **final destinations** (not intermediate stops), you can filter by **excluding** unwanted directions at each station:

```json
{
  "stations": [
    {
      "id": "900131508",
      "name": "Friedrich-Engels-Str./Eichenstr.",
      "walkingTime": 5,
      "excludeDirections": ["Rosenthal Nord"]
    }
  ]
}
```

**How it works:**
- Uses **case-insensitive partial matching** - "rosenthal" matches "Rosenthal Nord"
- **Per-station filtering** - each station can have different filters
- **Exclude mode** - hide specific directions, show everything else
- Multiple keywords = hide departures matching **any** keyword
- Empty array = show all directions

**Example Use Cases:**

1. **Show only city-bound trams (exclude outbound):**
   ```json
   {
     "id": "900131508",
     "excludeDirections": ["Rosenthal Nord"]
   }
   ```
   This hides M1 trams going to Rosenthal Nord, showing only those heading towards the city center (S Hackescher Markt direction).

2. **Different filters per station:**
   ```json
   {
     "stations": [
       {
         "id": "900131508",
         "excludeDirections": ["Rosenthal"]
       },
       {
         "id": "900131526",
         "excludeDirections": ["Hackescher"]
       }
     ]
   }
   ```
   First station shows only city-bound, second shows only outbound.

3. **Exclude multiple unwanted destinations:**
   ```json
   {
     "excludeDirections": ["Rosenthal", "Wittenau", "Hermsdorf"]
   }
   ```

💡 **Tip:** Run `python3 show_directions.py` first to see actual destination names, then add the ones you DON'T want to see!

## 🎨 Color Coding

The display uses colors to show timing relative to walking time:

- 🟢 **Green** - More time than walking time (comfortable)
- 🟡 **Yellow** - Exactly walking time (on the dot)
- 🔴 **Red** - Less than walking time (too tight) or "jetzt"
- 🟠 **Orange** - Disruption warning

## 🖥️ Hardware Requirements

### Recommended
- **Raspberry Pi Zero 2W** (or any Pi model)
- **7" Display** (800×480 HDMI/DSI touchscreen)
- **Power Supply** (5V 2.5A official)
- **MicroSD Card** (16GB+)

### Also Works With
- Raspberry Pi 3/4/5
- Any HDMI display
- Desktop computers (Mac/Linux/Windows with pygame)

## 📊 Performance

| Device | Performance | Notes |
|--------|-------------|-------|
| Pi Zero 2W | Good ✅ | Recommended, smooth at 30s refresh |
| Pi Zero | Acceptable ⚠️ | Use 60s refresh, 1 station |
| Pi 3/4/5 | Excellent ✅ | Overkill but works great |
| Desktop | Excellent ✅ | Perfect for testing |

## 🔧 Maintenance

### View Logs
```bash
sudo journalctl -u bvg-display.service -f
```

### Restart Service
```bash
sudo systemctl restart bvg-display.service
```

### Update Config
```bash
nano ~/bvg_abfahrt/config/config.json
sudo systemctl restart bvg-display.service
```

### Deploy Updates
```bash
# From your Mac/Linux
./deploy_to_pi.sh
ssh pi@raspberrypi.local 'sudo systemctl restart bvg-display.service'
```

## 🍓 Raspberry Pi Setup

### Prerequisites
- Raspberry Pi Zero 2W (or any Pi model)
- MicroSD card with Raspberry Pi OS
- Display (HDMI/DSI, 800×480 recommended)
- Internet connection

### Manual Setup

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install system packages
sudo apt-get install -y \
    python3-pip python3-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libfreetype6-dev libportmidi-dev libjpeg-dev unclutter

# 3. Install Python packages (in virtual environment)
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# 4. Add user to video group
sudo usermod -a -G video $USER
```

### Common Screen Resolutions
- Official 7" Touchscreen: 800×480
- Small HDMI: 1024×600, 1280×720
- Full HD: 1920×1080

## 🔄 Auto-Start Setup

### Create Systemd Service

```bash
sudo nano /etc/systemd/system/bvg-display.service
```

Add (replace `USERNAME` with your actual username, e.g., `pi`):

```ini
[Unit]
Description=BVG Abfahrtsmonitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=USERNAME
WorkingDirectory=/home/USERNAME/bvg_abfahrt
Environment=DISPLAY=:0
Environment=SDL_VIDEODRIVER=x11
ExecStart=/home/USERNAME/bvg_abfahrt/.venv/bin/python3 /home/USERNAME/bvg_abfahrt/main.py /home/USERNAME/bvg_abfahrt/config/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bvg-display.service
sudo systemctl start bvg-display.service
sudo systemctl status bvg-display.service
```

### Disable Screen Blanking

```bash
./disable_screen_blanking.sh
sudo reboot
```

Or manually:
```bash
# Desktop OS
nano ~/.config/lxsession/LXDE-pi/autostart
# Add:
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0

# Lite OS (console)
sudo nano /boot/cmdline.txt
# Add at end: consoleblank=0
```

## 🐛 Troubleshooting

### Service Won't Start - User Error

**Error:** `Failed to determine user credentials: No such process`

**Fix:** Edit the service file with the correct username:
```bash
sudo nano /etc/systemd/system/bvg-display.service
# Change "User=USERNAME" to your actual username (e.g., User=pi)
sudo systemctl daemon-reload
sudo systemctl restart bvg-display.service
```

### Display Not Showing

```bash
# Check service status
sudo systemctl status bvg-display.service

# View recent logs
sudo journalctl -u bvg-display.service -n 50

# View live logs
sudo journalctl -u bvg-display.service -f

# Test manually
./.venv/bin/python3 main.py ./config/config.json
```

### Screen Goes Black

```bash
./disable_screen_blanking.sh
sudo reboot
```

### No Departures Showing

```bash
# Test internet
ping -c 3 v6.bvg.transport.rest

# Test API directly
curl "https://v6.bvg.transport.rest/stops/900131508/departures?duration=60"

# Check logs for errors
sudo journalctl -u bvg-display.service -n 50
```

### Performance Issues (Pi Zero)

1. Increase `refreshInterval` to 60 seconds
2. Reduce to 1 station in config
3. Lower display resolution
4. Consider upgrading to Pi Zero 2W

### Python/Pygame Issues

```bash
# Test pygame
python3 -c "import pygame; pygame.init(); print('OK')"

# Reinstall if needed
pip3 install --upgrade pygame

# Check SDL2
dpkg -l | grep libsdl2
```

## 📚 Additional Resources

- **[BVG API Docs](https://v6.bvg.transport.rest/api.html)** - API reference
- **[Pygame Documentation](https://www.pygame.org/docs/)**
- **[Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)**

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# Test with example config
python3 main.py ./config/config.example.json

# Test mode (with fake disruptions)
# Set "testMode": true in config
```

### Validate Config
```bash
python3 validate_config.py
```

### Find Stations
```bash
python3 find_station.py "Station Name"
```

## 🙏 Credits

- **BVG API**: [v6.bvg.transport.rest](https://v6.bvg.transport.rest/)
- **pygame**: Display rendering
- **Inspired by**: Public transport displays worldwide

## 📄 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your setup photos!

## 📧 Contact

Have questions? Open an issue or reach out!

---

Made with ❤️ for Berlin's public transport riders 🚊

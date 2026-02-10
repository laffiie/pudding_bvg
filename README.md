# BVG Departure Monitor

A real-time public transport departure display for the Berliner Verkehrsbetriebe (BVG), designed to run on Raspberry Pi hardware. This application retrieves live data including departures, delays, and service disruptions, presenting them in a clear, legible interface suitable for dedicated hardware displays.

## Overview

The BVG Departure Monitor connects to the [VBB/BVG API](https://v6.bvg.transport.rest) to fetch real-time transit data. It is optimized for low-power devices like the Raspberry Pi Zero 2 W and renders using Pygame for smooth, direct-to-framebuffer output.

Key capabilities include:
- **Real-time Monitoring**: Displays continuous departure updates for configured stations.
- **Walking Time Logic**: Visually indicates if a connection is reachable based on configured walking times.
- **Service Alerts**: Shows delays and active disruption warnings.
- **Hardware Optimization**: Designed for always-on operation with screen burn-in protection and service management.

## Features

- **Multi-Station Support**: Monitor multiple stations simultaneously (e.g., tram and subway stops).
- **Customizable Filtering**: Filter specific lines or directions for each station.
- **Visual Status Indicators**: Color-coded departure times indicating reachability and delays.
- **Remote Management**: Includes scripts for deployment and service management over SSH.
- **Minimalist Interface**: High-contrast UI designed for readability at a distance.

## Requirements

### Hardware
- **Raspberry Pi**: Tested on Raspberry Pi Zero 2 W; compatible with Pi 3/4/5.
- **Display**: HDMI or SPI display compatible with the Raspberry Pi.

### Software
- **Operating System**: Raspberry Pi OS (Lite recommended) or Linux.
- **Python**: Version 3.11 or higher.
- **Dependencies**: SDL2 libraries (for Pygame).

## Installation

### Automated Installation (Raspberry Pi)

A setup script is provided to automate system updates, dependency installation, and environment configuration.

1.  Transfer the repository to your Raspberry Pi.
2.  Run the installation script:
    ```bash
    ./install_pi.sh
    ```

### Manual Installation

1.  **Install System Dependencies**:
    ```bash
    sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
    ```

2.  **Install Python Dependencies**:
    ```bash
    pip3 install -r requirements.txt
    ```

### Docker

A `Dockerfile` is included for containerized deployment.

```bash
docker build -t bvg-monitor .
docker run -d --device /dev/vchiq --device /dev/fb0 -v $(pwd)/config:/app/config bvg-monitor
```

## Configuration

The application is configured via a JSON file located at `config/config.json`. An example configuration is provided in `config.example.json`.

### Finding Station IDs

To configure your monitored stations, you need their unique BVG station IDs. Use the provided utility:

```bash
python3 find_station.py "Station Name"
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `stations` | Array | List of station objects to monitor. |
| `refreshInterval` | Integer | API polling interval in seconds (default: 30). |
| `maxDepartures` | Integer | Maximum number of departures to display per screen. |
| `displayWidth` | Integer | Width of the display in pixels. |
| `displayHeight` | Integer | Height of the display in pixels. |
| `fullscreen` | Boolean | Whether to run the application in fullscreen mode. |

**Station Object Structure:**

```json
{
  "id": "900100003",
  "name": "S+U Alexanderplatz",
  "walkingTime": 5,
  "lines": ["M4", "U2"],
  "excludeDirections": ["Warschauer Str."]
}
```

- `id`: The station ID found via `find_station.py`.
- `walkingTime`: Time in minutes required to walk to the station. Departures sooner than this will be highlighted differently. *Note: Determining these walking times is your task—consider it a little homework.*
- `lines`: (Optional) List of specific lines to filter (e.g., "M4"). If empty, shows all lines.
- `excludeDirections`: (Optional) List of destination names to ignore.

## Usage

### Local Testing

To run the application on a desktop environment (macOS/Windows/Linux):

1.  Configure `config/config.json`.
2.  Run the main application:
    ```bash
    python3 main.py ./config/config.json
    ```

### Production Deployment

For continuous operation on a Raspberry Pi, run the application as a systemd service.

1.  **Enable the Service**:
    ```bash
    sudo cp bvg-display.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable bvg-display.service
    sudo systemctl start bvg-display.service
    ```

2.  **Display Management**:
    Use `disable_screen_blanking.sh` to prevent the screen from sleeping during operation.

### Development Commands

A `Makefile` is included for common development tasks:

- `make validate`: Validates the syntax of `config.json`.
- `make deploy`: Deploys current code to the configured Raspberry Pi.
- `make logs`: Tails the logs on the remote Raspberry Pi.

## License

This project is open-source and available under the MIT License.

# Magic Mirror Project

## Overview

A smart magic mirror built using a Samsung 1080p TV behind two-way mirror glass in a custom wooden frame. The mirror displays information from various web services and home automation systems, with presence detection and environmental sensing capabilities.

**Status:** On hold — pending hardware decision (see [Next Steps](#next-steps))

**Repository:** [github.com/mattschoenholz/General-Projects](https://github.com/mattschoenholz/General-Projects)

---

## Hardware Inventory

### Display
- Samsung 1080p Smart TV (existing, mounted in wooden frame)
- Two-way mirror glass (existing, in front of TV)
- Custom wooden frame (existing, built to house TV + glass)
- HDMI-CEC (Anynet+) confirmed enabled on TV — allows software control of TV power and brightness

### Compute (Current — Retired)
- **UDOO Quad** (original 2013 Kickstarter board) — **RETIRED, hardware fault**
  - NXP iMX6 Quad ARM Cortex-A9 @ 1GHz
  - 1GB DDR3 RAM
  - Atmel ATSAM3X8E (Arduino Due compatible) co-processor
  - Ralink/Mediatek RT5370 WiFi (802.11n)
  - Board label: CS975REVD BD REVD
  - See [UDOO Diagnosis](#udoo-quad-diagnosis) for full failure analysis

### Compute (Recommended Replacement)
- **Raspberry Pi 4 (2GB or 4GB)** — ~$45-55
  - Available at Amazon, Adafruit, PiShop, Vilros
  - Runs current Raspberry Pi OS
  - Node.js 18 available directly via apt
  - MagicMirror² has a one-line installer for Pi
  - Rock solid WiFi

### Sensors (Purchased, Ready to Install)
| Sensor | Interface | Purpose | Notes |
|--------|-----------|---------|-------|
| HLK-LD2420 | UART (115200 baud) | Presence detection | 24GHz mmWave radar — detects stationary presence, not just motion. Range up to 8m. 3.3V |
| BME280 | I2C (0x76) | Temp / humidity / pressure | Environmental data for mirror display + Home Assistant |
| BH1750 (GY-302) | I2C (0x23) | Ambient light (lux) | Auto-dim TV brightness. Ordered, arriving soon |

### Other Hardware
- USB webcam (available) — reserved for future face detection / CV experiments
- 12V 5A barrel jack power supply (5.5mm/2.1mm, centre positive)
- 32GB Samsung microSD card (good quality, available)

---

## Planned Software Architecture

### Main Platform
**MagicMirror²** (Node.js) running on Linux

### Web Service Integrations
| Service | Module | Method | Notes |
|---------|--------|--------|-------|
| Spotify | MMM-OnSpotify | OAuth (Spotify Web API) | Display only — now playing, album art, progress bar. No audio playback |
| YouTube | newsfeed (built-in) | RSS (no API key needed) | Release radar — 6 most recent videos from subscribed channels. URL format: `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID` |
| Home Assistant | MMM-HomeAssistantDisplay | REST API + long-lived token | Display entity states using HA template language |
| Calendars | calendar (built-in) | .ics / iCal feeds | Supports Google Calendar, Apple iCal, Outlook. Built-in default module |
| Alexa | Via Home Assistant bridge | HA Alexa skill + Node-RED | Voice control of mirror pages/actions via HA routines |

### TV Control
- **HDMI-CEC** via `cec-client` on Linux
- Presence detected by LD2420 → Arduino → serial → Linux → CEC command → TV on/off
- Lux level from BH1750 → Arduino → serial → Linux → CEC brightness command

### Sensor Architecture
```
LD2420 (UART) ──────────────────────────┐
BME280 (I2C 0x76) ──┬── Arduino Due/Nano ──── Serial ──── Linux/MagicMirror²
BH1750 (I2C 0x23) ──┘                                          │
                                                                ├── HDMI CEC → Samsung TV
                                                                ├── Home Assistant REST API
                                                                └── MagicMirror² modules
```

Arduino reports all sensor data as a JSON string every 1 second over serial.

Example JSON payload:
```json
{
  "presence": true,
  "distance": 145,
  "temperature": 21.4,
  "humidity": 48.2,
  "pressure": 1013.2,
  "lux": 320
}
```

### Serial Port (UDOO specific — for reference)
- iMX6 ↔ SAM3X serial: `/dev/ttymxc3` at 115200 baud
- On Raspberry Pi with Arduino Nano via USB: `/dev/ttyUSB0` or `/dev/ttyACM0`

---

## Sensor Wiring

### Important: UDOO Arduino Due — 3.3V ONLY
All I2C and UART sensors must be 3.3V compatible. Do NOT use 5V signals.

### I2C Bus (BME280 + BH1750 share same pins)
| Pin | Arduino Due | Raspberry Pi 4 |
|-----|-------------|----------------|
| SDA | Pin 20 | GPIO 2 (Pin 3) |
| SCL | Pin 21 | GPIO 3 (Pin 5) |
| VCC | 3.3V | 3.3V |
| GND | GND | GND |

Both sensors share the same SDA/SCL lines — different I2C addresses (BME280: 0x76, BH1750: 0x23) prevent conflicts.

### LD2420 UART
| LD2420 Pin | Arduino Due | Raspberry Pi 4 |
|------------|-------------|----------------|
| TX | Serial1 RX | GPIO 15 (RX) |
| RX | Serial1 TX | GPIO 14 (TX) |
| VCC | 3.3V | 3.3V |
| GND | GND | GND |

**Baud rate:** 115200 (firmware v1.5.3+) or 256000 (older firmware)

### Arduino Libraries Required
```
BH1750 by Christopher Laws
Adafruit BME280
ld2420 by Bolukan (or similar)
Wire (built-in)
```

---

## UDOO Quad Diagnosis

### What We Proved
- Board boots correctly with UDOObuntu 2.2.0 Minimal
- Stable at idle (38-41°C, clean dmesg, no kernel errors)
- WiFi (RT5370) driver in kernel 3.14 is unstable under sustained data transfer
- Even with WiFi disabled, board crashes during sustained local SD card writes

### Crash Pattern
Every crash occurred during sustained I/O operations:
| Operation | Type | Result |
|-----------|------|--------|
| apt-get upgrade | Network + disk | Crash |
| nvm install | CPU + disk | Crash |
| tar xz extraction | CPU | Crash |
| scp receiving files | Network | Crash |
| apt-get install libstdc++6 | Network + disk | Crash |
| sudo cp -R (local file copy) | Disk only | Crash after ~1 hour |

### Root Cause Conclusion
The final crash — a pure local `cp` command with WiFi disabled and no network activity — eliminates WiFi, network, and CPU as causes. The board crashes during sustained SD card writes regardless of other factors. This points to a degraded SD card controller or failing memory on a 10+ year old board. Not worth further debugging.

### Boot Fix Discovered (uEnv.txt)
UDOObuntu ships with an empty uEnv.txt causing silent boot failure. Fix:
```
mmcroot=/dev/mmcblk0p2 rootwait rw
mmcargs=setenv bootargs console=ttymxc1,115200 root=${mmcroot}
uenvcmd=fatload mmc 0:1 ${loadaddr} zImage; fatload mmc 0:1 ${fdtaddr} dts/imx6q-udoo-hdmi.dtb; bootz ${loadaddr} - ${fdtaddr}
```
File location: `/Volumes/BOOT/uEnv.txt` (edit from Mac before first boot)

### WiFi Blacklist (for reference)
```bash
echo "blacklist rt2800usb
blacklist rt2x00usb
blacklist rt2x00lib" | sudo tee /etc/modprobe.d/blacklist-wifi.conf
```

### UDOO Board Jumpers
- **J2** — enables OTG power supply
- **J16** — resets Arduino SAM3X
- **J18** — routes CN6 micro USB to iMX6 (plugged) or SAM3X (unplugged). **Not present on this board revision**
- **J22** — erases Arduino sketch
- **CN6** — micro USB, Arduino serial (J18 unplugged) or iMX6 serial (J18 plugged)
- **CN3** — micro USB OTG port

---

## Next Steps

### Recommended Hardware Path
1. **Purchase Raspberry Pi 4 (2GB minimum, 4GB preferred)** — ~$45-80
   - Available: Amazon, Adafruit, PiShop, Vilros
   - Next day delivery available on Amazon Prime
2. **Purchase Arduino Nano** — ~$5-10
   - Handles LD2420 UART + BME280 + BH1750 I2C
   - Connects to Pi via USB serial
   - Arduino Due-compatible code will work with minor pin changes

### Pi 4 Setup Sequence
```bash
# Flash Raspberry Pi OS Lite (64-bit) using Raspberry Pi Imager
# Enable SSH in imager advanced options before flashing

# First boot — SSH in
ssh pi@raspberrypi.local

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should show v18.x.x

# Install MagicMirror²
bash -c "$(curl -sL https://raw.githubusercontent.com/sitetyler/magicmirror-installer/master/installer.sh)"

# Install cec-utils for TV control
sudo apt-get install -y cec-utils

# Test CEC TV control
echo "on 0" | cec-client -s -d 1      # Turn TV on
echo "standby 0" | cec-client -s -d 1  # Turn TV off
```

### MagicMirror² Modules to Install
```bash
cd ~/MagicMirror/modules

# Spotify now playing
git clone https://github.com/Fabrizz/MMM-OnSpotify.git
cd MMM-OnSpotify && npm install

# Home Assistant display
git clone https://github.com/wonderslug/MMM-HomeAssistantDisplay.git
cd MMM-HomeAssistantDisplay && npm install
```

### YouTube RSS Feed URLs
Replace `CHANNEL_ID` with actual channel IDs from subscribed channels:
```
https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
```
Add multiple feeds to MagicMirror² built-in `newsfeed` module — no API key required.

### MagicMirror² Config Template
```javascript
{
    module: "calendar",
    position: "top_left",
    config: {
        calendars: [
            { url: "YOUR_ICS_URL_HERE" }
        ]
    }
},
{
    module: "MMM-OnSpotify",
    position: "bottom_right",
    config: {
        clientID: "YOUR_CLIENT_ID",
        clientSecret: "YOUR_CLIENT_SECRET",
        accessToken: "YOUR_ACCESS_TOKEN",
        refreshToken: "YOUR_REFRESH_TOKEN"
    }
},
{
    module: "newsfeed",
    position: "bottom_bar",
    config: {
        feeds: [
            {
                title: "YouTube",
                url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID"
            }
        ],
        showPublishDate: true,
        showSourceTitle: true
    }
},
{
    module: "MMM-HomeAssistantDisplay",
    position: "top_right",
    config: {
        host: "YOUR_HA_HOST",
        token: "YOUR_HA_LONG_LIVED_TOKEN",
        port: 8123
    }
}
```

### Arduino Sensor Sketch (Starting Point)
```cpp
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>

Adafruit_BME280 bme;
BH1750 lightMeter;

// LD2420 on Serial1
bool presence = false;
int distance = 0;

void setup() {
    Serial.begin(115200);   // To Raspberry Pi
    Serial1.begin(115200);  // To LD2420
    Wire.begin();
    bme.begin(0x76);
    lightMeter.begin();
}

void loop() {
    // Read LD2420 (simplified)
    // Full implementation needs LD2420 library

    // Read BME280
    float temp = bme.readTemperature();
    float humidity = bme.readHumidity();
    float pressure = bme.readPressure() / 100.0F;

    // Read BH1750
    float lux = lightMeter.readLightLevel();

    // Send JSON to Pi
    Serial.print("{");
    Serial.print("\"presence\":");  Serial.print(presence ? "true" : "false");
    Serial.print(",\"distance\":"); Serial.print(distance);
    Serial.print(",\"temperature\":"); Serial.print(temp);
    Serial.print(",\"humidity\":"); Serial.print(humidity);
    Serial.print(",\"pressure\":"); Serial.print(pressure);
    Serial.print(",\"lux\":"); Serial.print(lux);
    Serial.println("}");

    delay(1000);
}
```

---

## Files in This Repository

```
General-Projects/
└── magic-mirror/
    ├── README.md                    ← This file
    ├── arduino/
    │   └── sensor_hub/
    │       └── sensor_hub.ino       ← Arduino sensor sketch
    └── magicmirror/
        └── config.js               ← MagicMirror² config template
```

---

## Resources

- [MagicMirror² Documentation](https://docs.magicmirror.builders/)
- [MagicMirror² Module List](https://modules.magicmirror.builders/)
- [MMM-OnSpotify GitHub](https://github.com/Fabrizz/MMM-OnSpotify)
- [MMM-HomeAssistantDisplay GitHub](https://github.com/wonderslug/MMM-HomeAssistantDisplay)
- [LD2420 Arduino Library](https://github.com/Bolukan/ld2420)
- [BH1750 Arduino Library](https://github.com/claws/BH1750)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [YouTube RSS Feed Format](https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID)

---

*Last updated: March 2026*
*Project started: March 2026*

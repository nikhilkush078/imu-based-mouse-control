# MPU-6500 ESP8266 Tilt Mouse

A wireless hand-tilt mouse controller built using an **ESP8266 NodeMCU** and **MPU-6500 IMU**.

## Features

- Tilt left/right → Move mouse left/right
- Tilt forward/backward → Move mouse up/down
- Small tilt → Slow movement
- Large tilt → Fast movement
- Hold tilt → Continuous movement
- Return to neutral → Stop
- Button 1 → Mouse left click
- Button 2 → Reserved for custom use
- Wi-Fi + UDP communication
- Linux virtual mouse using `evdev` / `uinput`

## Hardware

- NodeMCU ESP8266
- MPU-6500
- 2 × Push buttons
- Breadboard and jumper wires
- Ubuntu laptop/PC

## Connections

### MPU-6500 → NodeMCU

| MPU-6500 | NodeMCU |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | D2 / GPIO4 |
| SCL | D1 / GPIO5 |
| INT | Not connected |

### Buttons

| Button | NodeMCU | Other side |
|---|---|---|
| Button 1 | D5 | GND |
| Button 2 | D6 | GND |

The buttons use `INPUT_PULLUP`.

## How It Works

```text
Hand Tilt
   ↓
MPU-6500
   ↓
ESP8266
   ↓
Wi-Fi / UDP
   ↓
Python
   ↓
Linux Virtual Mouse
   ↓
Cursor / GameThe MPU-6500 provides raw accelerometer values:

AX, AY, AZ

Python converts these values into tilt angles:

X angle → Horizontal movement
Y angle → Vertical movement

The amount of tilt determines the mouse speed.

A small dead zone prevents small sensor noise from moving the cursor.

UDP Format

The ESP8266 sends:

AX,AY,AZ,BUTTON1,BUTTON2

Example:

1200,-500,16000,1,0

Here:

1200 = AX
-500 = AY
16000 = AZ
1 = Button 1 pressed
0 = Button 2 released
Configuration

In the ESP8266 code, set your Wi-Fi details:

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

const char* laptopIP = "YOUR_LAPTOP_IP";

UDP port:

4210

MPU-6500 I²C address:

0x68
Running on Ubuntu

Check the Python code:

/usr/bin/python3 -m py_compile main.py

Run the mouse controller:

sudo /usr/bin/python3 main.py

If required:

sudo modprobe uinput
Controls
Hand / Button	Action
Tilt left	Cursor left
Tilt right	Cursor right
Tilt forward	Cursor up
Tilt backward	Cursor down
Larger tilt	Faster movement
Neutral	Stop
Button 1	Left click
Button 2	Reserved
Important Settings

The Python program currently uses:

DEAD_ZONE = 5.0
MAX_ANGLE = 45.0
MAX_SPEED = 25

Increase MAX_SPEED for faster cursor movement.

Increase DEAD_ZONE if the cursor moves when the hand is supposed to be neutral.

Future Improvements
Program Button 2 for a custom function
Add startup calibration
Add adjustable sensitivity
Improve filtering
Add gyro + accelerometer sensor fusion
Add battery-powered operation
Create a configuration interface
Author

Nikhil Kushwah



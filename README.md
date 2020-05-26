# moosic-oled
A small Python3 utility that provides OLED display output for MPD. Used in the Moosic project.

## Requirements
* Raspberry Pi running Raspbian and Moosic (although will work with plain MPD)

For ssd1306 based OLED displays:
* OLED supported by luma.oled
This library is currently built for 256x64 displays only (although additional displays can be added)

## Installation
Install Python3 and pip3:
```
sudo apt install python3-dev python3-pip libfreetype6-dev libjpeg-dev build-essential libopenjp2-7 libtiff5
```
For OLED displays:
```
sudo -H pip3 install --upgrade luma.oled python-mpd2
git clone https://github.com/gilphilbert/moosic-oled.git
```

## Running
```
cd ~/moosic-oled
./moosic.py
```

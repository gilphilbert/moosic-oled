# moosic-oled
A small Python3 utility that provides OLED display output for MPD

## Requirements
Raspberry Pi running Raspbian
OLED supported by luma.oled

## Installation
Install Python3 and pip3:
```
sudo apt install python3-dev python3-pip libfreetype6-dev libjpeg-dev build-essential libopenjp2-7 libtiff5

sudo -H pip3 install --upgrade luma.oled python-mpd2

git clone https://github.com/gilphilbert/moosic-oled.git
```

## Running
```
cd ~/moosic-oled
./moosic.py
```

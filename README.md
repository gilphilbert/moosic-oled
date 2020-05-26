# moosic-oled
A small Python3 utility that provides OLED and LCD display output for MPD. Used in the Moosic project.

Currently supports ssd1306 based OLEDs.

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

## Running as a service
```
sudo cp moosic-oled.service /etc/systemd/system/
sudo systemctl enable moosic-oled
sudo systemctl start moosic-oled
```

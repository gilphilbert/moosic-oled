#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#generic imports needed
import asyncio
import time
from select import select
import os.path

#mpd library
from mpd import MPDClient

#display library
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322

#drawing font library
from PIL import Image
from PIL import ImageFont

#create the device
serial = spi(device=0, port=0)
device = ssd1322(serial, 256, 64, 0, 'RGB', 'diff_to_previous')

#this is the MPD host we're connecting to (should be localhost for production)
host = '192.168.68.100'
port = 6600

#our logo
img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))

#define the MPD client
client = MPDClient()
client.timeout = 10

#connect to the MPD server
client.connect(host, port)

#load fonts (so we only have to do this once)
titleFont = ImageFont.truetype('sen-bold.ttf', 18)
font = ImageFont.truetype('VerdanaPro-Regular.ttf', 11)

### --> Format time to strings for display
def format_time(seconds):
    return time.strftime('%M:%S', time.gmtime(seconds))

### --> draw the actual display content
def drawScreen(status, song):
    state = status.get('state')

    elapsed = float(status.get('elapsed'))
    duration = float(status.get('duration'))
    perc = (elapsed / duration)

    _quality = status.get('quality','0:0:0').split(':')
    quality = str(int(int(_quality[0]) / 1000)) + 'kHz ' + _quality[1] + 'bit'

    title = song.get('title')
    artist = song.get('artist')

    if state != 'stop':
        with canvas(device) as draw:

            #insert text (title, artist, quality lines)
            draw.text((0, 0), title, font=titleFont, fill=(255,255,255))
            draw.text((0, 19), artist, font=font, fill=(255,255,255))
            draw.text((0, 31), quality, font=font, fill=(130,130,130))

            #current song elapsed (bottom left)
            draw.text((0, 46), format_time(elapsed), font=font, fill=(255,255,255))
            #current song duration
            durText = format_time(duration)
            durX = 256 - draw.textsize(format_time(duration), font)[0]
            draw.text((durX, 46), durText, font=font, fill=(255,255,255))
            #progress bar background
            draw.rectangle([(0,60),(256,64)], fill=(75,75,75))
            #progress bar fill
            draw.rectangle([(0,60),(round(256*perc),64)], fill=(255,255,255))

            if state == 'play':
                #play icon
                draw.polygon([(124,48), (133,53), (124,58)], fill='white')
            else:
                #pause icon
                draw.rectangle([(124,48),(126,58)], fill='white')
                draw.rectangle([(130,48),(132,58)], fill='white')

    else:
        #there's nothing playing, just show the logo
        logo = Image.open(img_path).convert("RGB")
        device.display(logo)


async def startLoop(playState):
    #store progress
    playProgress = 0
    #assume we're not playing and set a timer
    screenOff = int(time.time() + 29)
    #store the current time
    curTime = int(time.time())
    #check to see if time has changed
    cur = { 'status': {}, 'song': {} }
    while True:
        #check to see if the time has changed
        loopTime = int(time.time())
        hasTicked = False
        if loopTime > curTime:
            #update the clock
            curTime = loopTime
            hasTicked = True

        #if the screenOff timer is set and we're past that time
        if screenOff > 1 and screenOff < curTime:
            #turn off the display
            device.hide()
            screenOff = 1

        #check if MPD has sent us an update
        canRead = select([client], [], [], 0)[0]
        changes = []
        if canRead:
            #fetch changes
            changes = client.fetch_idle()

        #if the data has changed (this doesn't differentiate between any sort of messages)
        if len(changes) > 0:
            #fetch data from the server
            cur['status'] = client.status()
            cur['song'] = client.currentsong()

            #prep data and draw sceen
            drawScreen(cur.get('status'), cur.get('song'))

            #has the play state changed?
            if (playState != cur.get('status').get('state')):
                #update the state
                playState = cur.get('status').get('state')
                #if we're not playing
                if (playState != 'play'):
                  #set a timer for 30s
                  screenOff = curTime + 29
                #if the new state is play and the screen is off
                if (playState == 'play' and screenOff == 1):
                  #turn the screen on
                  device.show()
                  screenOff = 0

            #continue waiting for updates
            client.send_idle()

        #status hasn't changed, but time has passed (this provides updates in 1s intervals...)
        elif playState == "play" and hasTicked == True:
            #incrememnt elapsed
            cur['status']['elapsed'] = int(float(cur['status']['elapsed'])) + 1
            #update the display
            drawScreen(cur.get('status'), cur.get('song'))

#we need to update the screen to start (we may not get a status update)

#fetch data
status = client.status()
song = client.currentsong()

#prep data and draw sceen
drawScreen(status, song)

#create the loop
loop = asyncio.get_event_loop()

#start waiting for new data
try:
    client.send_idle()
    asyncio.ensure_future(startLoop(status['state']))  #(startLoop(status['duration'], status['elapsed']))
    loop.run_forever()
except KeyboardInterrupt:
    print('Caught [CTRL][C]')
    try:
        loop.close()
    except:
        pass

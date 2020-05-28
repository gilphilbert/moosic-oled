#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#generic imports needed
import time
import os.path

#drawing font library
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import sys
sys.path.insert(1, 'vendor')
from colorthief import ColorThief

import requests
import io
import urllib.parse

#our logo
img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))

#load fonts (so we only have to do this once)
titleFont = ImageFont.truetype('fonts/MavenPro-Bold.ttf', 60)
font = ImageFont.truetype('fonts/MavenPro-Medium.ttf', 35)
qFont = ImageFont.truetype('fonts/MavenPro-Medium.ttf', 22)

### --> Format time to strings for display
def format_time(seconds):
    return time.strftime('%M:%S', time.gmtime(seconds))

### --> draw the actual display content
def drawScreen(status, song):
    state = status.get('state')

    elapsed = float(status.get('elapsed'))
    duration = float(status.get('duration'))
    perc = (elapsed / duration)

    _quality = status.get('audio','0:0:0').split(':')
    quality = str(int(int(_quality[0]) / 1000)) + 'kHz ' + _quality[1] + 'bit'

    title = song.get('title')
    artist = song.get('artist')
    album = song.get('album')

    aaurl = "http://127.0.0.1:3000" + urllib.parse.quote("/art/album/" + artist + "/" + album)
    print(aaurl)

    r = requests.get(aaurl, stream=True)
    aa = Image.open(io.BytesIO(r.content))
    thumbSize = (420, 420)

    aa = aa.resize(thumbSize)
    color_thief = ColorThief(aa)
    dominant_color = color_thief.get_color()

    w, h = 1920, 480
    img = Image.new("RGBA", (w, h), dominant_color)
    draw = ImageDraw.Draw(img)
    img.paste(aa, (30, 30))

    if state != 'stop':

        #insert text (title, artist, quality lines)
        draw.text((503, 30), title, font=titleFont, fill=(255,255,255))
        draw.text((503, 115), artist, font=font, fill=(255,255,255))
        draw.text((503, 166), album, font=font, fill=(255,255,255))

        #current song quality
        draw.rectangle([(503,230), (683,280)], fill=(255,255,255,90))
        draw.text((523, 240), quality, font=qFont, fill=(255,255,255))

        #current song elapsed (bottom left)
        draw.text((503, 372), format_time(elapsed), font=font, fill=(255,255,255))
        #current song duration
        durText = format_time(duration)
        durX = 1378 - draw.textsize(format_time(duration), font)[0]
        draw.text((durX, 372), durText, font=font, fill=(255,255,255))

        progress_start = 503
        progress_end = 1378
        progress_size = 660

        #progress bar background
        #draw.rectangle([(0,60),(256,64)], fill=(75,75,75))
        draw.rectangle([(progress_start, 423),(progress_end, 450)], fill=(255,255,255,90))
        #progress bar fill
        #draw.rectangle([(0,60),(round(256*perc),64)], fill=(255,255,255))
        draw.rectangle([(progress_start, 423),(progress_start+round(progress_end*perc), 450)], fill=(255,255,255))

        if state == 'play':
            #play icon
            draw.polygon([(124,48), (133,53), (124,58)], fill='white')
        else:
            #pause icon
            draw.rectangle([(124,48),(126,58)], fill='white')
            draw.rectangle([(130,48),(132,58)], fill='white')

        draw.rectangle([(1432,0),(1437,480)], fill=(255,255,255))

        img.save("out.png","PNG")
            

    else:
        #there's nothing playing, just show the logo
        logo = Image.open(img_path).convert("RGB")
        logo.save("out.png","PNG")
        #device.display(logo)

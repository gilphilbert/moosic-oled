#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#generic imports needed
import time
import os.path

#drawing font library
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import requests
import io
import urllib.parse

#our logo
img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))

#load fonts (so we only have to do this once)
titleFont = ImageFont.truetype('fonts/Manrope-Regular.otf', 15)
font = ImageFont.truetype('fonts/pf_tempesta_seven.ttf', 8)
qFont = ImageFont.truetype('fonts/uni0553-webfont.ttf', 8)

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

    w, h = 1920, 480
    img = Image.new("RGB", (w, h))
    if state != 'stop':
        draw = ImageDraw.Draw(img)

        r = requests.get(aaurl, stream=True)
        aa = Image.open(io.BytesIO(r.content))
        thumbSize = (420, 420)
        #aa.thumbnail(thumbSize)
        aa = aa.resize(thumbSize)
        img.paste(aa, (30, 30))

        #insert text (title, artist, quality lines)
        draw.text((420, -5), title, font=titleFont, fill=(255,255,255))
        draw.text((420, 14), album, font=font, fill=(255,255,255))
        #draw.text((0, 28), quality, font=font, fill=(130,130,130))
        draw.text((420, 26), artist, font=font, fill=(255,255,255))

        #current song elapsed (bottom left)
        draw.text((190, 30), quality, font=qFont, fill=(255,255,255))

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

            #icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon-cd.png'))
            #icon = Image.open(icon_path).convert("RGB")
            #size = 24, 24
            #icon.thumbnail(size, Image.ANTIALIAS)
            #offset = 232, 12
            #draw.paste(icon, offset) 
        img.save("out.png","PNG")
            

    else:
        #there's nothing playing, just show the logo
        logo = Image.open(img_path).convert("RGB")
        logo.save("out.png","PNG")
        #device.display(logo)

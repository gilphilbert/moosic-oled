#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#generic imports needed
import asyncio
import time
from select import select

#parse arguments
import sys, getopt

#mpd library
from mpd import MPDClient

#from ssd1306 import drawScreen
from fb import drawScreen

Single = False
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv,"hs",["help", "single"])
except getopt.GetoptError:
    print ('Usage: moosic.py [-s]')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-s' or opt == '--single':
        Single = True

#this is the MPD host we're connecting to (should be localhost for production)
host = '127.0.0.1'
port = 6600

#define the MPD client
client = MPDClient()
client.timeout = 10

#connect to the MPD server
client.connect(host, port)

#async def startLoop(playState):
async def startLoop(status, song):
    playState = status.get('state')
    #store progress
    playProgress = 0
    #assume we're not playing and set a timer
    screenOff = int(time.time() + 29)
    #store the current time
    curTime = int(time.time())
    #check to see if time has changed
    cur = { 'status': status, 'song': song }
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

if Single == False:

    #create the loop
    loop = asyncio.get_event_loop()

    #start waiting for new data
    try:
        client.send_idle()
        #asyncio.ensure_future(startLoop(status['state']))  #(startLoop(status['duration'], status['elapsed']))
        asyncio.ensure_future(startLoop(status, song))  #(startLoop(status['duration'], status['elapsed']))
        loop.run_forever()
    except KeyboardInterrupt:
        print('Caught [CTRL][C]')
        try:
            loop.close()
        except:
            pass

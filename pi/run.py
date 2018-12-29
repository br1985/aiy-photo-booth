#!/usr/bin/env python

import math
import random
import signal
import subprocess
import sys
import time
import threading

import aiy._drivers._buzzer
import aiy.leds
import aiy.pins
import gpiozero
import picamera

def photo():
    global led0, led1, camera

    led0.update(aiy.leds.Leds.privacy_on())
    camera.start_preview()

    with aiy._drivers._buzzer.PWMController(22) as buzzer:
        x = 0.5
        f = 110.0

        while x > 1e-3:
            led0.update(aiy.leds.Leds.rgb_on((
                math.floor((random.random()**2) * 255),
                math.floor((random.random()**2) * 255),
                math.floor((random.random()**2) * 255))))
            buzzer.set_frequency(f)
            time.sleep(x)
            x *= 0.9

            led0.update(aiy.leds.Leds.rgb_off())
            buzzer.set_frequency(0.0)
            time.sleep(x)
            x *= 0.9

            f *= 1.1

        led0.update(aiy.leds.Leds.rgb_on((255, 255, 255)))

        camera.capture('/home/pi/aiy/Pictures/' + time.strftime("%Y-%m-%d %H:%M:%S UTC") + '.jpg')

        buzzer.set_frequency(f)
        time.sleep(x)
        buzzer.set_frequency(0)

    camera.stop_preview()
    led0.update(aiy.leds.Leds.privacy_off())

    subprocess.run(['/usr/bin/ssh', 'aiy@192.168.0.164', 'pictures'])

    x = 0.5
    while x < 255:
        led0.update(aiy.leds.Leds.rgb_on((255-x, 255-x, 255-x)))
        time.sleep(0.01)
        x *= 1.1

    led0.update(aiy.leds.Leds.rgb_off())


def video():
    global led0, led1, camera

    led0.update(aiy.leds.Leds.privacy_on())

    with aiy._drivers._buzzer.PWMController(22) as buzzer:
        camera.start_preview()

        x = 0.5
        f = 110.0

        while x > 1e-3:
            led1.off()
            buzzer.set_frequency(f)
            time.sleep(x)
            x *= 0.9

            led1.on()
            buzzer.set_frequency(0.0)
            time.sleep(x)
            x *= 0.9

            f *= 1.1

        led1.off()

        camera.start_recording('/home/pi/aiy/Videos/' + time.strftime("%Y-%m-%d %H:%M:%S UTC") + '.h264')
        camera.wait_recording(5)
        camera.stop_recording()
        camera.stop_preview()

        buzzer.set_frequency(f)
        time.sleep(x)
        buzzer.set_frequency(0)

    led0.update(aiy.leds.Leds.privacy_off())

    subprocess.run(['/usr/bin/ssh', 'aiy@192.168.0.164', 'videos'])

    x = 0.5
    while x < 255:
        led1.value = x / 255
        time.sleep(0.01)
        x *= 1.1

    led1.on()


def push0():
    global lock

    print('push0')

    if lock.acquire(False):
        photo()
        lock.release()

def push1():
    global lock

    print('push1')

    if lock.acquire(False):
        video()
        lock.release()

lock = threading.Lock()

led0 = aiy.leds.Leds()
led1 = gpiozero.LED(aiy.pins.PIN_B)

button0 = gpiozero.Button(23)
button1 = gpiozero.Button(aiy.pins.PIN_A)

button0.when_pressed = push0
button1.when_released = push1

camera = picamera.PiCamera(framerate=25)

random.seed()

led1.on()

print('ready...')

# signal.pause()

while True:
    print("status:", button0.is_pressed, button1.is_pressed)
    time.sleep(5)

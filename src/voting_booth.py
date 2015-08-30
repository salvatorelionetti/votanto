#!/usr/bin/env python2.7  
import time
import threading
import RPi.GPIO
import model.observable

led_gpio_pin = 23 # GND+5
led_secs_on = 4
led_timer = None
switch_gpio_pin = 24 # GND+6
switch_gpio_active_high = False
buzzer_gpio_pin = 25 # GND+8
buzzer_secs_on = 1
duration = 10

def led_off():
    RPi.GPIO.output(buzzer_gpio_pin, RPi.GPIO.LOW)
    RPi.GPIO.output(led_gpio_pin, RPi.GPIO.LOW)
    print 'led_off'

def switch_ignore():
    RPi.GPIO.cleanup(switch_gpio_pin)
    
def btn1_pressed(channel):
    global led_timer
    switch_ignore()
    print "btn1_pressed", channel
    RPi.GPIO.output(led_gpio_pin, RPi.GPIO.HIGH)
    print 'before',led_timer
    led_timer = threading.Timer(led_secs_on, led_off)
    led_timer.start()
    print 'after',led_timer
  
def setup(callback):
    print 'setup GPIO.BCM'
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    RPi.GPIO.setup(led_gpio_pin, RPi.GPIO.OUT)
    RPi.GPIO.setup(buzzer_gpio_pin, RPi.GPIO.OUT)

    if switch_gpio_active_high:
        RPi.GPIO.setup(switch_gpio_pin, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)
        RPi.GPIO.add_event_detect(switch_gpio_pin, RPi.GPIO.RISING, callback=callback, bouncetime=2000)
        print 'Active High'
    else:
        RPi.GPIO.setup(switch_gpio_pin, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
        RPi.GPIO.add_event_detect(switch_gpio_pin, RPi.GPIO.FALLING, callback=callback, bouncetime=2000)
        print 'Active Low'
    print 'Found switch@', RPi.GPIO.input(switch_gpio_pin)
  
def buzzer_on():
    RPi.GPIO.output(buzzer_gpio_pin, RPi.GPIO.HIGH)

def buzzer_off():
    RPi.GPIO.output(buzzer_gpio_pin, RPi.GPIO.LOW)

def open(callback=btn1_pressed):
    global buzzer_timer
    setup(callback)
    led_off()
    buzzer_on()
    buzzer_timer = threading.Timer(buzzer_secs_on, buzzer_off)
    buzzer_timer.start()
  
def close():
    global led_timer
    global buzzer_timer

    print 'Cleaning up'
    print 'led_timer', led_timer
    led_off()
    buzzer_off()
    RPi.GPIO.cleanup()

    if led_timer is not None:
        print 'Stopping led timer'
        led_timer.cancel()
        led_timer = None

    if buzzer_timer is not None:
        print 'Stopping buzzer timer'
        buzzer_timer.cancel()
        buzzer_timer = None

@model.observable.observable('button_pressed', False,'Button pressed')
@model.observable.observable('button_released', True,'Button released')
class vote(object):
    def __init__(self):
        pass

    def btn_pressed(self, channel):
        print 'vote.btn_pressed',channel
        btn1_pressed(channel)
        self.button_pressed = True

    def open(self):
        print 'vote.__open__'
        open(callback=self.btn_pressed)

    def close(self):
        print 'vote.__close__'
        close()

def main1():
    try:
        open()
        print "Waiting for rising edge on port ", switch_gpio_pin
        time.sleep(duration)

    finally:
        close()

def main2():
    v = vote()
    try:
        v.open()
        print "Waiting for rising edge on port ", switch_gpio_pin
        time.sleep(duration)

    finally:
        if v is not None:
            v.close()

if __name__ == '__main__':
    main2()

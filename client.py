# pip install adafruit-circuitpython-dht
# flask --app client.py run --debug --port 4000 --host 0.0.0.0
# import cv2
#gunicorn --bind 0.0.0.0:4000 wsgi:client
import requests
import time
import os
import threading
import time
import board
import adafruit_dht

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
import random
import copy
import json
from myconfig import image_path

from gpiozero import LED, Button
from gpiozero import PWMLED
from gpiozero import PWMOutputDevice
import math

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

MOTOR = 22
FANIO = 18
class Farm(object):
    def __new__(cls):
        """ creates a singleton object, if it is not created,
        or else returns the previous singleton object"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Farm, cls).__new__(cls)
        return cls.instance
    def __init__(self,pin=MOTOR,pin_fan=FANIO) -> None:
        self.motorc = LED(pin)
        self.motor_status = ''
        self.fanc = LED(pin_fan)
        self.fan_status = ''
        self.temperature_f = None
        self.temperature_c = None
        self.humidity = None
        self.auto_mode = False
        self.motor('off')
        self.fan('off')
        self._json_object = {}
        pass
    def reload_new_data(self):
        # Opening JSON file
        try:
            with open('myfarm.json', 'r') as openfile:
                # Reading from json file
                self._json_object = json.load(openfile)
                self.temperature_f = self._json_object['temperature_f']
                self.temperature_c = self._json_object['temperature_c']
                self.humidity = self._json_object['humidity']
        except:
            pass
    def get_state(self):
        self.reload_new_data()
        
    def motor(self,state):
        if state in ['on','off']:
            self.motor_status = state
            if state in ['on']:
                self.motorc.on()
            if state in ['off']:
                self.motorc.off()
        else:
            return 'error'
        return 'ok'
    def fan(self,state):
        if state in ['on','off']:
            self.fan_status = state
            if state in ['on']:
                self.fanc.on()
            if state in ['off']:
                self.fanc.off()
        else:
            return 'error'
        return 'ok'
    def auto(self,action):
        if action in [True,False,'True','False']:
            self.auto_mode = action
        else:
            return 'error'
        return 'ok'

myfarm = Farm()


@app.route('/apiv1/', methods=['GET'])
def apiv1():
    return jsonify({'msg':myfarm.motor_status})
@app.route('/api/', methods=['GET'])
def get_device_status():
    device = request.args.get('device')
    action = request.args.get('action')
    if action:
        msg = None
        if device == 'motor':
            msg = myfarm.motor(action)
        elif device == 'fan':
            msg = myfarm.fan(action)
        elif device == 'auto':
            msg = myfarm.auto(action)
        else:
            msg = 'Unkown device'
        return jsonify({'msg':msg})
    else:
        status = None
        myfarm.get_state()
        if device == 'motor':
            status = myfarm.motor_status
        elif device == 'fan':
            status = myfarm.fan_status
        elif device == 'tempc':
            status = myfarm.temperature_c
        elif device == 'humi':
            status = myfarm.humidity
        elif device == 'auto':
            status = myfarm.auto_mode
        else:
            status = 'Unkown device'
        return jsonify({'device':device,'status':status })

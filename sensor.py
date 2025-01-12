#python sensor.py
import requests
import time
import os
import threading
import time
import board
import adafruit_dht
import os
from datetime import datetime
import random
import copy
from gpiozero import LED, Button
from gpiozero import PWMLED
from gpiozero import PWMOutputDevice
import math
from picamera2 import Picamera2
import json
from myconfig import image_path
COUNTDOWN_CAPTURE = 2
height = 210
width = 320
dimensions = (width, height)
DOAMDAT = 27
myfarm = {
    'temperature_f': None,
    'temperature_c': None,
    'humidity': None,
    'doamdat': None
          }

ss_doamdat = Button(DOAMDAT)


dhtDevice = adafruit_dht.DHT11(board.D17)
# Hàm chụp ảnh từ webcam và gửi lên server

picam2 = Picamera2()
picam2.start()
time.sleep(5)
picam2.preview_configuration.main.size = dimensions
picam2.preview_configuration.main.format = "RGB888"

URL_BASE = 'https://de37-116-110-43-138.ngrok-free.app'
def send_data_to_server(data):
    try:
        # Gửi ảnh lên server
        url = f"{URL_BASE}/sensor"
        response = requests.post(url, json=data)
        # Kiểm tra phản hồi từ server
        if response.status_code == 200:
            print("sensor uploaded successfully")
        else:
            print("Failed to upload sensor")
    except Exception as ex:
        print(ex)
        pass

def capture_and_send_image():
    # Khởi tạo webcam
    global picam2
    try:
        request = picam2.capture_request()
        time.sleep(20)
        request.save("main",image_path)
        request.release()
        
        # Gửi ảnh lên server
        url = f"{URL_BASE}/upload"
        files = {'file': open(image_path, 'rb')}
        response = requests.post(url, files=files)
        
        # Kiểm tra phản hồi từ server
        if response.status_code == 200:
            print("Image uploaded successfully")
        else:
            print("Failed to upload image")
    except Exception as ex:
        print(ex)
        pass
    # Đóng webcam và xóa ảnh tạm thời
    # os.remove(image_path)

count = 0
def capture_and_send_image_thread():
    global count
    count += 1
    print(count)
    if count >= COUNTDOWN_CAPTURE:
        count = 0
        capture_and_send_image()

def thread_read_sensor(name,myfarm):
    print("Thread %s: starting", name)
    while True:
        capture_and_send_image_thread()
        try:
            print("Thread %s: finishing", name)

            # Print the values to the serial port
            _temperature_c = dhtDevice.temperature
            _temperature_f = _temperature_c * (9 / 5) + 32
            _humidity = dhtDevice.humidity

            if _temperature_c and _humidity:
                myfarm['temperature_f'], myfarm['temperature_c'], myfarm['humidity'] = _temperature_f, _temperature_c, _humidity
                print(
                    "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                        myfarm['temperature_f'], myfarm['temperature_c'], myfarm['humidity']
                    )
                )
            if ss_doamdat.is_pressed:
                myfarm['doamdat'] = 'Do am cao'
            else:
                myfarm['doamdat'] = 'Do am thap'
            # Serializing json
            json_object = json.dumps(myfarm, indent=4)
            send_data_to_server(myfarm)
            # Writing to sample.json
            with open("myfarm.json", "w") as outfile:
                outfile.write(json_object)
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(3.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(3.0)
thread_read_sensor(1,myfarm)
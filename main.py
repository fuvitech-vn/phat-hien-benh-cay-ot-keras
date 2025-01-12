#flask --app main.py run --port 6000 --debug --host 0.0.0.0
from flask import Flask, render_template, request, jsonify
from requests.compat import urljoin
import os
from datetime import datetime
import os
from datetime import datetime
import random
import copy
import cv2
import json
import requests
from myconfig import CLIENT_URL
from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
last_output = ''
myfarm = {
    'temperature_f': None,
    'temperature_c': None,
    'humidity': None,
    'doamdat': None,
    'auto': False,
          }
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),'static/uploads')

def send_message_to_telegram(message):
    try:
        TOKEN = "6232369389:AAEh03D1TObhOcqfzEd1hjzD1_VXoxrV8Ns"
        chat_id = "1227725962"
        
        # TOKEN = "5999578358:AAECv-lTRInbc7jiNJ4Opt1iXSS7Dmo1ZXk"
        # chat_id = "1468168962"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        print(requests.get(url).json()) # this sends the message
    except:
        pass



@app.route('/')
def index():
    global myfarm
    files = os.listdir('static/uploads/')
    print(files)
    if 'temp_image2.jpg' in files:
        files.remove('temp_image2.jpg')
    if 'temp_image.jpg' in files:
        files.remove('temp_image.jpg')
    images = []
    for file in files:
        status, timestamp, jpg = file.split('.')
        image = {'status':status, 'timestamp':timestamp,'path':f'uploads/{file}'}
        print(image) # this
        images.append(image)
    return render_template('upload.html',len=len(images), images=images,img_w=100,img_h=100,\
                            auto=myfarm['auto'], \
                            tempc= myfarm['temperature_c'], \
                            humidity=myfarm['humidity'], \
                            doamdat=myfarm['doamdat'] )

@app.route('/sensor', methods=['POST'])
def sensor():
    global last_output, myfarm
    _myfarm = json.loads(request.data)
    print('myfarm',_myfarm)
    myfarm['temperature_c'] = _myfarm['temperature_c']
    myfarm['doamdat'] = _myfarm['doamdat']
    myfarm['humidity'] = _myfarm['humidity']

    if myfarm['auto']:
        if myfarm['temperature_c'] >= 30:
            sent_request_farm({'device':'fan', 'action':'on'})
        elif myfarm["temperature_c"] < 25:
            sent_request_farm({'device':'fan', 'action':'off'})
        if 'cao' in myfarm['doamdat']:
            sent_request_farm({'device':'motor', 'action':'off'})
        elif 'thap' in myfarm['doamdat']:
            sent_request_farm({'device':'motor', 'action':'on'})

    message = f"""
[{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}]
Temp:{myfarm['temperature_c']}
Humidity:{myfarm['humidity']}
Status: {last_output}
"""
    send_message_to_telegram(message)
    return 'ok'


@app.route('/upload', methods=['POST'])
def upload():
    global last_output
    file = request.files['file']
    filename = file.filename

    # Save the image to the uploads folder
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(image_path)

    # os.mkdir(os.path.join(app.config['UPLOAD_FOLDER']))
    if file:
        file.save(image_path)
        print(type(file))
    output = xulyanh_cayot(image_path)
    last_output = output
    if output:
        image =  cv2.imread(image_path)
        image_path = f'{output}.{int(datetime.now().timestamp())}.jpg'
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        cv2.imwrite(image_path, image)
    return str(output)
def sent_request_farm(params):
    try:
        url=urljoin(CLIENT_URL,'api/')
        print('sent_request_farm',url,params)
        res = requests.get(url , params=params)
        return jsonify({'msg':res.content.decode('utf-8')})
    except Exception as e:
        return jsonify({'msg':str(e)})


@app.route('/api/', methods=['GET'])
def get_device_status():
    device = request.args.get('device')
    action = request.args.get('action')
    if action and device:
        return sent_request_farm({'device':device, 'action':action})

    return jsonify({'msg':'eror'})

def xulyanh_cayot(image_to_detect):
    model = keras.models.load_model('mymodel')
    class_names = ['healthy','leaf curl','white fly','yellowish']
    img = load_img(image_to_detect, target_size=(100, 100))
    img_array = img_to_array(img)
    img_array /= 255.0
    img_array = img_array.reshape((1, 100, 100, 3))
    result = model.predict(img_array)
    class_index = result.argmax()
    print(class_names[class_index])
    return class_names[class_index]

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6000, debug=True)
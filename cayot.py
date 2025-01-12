import os
from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array


model = keras.models.load_model('/home/phuongl/notebook/mymodel')
train_dir = '/home/phuongl/notebook/input/chili-plant-disease/train'
class_names = os.listdir(train_dir)
image_path2='/home/phuongl/notebook/input/chili-plant-disease/test/leaf spot/leaf spot16 (1).jpg'
img = load_img(image_path2, target_size=(100, 100))
img_array = img_to_array(img)
img_array /= 255.0
img_array = img_array.reshape((1, 100, 100, 3))
result = model.predict(img_array)
class_index = result.argmax()
print(class_names[class_index])
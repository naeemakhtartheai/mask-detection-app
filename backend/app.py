

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import tensorflow as tf
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# import numpy as np
# import os

# app = Flask(__name__)
# CORS(app)

# model = load_model('mask_detector_model.h5')

# class_names = ['Mask', 'No Mask']

# def predict_mask(img_path):
#     img = image.load_img(img_path, target_size=(224, 224))
#     img_array = image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#     img_array /= 255.0

#     prediction = model.predict(img_array)
#     return class_names[np.argmax(prediction)]

# @app.route('/predict', methods=['POST'])
# def predict():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image uploaded'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({'error': 'Empty filename'}), 400

#     os.makedirs("temp", exist_ok=True)
#     file_path = os.path.join("temp", file.filename)
#     file.save(file_path)

#     result = predict_mask(file_path)
#     os.remove(file_path)

#     return jsonify({'prediction': result})

# if __name__ == '__main__':
#     app.run(debug=False)










from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Load model
MODEL_PATH = 'mask_detector_model.h5'
model = load_model(MODEL_PATH)
class_names = ['Mask', 'No Mask']

# Initialize Firebase (safe check for reinitialization)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase initialized")
    except Exception as e:
        db = None
        print("❌ Firebase initialization failed:", e)

def predict_mask(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    prediction = model.predict(img_array)
    return class_names[np.argmax(prediction)]

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    os.makedirs("temp", exist_ok=True)
    file_path = os.path.join("temp", file.filename)
    file.save(file_path)

    try:
        result = predict_mask(file_path)
        print(f"🧠 Prediction result: {result}")

        if db:
            try:
                db.collection('predictions').add({
                    'filename': file.filename,
                    'prediction': result
                })
                print("✅ Result saved to Firestore")
            except Exception as firebase_error:
                print("❌ Error saving to Firestore:", firebase_error)
        else:
            print("⚠️ Firebase DB not initialized")

        return jsonify({'prediction': result})
    except Exception as e:
        print("❌ Error during prediction:", e)
        return jsonify({'error': 'Prediction failed'}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=False)

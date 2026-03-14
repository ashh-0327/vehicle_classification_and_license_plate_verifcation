import os
from flask import Flask, render_template, request, jsonify
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
import easyocr
from fuzzywuzzy import fuzz
import csv

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'veriplate-ai-secret-2024')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
os.makedirs('uploads', exist_ok=True)

# Global variables to store current image
current_image_path = None

# Load model once
MODEL_PATH = 'truck_classifier_v2.h5'
model = tf.keras.models.load_model(MODEL_PATH)

PLATE_CASCADE_PATH = 'haarcascade_russian_plate_number.xml'
DATABASE_FILE = 'Telangana_vehicle_registration_dataset.csv'

# EasyOCR reader (initialize once)
reader = easyocr.Reader(['en'], gpu=False)
plate_cascade = cv2.CascadeClassifier(PLATE_CASCADE_PATH)

# ================ PLATE RECOGNITION ================
def recognize_plate(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30))

    if len(plates) > 0:
        for (x, y, w, h) in plates:
            plate_roi = gray[y:y+h, x:x+w]
            _, thresh = cv2.threshold(plate_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            result = reader.readtext(thresh, detail=0, paragraph=False)
            if result:
                text = max(result, key=len).upper().replace(" ", "")
                cleaned = ''.join(c for c in text if c.isalnum())
                if len(cleaned) >= 6:
                    return cleaned

    # Fallback: read from whole image
    result = reader.readtext(gray, detail=0, paragraph=False)
    if result:
        text = max(result, key=len).upper().replace(" ", "")
        cleaned = ''.join(c for c in text if c.isalnum())
        if len(cleaned) >= 6:
            return cleaned
    return None

# ================ DATABASE SEARCH ================
def search_database(plate):
    if not plate or len(plate) < 6:
        return None, "Invalid or no plate detected"
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            best_match = None
            best_score = 0
            for row in csv_reader:
                db_plate = row.get('registrationNo', '').strip().upper()
                if not db_plate:
                    continue
                if db_plate == plate:
                    return row, "Exact Match Found!"
                score = fuzz.ratio(plate, db_plate)
                if score > best_score:
                    best_score = score
                    best_match = row
            if best_score >= 90:
                return best_match, f"Match Found ({best_score}%)"
            return None, f"Not Found (Best: {best_score}%)"
    except Exception as e:
        return None, f"DB Error: {str(e)}"

# ================ ROUTES ================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global current_image_path
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    current_image_path = filepath

    return jsonify({
        'success': True,
        'preview': f"/uploads/{filename}",
        'message': 'Image uploaded! Now click a button below.'
    })

@app.route('/classify_vehicle', methods=['POST'])
def classify_vehicle():
    global current_image_path
    if not current_image_path or not os.path.exists(current_image_path):
        return jsonify({'error': 'No image uploaded yet!'})

    img = image.load_img(current_image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    pred = model.predict(img_array)[0][0]
    confidence = pred if pred > 0.5 else 1 - pred
    confidence_pct = round(confidence * 100, 2)

    result = "TRUCK" if pred > 0.5 else "NOT A TRUCK"
    color = "success" if pred > 0.5 else "danger"

    return jsonify({
        'result': result,
        'confidence': f"{confidence_pct}%",
        'color': color
    })

@app.route('/detect_plate', methods=['POST'])
def detect_plate():
    global current_image_path
    if not current_image_path or not os.path.exists(current_image_path):
        return jsonify({'error': 'No image uploaded yet!'})

    plate = recognize_plate(current_image_path)
    if not plate:
        return jsonify({
            'plate': None,
            'message': 'No number plate detected',
            'details': None
        })

    details, msg = search_database(plate)

    response = {
        'plate': plate,
        'message': msg
    }
    if details:
        response['details'] = {
            'Registration No': details.get('registrationNo'),
            'Maker': details.get('makerName'),
            'Model': details.get('modelDesc'),
            'Fuel': details.get('fuel'),
            'CC': details.get('cc'),
            'Seating': details.get('seatCapacity'),
            'Valid Till': details.get('regvalidto')
        }

    return jsonify(response)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/stats')
def api_stats():
    """Return database record count for frontend counter animation."""
    try:
        count = 0
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            # Count lines quickly (subtract 1 for header)
            count = sum(1 for _ in f) - 1
        return jsonify({'records': max(count, 0)})
    except Exception:
        return jsonify({'records': 500000})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os

# --- PATHS ---
MODEL_PATH = 'truck_classifier_v2.h5'
TEST_DIR = 'C:\\Users\\devas\\OneDrive\\Desktop\\VehicleDetector\\test_folder'  # The main folder containing 'truck' and 'not_truck' subfolders

# Load the trained model
print(f"Loading model from {MODEL_PATH}...")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully.")

total_images = 0
correct_predictions = 0

# Loop through each category ('truck', 'not_truck')
for category in os.listdir(TEST_DIR):
    category_path = os.path.join(TEST_DIR, category)
    
    if not os.path.isdir(category_path):
        continue
        
    print(f"\n--- Testing Category: {category} ---")
    
    # Loop through each image in the category folder
    for img_name in os.listdir(category_path):
        img_path = os.path.join(category_path, img_name)
        
        try:
            # 1. Load and preprocess the image
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0
            
            # 2. Make a prediction
            prediction = model.predict(img_array, verbose=0) # verbose=0 silences prediction spam
            score = prediction[0][0]
            
            total_images += 1
            
            # 3. Check if the prediction was correct
            # 'truck' corresponds to class 1 (score > 0.5)
            # 'not_truck' corresponds to class 0 (score <= 0.5)
            
            result_text = ""
            is_correct = False
            
            if score > 0.5:
                result_text = "TRUCK"
                if category == 'truck':
                    is_correct = True
            else:
                result_text = "NOT a truck"
                if category == 'not_truck':
                    is_correct = True
                    
            if is_correct:
                correct_predictions += 1
                print(f"[OK] {img_name}: Predicted {result_text}")
            else:
                print(f"[FAIL] {img_name}: Predicted {result_text} (Was {category})")

        except Exception as e:
            print(f"Could not process image {img_name}: {e}")

# --- FINAL REPORT ---
if total_images > 0:
    final_accuracy = (correct_predictions / total_images) * 100
    print("\n" + "="*30)
    print("      FINAL TEST REPORT")
    print("="*30)
    print(f"Total Images Tested: {total_images}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Final Test Accuracy: {final_accuracy:.2f}%")
else:
    print("No images found in the test_folder. Please check your folder structure.")
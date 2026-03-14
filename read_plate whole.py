import cv2
import easyocr
import csv
from fuzzywuzzy import fuzz
import numpy as np 

# --- PART 1: LICENSE PLATE RECOGNITION ---
def recognize_plate(image_path):
    """
    Finds a license plate in an image, reads it, and returns the text.
    Includes a fallback to read the whole image if detection fails.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
    reader = easyocr.Reader(['en'])

    # Use aggressive settings to find the plate
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=2)

    if len(plates) == 0:
        print("--- DEBUG: No plate rectangles found. Trying fallback: reading whole image... ---")
        result = reader.readtext(gray, detail=0, paragraph=False)
        if result:
            print("--- DEBUG: Found text in whole image (fallback). ---")
            plate_text = max(result, key=len) 
            plate_text = plate_text.upper().replace(" ", "")
            cleaned_text = ''.join(char for char in plate_text if char.isalnum())
            print(f"Detected Plate Text (from Fallback): {cleaned_text}")
            return cleaned_text
        else:
            print("--- DEBUG: No text found in whole image either. ---")
            
    for (x, y, w, h) in plates:
        print(f"--- DEBUG: Plate rectangle found. Cropping... ---")
        plate_roi = gray[y:y+h, x:x+w]
        
        # Apply threshold
        _, plate_roi_thresh = cv2.threshold(plate_roi, 130, 255, cv2.THRESH_BINARY)
        
        # We removed cv2.imshow to prevent crashes
        
        result = reader.readtext(plate_roi_thresh, detail=0, paragraph=False)

        if result:
            plate_text = max(result, key=len) 
            plate_text = plate_text.upper().replace(" ", "")
            cleaned_text = ''.join(char for char in plate_text if char.isalnum())
            
            print(f"Detected Plate Text (from Crop): {cleaned_text}")
            return cleaned_text

    print("No plate text could be recognized.")
    return None


# --- PART 2: DATABASE LOOKUP (FOR TELANGANA CSV) ---
def search_database(plate_number):
    """
    Searches for a license plate in the large Telangana CSV
    using fuzzy matching and prints verbose output.
    """
    if plate_number is None:
        return None, "Plate not recognized"
    
    DATABASE_FILE = "C:\\Users\\devas\\OneDrive\\Desktop\\VehicleDetector\\Telangana_vehicle_registration_dataset.csv"

    print("\n--- Starting Database Search ---")
    print(f"Searching for detected plate: '{plate_number}'")
    print(f"Opening large database: {DATABASE_FILE}")
    print("...this may take a few minutes...")
            
    try:
        # We open the file and read it line-by-line to save memory
        with open(DATABASE_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            best_match = None
            highest_score = 0
            
            # This loop will be slow
            for i, row in enumerate(reader):
                
                db_plate = row.get('registrationNo') 
                
                if not db_plate: # Skip empty rows
                    continue
                
                db_plate = db_plate.strip()
                
                # Check for an exact match first (this is fast)
                if db_plate == plate_number:
                    print(f"-> Comparing with: '{db_plate}'... Score: 100% (Exact Match!)")
                    return row, "Details Found (Exact Match)"
                
                # Run the slow fuzzy match
                score = fuzz.ratio(plate_number, db_plate)
                
                # Only print updates every 100,000 rows to avoid spamming
                if i % 10000 == 0 and i > 0:
                    print(f"...processed {i} rows. Current best score: {highest_score}%")
                
                # Print any high-scoring matches
                if score > 90:
                    print(f"-> Comparing with: '{db_plate}'... Score: {score}%")
                
                if score > highest_score:
                    highest_score = score
                    best_match = row
            
            # --- END OF FILE ---
            # We use 90% to be flexible
            if highest_score >= 90:
                print(f"\nFound best match above 90% threshold.")
                return best_match, f"Details Found (Fuzzy Match: {highest_score}%)"

    except FileNotFoundError:
        return None, f"Error: {DATABASE_FILE} not found."
    except Exception as e:
        return None, f"An error occurred while reading the file: {e}"
    
    print(f"\nNo match found above 90% threshold.")
    return None, f"Vehicle Not Found in Database (Best score was: {highest_score}%)"


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    
    test_image = "C:\\Users\\devas\\OneDrive\\Desktop\\VehicleDetector\\plates\\ts\\ts_1.png"

    recognized_text = recognize_plate(test_image)
    vehicle_details, message = search_database(recognized_text)

    print("\n--- Search Result ---")
    print(f"Message: {message}")
    
    if vehicle_details:
        # We use .get() which is safer and won't crash if a column is missing
        print(f"  Registration No: {vehicle_details.get('registrationNo')}")
        print(f"  Maker: {vehicle_details.get('makerName')}")
        print(f"  Model: {vehicle_details.get('modelDesc')}")
        print(f"  Body Type: {vehicle_details.get('bodyType')}")
        print(f"  Fuel: {vehicle_details.get('fuel')}")
        print(f"  CC: {vehicle_details.get('cc')}")
        print(f"  Seating Capacity: {vehicle_details.get('seatCapacity')}")
        print(f"  Registration Valid From: {vehicle_details.get('regvalidfrom')}")
        print(f"  Registration Valid To: {vehicle_details.get('regvalidto')}")
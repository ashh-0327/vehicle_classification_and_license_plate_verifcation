# 🚗 VehicleDetector AI

A Flask web application that detects whether a vehicle is a **truck or not**, and performs **number plate recognition** with live database lookup.

---

## 🔍 Features
- **Vehicle Classification** — TensorFlow CNN model (`truck_classifier_v2.h5`)
- **Plate Recognition** — OpenCV + EasyOCR
- **Database Lookup** — fuzzy-match against Telangana vehicle registration dataset
- **Web UI** — Upload image and get instant results

---

## 📁 Project Structure
```
VehicleDetector/
├── app.py                          # Main Flask app
├── requirements.txt                # Python dependencies
├── Procfile                        # Gunicorn start command
├── runtime.txt                     # Python version
├── render.yaml                     # Render.com deploy config
├── .env.example                    # Environment variable template
├── truck_classifier_v2.h5          # TF model (do not commit to git)
├── haarcascade_russian_plate_number.xml  # Haar cascade (do not commit)
├── Telangana_vehicle_registration_dataset.csv  # DB (do not commit)
├── templates/index.html            # Frontend HTML
├── static/                         # CSS / JS assets
└── uploads/                        # Temporary image uploads
```

---

## 🚀 Deploy on Render (Recommended)

> **Important:** The `.h5`, `.csv`, and `.xml` files are **NOT** committed to git (they are too large). You must upload them separately.

### Option A — Auto Deploy via render.yaml
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo — Render will auto-detect `render.yaml`
4. Before deploying, manually upload the large files (see below)
5. Click **Deploy**

### Option B — Manual Setup on Render
1. New → Web Service → Connect GitHub repo
2. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --timeout 120 --workers 1`
   - **Python Version:** `3.10.13`
3. Environment Variables:
   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | *(generate a random string)* |

### ⚠️ Large Files (Model, Dataset, Cascade)
These files exceed GitHub's 100MB limit and are excluded from git:
- `truck_classifier_v2.h5` (~9MB — small enough, but excluded for safety)
- `Telangana_vehicle_registration_dataset.csv` (~56MB)
- `haarcascade_russian_plate_number.xml` (~74KB — could be committed)

**Solutions:**
- Use [Render Disks](https://render.com/docs/disks) to persist uploaded files
- Or upload via Render Shell after first deploy:
  ```bash
  # In Render Shell
  wget <your-file-url> -O truck_classifier_v2.h5
  ```
- Or store on Google Drive / S3 and download at startup in `app.py`

---

## 💻 Run Locally

```bash
# 1. Clone & enter directory
git clone <your-repo-url>
cd VehicleDetector

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env file
copy .env.example .env     # Windows
# cp .env.example .env     # Mac/Linux

# 5. Place large files in root directory:
#    - truck_classifier_v2.h5
#    - haarcascade_russian_plate_number.xml
#    - Telangana_vehicle_registration_dataset.csv

# 6. Run the app
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## 🌐 Deploy on Heroku

```bash
heroku create vehicledetector-ai
heroku config:set FLASK_ENV=production SECRET_KEY=your-secret-key
git push heroku main
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `Flask` | Web framework |
| `gunicorn` | Production WSGI server |
| `tensorflow` | Vehicle classification model |
| `opencv-python-headless` | Image processing (headless for servers) |
| `easyocr` | Number plate text recognition |
| `fuzzywuzzy` | Fuzzy plate string matching |
| `numpy` | Array operations |

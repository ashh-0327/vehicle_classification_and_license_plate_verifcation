---
title: VehicleDetector AI
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
app_port: 7860
---

#  VehicleDetector AI

A Flask web application that detects whether a vehicle is a **truck or not**, and performs **number plate recognition** with live database lookup.

## Features
- **Vehicle Classification** — TensorFlow CNN model (`truck_classifier_v2.h5`)
- **Plate Recognition** — OpenCV + EasyOCR
- **Database Lookup** — fuzzy-match against Telangana vehicle registration dataset



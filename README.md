# Brain Tumor Detection Flask Application

This web application lets you upload a brain MRI image and receive an instant prediction of the tumor type using a pre-trained deep learning model built with TensorFlow/Keras. It runs a simple Flask server and provides a lightweight UI for image upload and viewing the result.

What it does (at a glance):
- Accepts an MRI image upload (JPG/PNG/JPEG)
- Preprocesses the image to 224×224 RGB and normalizes pixel values
- Runs inference with a CNN model (`.h5`)
- Returns one of four classes: `glioma`, `meningioma`, `no tumor`, `pituitary`

Use cases:
- Quick local demos of medical imaging classification workflows
- Baseline for students learning Flask + TensorFlow deployment
- Starting point for customizing with your own models/datasets

Note: This app is intended for educational and research demonstration only and is not a medical device.

---

## Prerequisites

- Python 3.7 or higher
- `pip` (Python package installer)

---

## Instructions to Set Up and Run the Project

### 1. Clone the Repository
First, clone the repository to your local machine:
```bash
git clone git@github.com:Jay-2704/CMSC_668_brain_tumor_detection.git
```

### 2. Navigate to the Project Directory
Move into the project directory:
```bash
cd CMSC_668_brain_tumor_detection
```

### 3. Install Dependencies
Install the required Python libraries from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Download the Model File
Download the `.h5` model from this Google Drive folder: `https://drive.google.com/drive/folders/12cdcVJYoenwH2WIF_IuYXjKRrFiedDnn`

After downloading, create a `models/` directory (if it does not exist) and place the file there. The application expects the file at:

```
models/Brain_Tumors_vgg_final.h5
```

Example project layout:
```
CMSC_668_brain_tumor_detection/
├── models/
│   └── Brain_Tumors_vgg_final.h5
```

### 5. Your directory will look like

```
CMSC_668_brain_tumor_detection/
├── app.py
├── requirements.txt
├── models/
│   └── Brain_Tumors_vgg_final.h5
├── static/
│   ├── uploads/
│   └── ...
|   └── style.css
├── templates/
│   └── index.html
└── README.md
```

### 6. Run the Flask Application
Run the application using the following command:
```bash
python app.py
```

### 7. Access the Application
Open your browser and navigate to:
```
http://127.0.0.1:5001/
```

---

## Features
- Upload MRI images for brain tumor detection.
- Real-time prediction and visualization.
- User-friendly interface.

---

## How it Works
1. Upload an MRI image via the homepage form.
2. The server saves the image to `static/uploads/`.
3. The image is converted to RGB, resized to 224×224, and normalized to [0, 1].
4. The TensorFlow model at `models/Brain_Tumors_vgg_final.h5` runs inference.
5. The highest-probability class is returned and displayed on the page.

Model input shape: `(1, 224, 224, 3)`

Predicted classes: `glioma`, `meningioma`, `no tumor`, `pituitary`

Routes:
- `/` (GET): Home page and upload form
- `/upload` (POST): Handles image upload and prediction
- `/about` (GET): Project background page
- `/contact` (GET): Contact page

---

## Troubleshooting
- Ensure all dependencies are installed correctly.
- Verify the `model.h5` file is in the `models/` folder.
- If the application doesn't run, check for errors in the terminal and ensure Python is installed correctly.

Additional tips:
- If you see a model loading error, confirm the exact filename is `Brain_Tumors_vgg_final.h5` and the directory is `models/` (relative to `app.py`).
- If the port is in use, edit the `app.run(port=5001, debug=True)` line in `app.py` to another port.
- On Apple Silicon, ensure a compatible TensorFlow build per the official docs if you encounter binary compatibility errors.

---

## License
This project is for educational purposes only. For any other usage, please contact the author.

---

## Credits
- Flask Framework
- TensorFlow/Keras
- Jay and Team
---

## Notes for Customization
- You can replace `models/Brain_Tumors_vgg_final.h5` with your own Keras `.h5` model. Make sure it accepts 224×224 RGB input or update the preprocessing in `app.py` accordingly.
- To display the uploaded image alongside the prediction, use the commented code in `app.py` as a starting point and pass the image URL to the template.


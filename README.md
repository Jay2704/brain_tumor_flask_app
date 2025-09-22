# Brain Tumor Detection Flask Application

This is a Flask application for detecting brain tumors using MRI images. The project uses a pre-trained CNN model (`.h5` file) for predictions.

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
Download the `.h5` model file from [[[[this Google Drive link](https://drive.google.com/dri](https://drive.google.com/drive/folders/12cdcVJYoenwH2WIF_IuYXjKRrFiedDnn?dmr=1&ec=wgc-drive-hero-goto). Once downloaded, move the file to the `models/` directory in your project:
```
CMSC_668_brain_tumor_detection/
├── models/
│   └── model.h5
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

## Troubleshooting
- Ensure all dependencies are installed correctly.
- Verify the `model.h5` file is in the `models/` folder.
- If the application doesn't run, check for errors in the terminal and ensure Python is installed correctly.

---

## License
This project is for educational purposes only. For any other usage, please contact the author.

---

## Credits
- Flask Framework
- TensorFlow/Keras
- Jay and Team
```


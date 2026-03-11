# Brain Tumor Detection AI

## Project Overview

**Brain Tumor Detection AI** is a deep learning-based MRI image classification project built with **TensorFlow** and deployed as a **Hugging Face Space** using **Gradio**.  
The application is designed to provide fast, accessible, and interpretable brain MRI tumor predictions for demonstration and educational purposes.

The model classifies MRI scans into the following categories:

- **Glioma Tumor**
- **Meningioma Tumor**
- **Pituitary Tumor**
- **No Tumor**

This project demonstrates an end-to-end AI workflow: image preprocessing, CNN-based inference, and user-facing deployment.

## Live Demo

The live demo is available on Hugging Face Spaces:

- **Space Name:** `Brain Tumor Detection AI`
- **Demo URL:** _Add your Hugging Face Space URL here_

## Model Architecture

The classifier is a TensorFlow/Keras CNN model trained for 4-class MRI tumor detection.

- **Framework:** TensorFlow / Keras
- **Input Size:** `224 x 224 x 3`
- **Preprocessing:** RGB conversion, resizing to 224x224, normalization to `[0, 1]` by dividing pixel values by 255
- **Output:** Class probabilities across four tumor categories
- **Inference Result:** Predicted label + confidence score

## Dataset

The model is trained on a labeled brain MRI dataset containing images across four classes:

- Glioma Tumor
- Meningioma Tumor
- Pituitary Tumor
- No Tumor

Dataset samples are preprocessed and standardized to maintain consistency during training and inference.

## Technologies Used

- **TensorFlow / Keras** - CNN model training and inference
- **Gradio** - Interactive web interface for image upload and predictions
- **NumPy** - Numerical preprocessing operations
- **Pillow (PIL)** - Image loading and resizing
- **OpenCV (optional in pipeline)** - Additional image processing support
- **Hugging Face Spaces** - Model demo hosting and deployment

## How to Use the Demo

1. Open the Hugging Face Space.
2. Upload a brain MRI image (`.jpg`, `.jpeg`, or `.png`).
3. Click **Submit** (or the prediction button in the UI).
4. Review:
   - Uploaded image preview
   - Predicted tumor class
   - Confidence score

## Future Improvements

- Add model explainability (e.g., Grad-CAM heatmaps) for visual interpretability
- Improve robustness with additional data augmentation and class balancing
- Provide top-k predictions and confidence calibration
- Add DICOM support for clinical-format image workflows
- Include model versioning and experiment tracking for reproducibility
- Expand to multi-condition brain MRI screening in future releases

---

**Note:** This tool is intended for research and portfolio demonstration. It is **not** a certified medical diagnostic system.

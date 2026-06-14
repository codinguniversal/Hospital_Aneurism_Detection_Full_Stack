# RSNA Intracranial Aneurysm Detection 🧠💻

This repository contains an end-to-end AI pipeline for detecting intracranial aneurysms from patient DICOM scans. It uses an ensemble of 3D CNN models (ResNet and EfficientNet backbones) wrapped in a high-performance FastAPI backend, coupled with a user-friendly web interface.

## 🚀 Getting Started

Follow these instructions to set up and run the project locally in your lab environment.

## Prerequisites

- Python 3.8 or higher installed on your system
- Git installed on your system
- **Model Weights:** Due to file size limits, the pre-trained `.pt` model weights are not included in this repository. You must obtain them from the project maintainer via Google Drive or a flash drive.

## Installation & Setup

### 1. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/mohammedayoub968/RSNA-Aneurysm-Detection.git
cd RSNA-Aneurysm-Detection
```

### 2. Add the Model Weights

Create a directory named `model_weights` in the root of the project and place the three required weight files inside it.

Your directory structure should look exactly like this:

```plaintext
RSNA-Aneurysm-Detection/
│
├── model_weights/
│   ├── model12.pt
│   ├── model13.pt
│   └── model25.pt
...
```
link : 
```bash
https://drive.google.com/drive/folders/1XLOjDyLIh7wuGo6SuyDJfGiH3VAHJMZo?usp=drive_link
```

### 3. Create a Virtual Environment

It is highly recommended to use a virtual environment to isolate project dependencies.

```bash
# Create the environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\activate

# Activate the environment (Linux/Mac)
source venv/bin/activate
```

> **Note for Windows users:** If you encounter a script execution error, run the following command first, then try activating again:
>
> ```powershell
> Set-ExecutionPolicy Unrestricted -Scope Process
> ```

### 4. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

### 1. Start the AI Server (Backend)

Run the FastAPI server using Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Wait a few moments until you see the message:

```text
Models loaded successfully! Server is ready.
```

The server will automatically detect if a compatible GPU is available; otherwise, it will fall back to CPU execution.

### 2. Launch the User Interface (Frontend)

1. Navigate to the project folder in your file explorer.
2. Double-click the `index.html` file to open it in your default web browser (Chrome, Edge, Safari, etc.).
3. Click the upload area to select a `.zip` file containing a patient's DICOM (`.dcm`) images.
4. Click **"Analyze Scan"** to start the AI inference.

The system will unpack the files, construct the 3D volume, run the ensemble model with Test Time Augmentation (TTA), and display the overall risk percentage along with detailed branch localizations.

## 💡 Pro Tip for Adding This to GitHub

1. Go to your repository on GitHub.
2. Click the **Add file** button and select **Create new file**.
3. Name the file exactly `README.md`.
4. Paste the content above, scroll down, and click **Commit changes**.

# Hospital Aneurysm Detection System 

An end-to-end medical software suite designed for clinical radiologist workflows. The system automatically ingests 3D DICOM patient head scans, identifies intracranial aneurysms via an ensemble of deep learning 3D CNNs (ResNet & EfficientNet), manages patient/scan records via a FastAPI/MongoDB orchestrator, and presents findings in a web dashboard and native Electron desktop application.

---

##  Repository Structure

The codebase is divided into four main logical components:

*    **[FrontEnd/](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/FrontEnd)**: Vue 3 + Vite client dashboard for clinical radiologists to manage patients, view scans, and trigger AI analysis.
*    **[BackEnd/](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/BackEnd)**: FastAPI core gateway orchestrator responsible for routing authentication, patient data CRUD, scheduling tasks, and forwarding scan packets to the AI pipeline.
*    **[AI Service/](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/AI%20Service)**: FastAPI Python server running the PyTorch 3D CNN ensemble model (loaded from weights) to analyze patient `.zip` archives of DICOM (`.dcm`) scan slices.
*    **[DesktopApp/](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/DesktopApp)**: An Electron wrapper that launches a desktop window pointing to the client interface for local offline clinic integration.

---

## Prerequisites

Ensure the following tools are installed on your machine before setup:
*   **Python**: Version `3.10` or higher
*   **Node.js**: Version `20.x` or `22.x` (Long-Term Support recommended)
*   **MongoDB**: Local server (running on `mongodb://127.0.0.1:27017`) or a MongoDB Atlas URI string.
*   **AI Weights**: Download the PyTorch CNN weight binaries from the project link below and save them inside the AI Service directory:
    *   🔗 **Weights Drive Folder**: [Google Drive Model Weights](https://drive.google.com/drive/folders/1XLOjDyLIh7wuGo6SuyDJfGiH3VAHJMZo?usp=drive_link)
    *   Target Folder Destination: `AI Service/model_weights/` (create this folder if it does not exist)

---

## Quick-Start (Zero Setup Mock Mode)

If you wish to test or demo the system interface quickly without running local MongoDB or downloading large PyTorch models, you can toggle the **Mock Mode** in the backend configuration:

1.  Open **[BackEnd/app/config.py](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/BackEnd/app/config.py)**.
2.  Set `database_mode = "mock"`.
3.  Set `use_mock_ai = True`.
4.  Proceed to spin up **BackEnd** and **FrontEnd** services normally.

---

## Setup & Launch Instructions

Perform the setup steps in the following order:

### 1- Run the AI Service
This service loads PyTorch models to execute inference on uploads.

1.  Navigate to the directory:
    ```bash
    cd "AI Service"
    ```
2.  Download the weight files (`model12.pt`, `model13.pt`, `model25.pt`) from [Google Drive](https://drive.google.com/drive/folders/1XLOjDyLIh7wuGo6SuyDJfGiH3VAHJMZo?usp=drive_link) and put them in a folder called `model_weights`:
    ```plaintext
    AI Service/
    └── model_weights/
        ├── model12.pt
        ├── model13.pt
        └── model25.pt
    ```
3.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Launch the FastAPI server:
    ```bash
    python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
    ```
    *Verification*: The server is ready once you see `Models loaded successfully! Server is ready.` (Interactive swagger docs at `http://127.0.0.1:8001/docs`).

---

### 2- Run the Core BackEnd Orchestrator
The backend connects to MongoDB, schedules scans, manages users, and proxies scans to the AI service.

1.  Navigate to the directory:
    ```bash
    cd ../BackEnd
    ```
2.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  *(Optional but Recommended)* Run the database seed script:
    > [!IMPORTANT]
    > Open **[BackEnd/app/seed.py](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/BackEnd/app/seed.py)** and verify the `NEGATIVE_ZIP_PARENT` and `POSITIVE_ZIP_PARENT` absolute directory paths point to valid zip archives of DICOM scan files on your disk. Alternatively, if you only need user accounts seeded, comment out the patient seeding method calls at the bottom.
    ```bash
    python -m app.seed
    ```
5.  Launch the API gateway orchestrator:
    ```bash
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    ```
    *Verification*: The server runs at `http://127.0.0.1:8000`. API docs can be viewed at `http://127.0.0.1:8000/docs`.

---

### 3- Run the Vue 3 FrontEnd
The UI interfaces with the Core Backend APIs on port 8000.

1.  Navigate to the directory:
    ```bash
    cd ../FrontEnd
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    *Verification*: Open your browser to `http://localhost:5173`. You can log in using the credentials seeded during step 2 (e.g. email: `admin@hospital.com` / password: `SuperSecretAdmin2026!`).

---

### 4- Run the DesktopApp (Electron Wrapper)
If you prefer running a native desktop window integration:

1.  Ensure your Vue 3 Vite server is running at `http://localhost:5173`.
2.  Navigate to the desktop app directory:
    ```bash
    cd ../DesktopApp
    ```
3.  Install dependencies:
    ```bash
    npm install
    ```
4.  Boot up the application:
    ```bash
    npm start
    ```

---

## Configuration & Environment Variables

Settings are declared inside **[BackEnd/app/config.py](file:///home/m-ammar/Documents/GitHub/Hospital_Aneurism_Detection_Full_Stack/BackEnd/app/config.py)**. You can override them by creating a `.env` file in the `BackEnd/` root folder:

*   `database_mode`: `"mongodb"` or `"mock"` (toggles mock in-memory data layer).
*   `use_mock_ai`: `True` or `False` (toggles simulated AI prediction results).
*   `mongodb_uri`: Connection string to MongoDB (defaults to `mongodb://127.0.0.1:27017`).
*   `mongodb_db_name`: Database namespace (defaults to `"CAD_DB"`).
*   `JWT_SECRET`: Secure cryptographic token signing key.
*   `mailtrap_api_token` / `mailtrap_inbox_id`: Mailtrap SMTP/HTTP credentials for hospital scan alerts and notification deliveries.
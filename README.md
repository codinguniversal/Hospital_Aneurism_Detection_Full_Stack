# Graduation Project Full Stack

#  Hospital Aneurysm Detection Backend - Database Setup Guide

This guide ensures all developers have a consistent local environment using MongoDB for development and testing.

---

## Prerequisites & Installation

### 1. MongoDB Community Server (Database Engine)
* **Download Link:** [MongoDB Community Downloads](https://www.mongodb.com/try/download/community)
* Select **Windows**, choose the **MSI** package, and download.
* **Installation Steps (MSI):**
  1. Run the `.msi` installer wizard.
  2. Choose **"Complete"** installation type.
  3. Ensure **"Run service as Network Service user"** is checked (this makes MongoDB run automatically in the background).
  4. Uncheck "Install MongoDB Compass" if you prefer to install it separately, or leave it checked to get a free GUI.

### 2. MongoDB Database Tools (Required for CLI Utilities)
* **Download Link:** [MongoDB Command Line Tools](https://www.mongodb.com/try/download/database-tools)
* Select **Windows**, choose the **ZIP** or **MSI** package.
* *If downloading the ZIP:* Extract it into a permanent folder (e.g., `C:\Program Files\MongoDB\Tools`).
* *If downloading the MSI:* Run the installer, and it will place them automatically into `C:\Program Files\MongoDB\Tools\100\bin`.

---

## ⚙️ Environment Path Configuration

Windows needs to know where commands like `mongodump` live. You must add the tools folder to your system environment variables.

1. Copy the exact path to the `bin` folder where your Database Tools are located:
   * *For MSI Installers (Standard Path):* `C:\Program Files\MongoDB\Tools\100\bin`
   * *For ZIP Installers:* The path to the folder where you unzipped the tools.
2. Press the **Windows Key**, type **"env"**, and select **Edit the system environment variables**.
3. Click **Environment Variables...** at the bottom right.
4. Under **System variables**, select the row named **`Path`** and click **Edit...**.
5. Click **New** and paste the folder path you copied in Step 1.
6. Click **OK** on all windows to save.
7. **CRITICAL:** Close and restart any open terminals or VS Code instances to load the new paths.

---

##  Verifying and Seeding the Database

### 1. Verify CLI Tools Installation
Open a **brand new** PowerShell terminal and run:
```bash
mongodump --version
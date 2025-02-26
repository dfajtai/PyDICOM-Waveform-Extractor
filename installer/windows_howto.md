# Windows build HOWTO

## 1. Install Python  

1. Download a Python installer from the [official Python site](https://www.python.org/downloads/windows/).  
2. Choose your preferred version, e.g.:  
   - [Python 3.13.2 - Feb. 4, 2025](https://www.python.org/downloads/release/python-3132/)  
     - [x64](https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe)  
     - [x32](https://www.python.org/ftp/python/3.13.2/python-3.13.2.exe)  
3. Run the installer and **select "Add to PATH"** during the install procedure.

⚠️ **Note:** Remember the Python version you installed, as it will be needed later. (Tested for Python >= 3.10.)
---

## 2. Clone This Repository  

### Option 1: Using Git  
```sh
git clone https://github.com/dfajtai/PyDICOM-Waveform-Extractor.git
```

### Option 2: Download Manually
- [Download the latest version](https://github.com/dfajtai/PyDICOM-Waveform-Extractor/archive/refs/heads/main.zip)
- Extract the ZIP file to your desired location.

---

## 3. Build and Run  

### Step 1: Navigate to the Build Folder  
1. Open a terminal (Command Prompt or PowerShell).  
2. Change directory to the `installer` folder:  
   ```sh
   cd path/to/PyDICOM-Waveform-Extractor/installer
   ```

### Step 2: Set Up the Environment
1. Ensure the correct Python version is set in the 'create_env.bat' file.
  ```sh
  set PYTHON_VERSION=3.13
  ```
2. Run the 'create_env.bat' script to set up the required environment variables:
  ```sh
  create_env.bat
  ```

This script configures the necessary paths and dependencies.

### Step 3: Build the Project
1. Execute the build.bat script to compile/build the project:
  ```sh
  build.bat
  ```

This will prepare all necessary components for running the software.

### Step 3 Alternative: Run the project inside the Virtual Environment
1. Execute the windows_no_build_ran.bat file:
  ```sh
  windows_no_build_run.bat
  ```

---
_"PyDICOM-Waveform-Extractor: Because reading the manual is hard."_  

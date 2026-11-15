# ⚙️ AI Production Scheduler & Bottleneck Predictor

An intelligent production planning assistant built with **Python**, **Pandas**, **Streamlit**, and **Groq LLM (Llama 3)**. This application helps production planners simulate work orders, calculate On-Time Delivery (**OTD**) risks, identify factory bottlenecks, and interact with an AI assistant via natural language to optimize scheduling.

---

## 🚀 Key Features

* **Real-time OTD Risk Analysis:** Automatically calculates capacity load per production line and flags orders at risk of delay due to processing time or raw material shortages.
* **Interactive Dashboard:** Built with **Streamlit** for instant data visualization, color-coded status tables, and KPI metrics.
* **Work Order Management:** Easily add new work orders via the sidebar form, which instantly updates the dataset and recalculates bottlenecks.
* **AI Planner Assistant (Groq LLM):** Powered by ultra-fast Groq inference (`llama-3.3-70b-versatile`), allowing planners to ask natural language "What-if" questions and receive structured, actionable recommendations.

---

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **Data Processing:** Pandas
* **Web Frontend:** Streamlit
* **AI / LLM Integration:** Groq API (Llama 3)


---

## 📂 Project Structure

'''text
ai-production-scheduler/
│
├── data/
    ├── machines_capacity.csv    # Simulated ERP work orders, machines and stock dataset, can be edited in app or manually in Notepad, Excel
    ├── raw_materials_stock.csv
│   └── work_orders.csv       
├── app.py                       # Streamlit frontend & UI logic
├── backend.py                   # Core planning logic, OTD calculation & Groq API
├── requirements.txt             # Python dependencies
├── .env                         # your Groq API key
└── README.md                    # Project documentation 


---


## 📦 Running on Another Computer (Portable Version)

If you want to run this application on a target machine that **does not have Python or a pre-configured environment installed**, you can use the portable folder structure.

### Step 1: Prepare the `Aplication_Package` Directory

Create a folder named `Aplication_Package` with the following layout:

```text
Aplication_Package/
│
├── python/                  # Extracted Python 3.12 Embeddable package
│   └── Lib/
│       └── site-packages/   # Required dependencies (Streamlit, Pandas, Groq, etc.)
│
├── data/                    # Folder containing your local CSV data files
├── app.py                   # Main Streamlit application script
├── backend.py               # Data processing & AI logic script
├── .env                     # Configuration file containing your GROQ_API_KEY
└── pokreni.bat              # Batch launch script


### Step 2: **Downloading Portable Python:**
   - Download the official *Python Windows embeddable package (64-bit)* for version 3.12 from the official website.
   - unpack embeddable Python into Aplication_Package and manually add `Lib/site-packages` folder from your virtual env containing all the necessary libraries, such as Streamlit, Pandas, Groq, etc.)
   - In the root directory of the `python/` folder, open the file ending in `._pth` (e.g., `python312._pth`) in Notepad, ensure that the line `import site` is uncommented, and, if necessary, add the following to the bottom: Lib/site-packages

### Step 3: Configure the .bat Launcher (Open_app.bat)
Ensure your Open_app.bat script contains the following commands:

@echo off
chcp 65001 >nul
echo Starting AI Production Scheduler...

REM Set path to prioritize the portable Python interpreter
set "PATH=%~dp0python;%~dp0python\Scripts;%PATH%"

cd /d "%~dp0"

REM Run Streamlit app
python -m streamlit run app.py

pause


### Step 4: Launching the App
Transfer the entire Aplication_Package folder to the target machine (via USB drive, network share, etc.).

Double-click on Open_app.bat.

The server will start, and the application will automatically open in your default web browser.

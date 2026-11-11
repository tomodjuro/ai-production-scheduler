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

```text
ai-production-scheduler/
│
├── data/
    ├── machines_capacity.csv    # Simulated ERP work orders, machines and stock dataset
    ├── raw_materials_stock.csv
│   └── work_orders.csv       
├── app.py                       # Streamlit frontend & UI logic
├── backend.py                   # Core planning logic, OTD calculation & Groq API
├── requirements.txt             # Python dependencies
├── .env                         # your Groq API key
└── README.md                    # Project documentation

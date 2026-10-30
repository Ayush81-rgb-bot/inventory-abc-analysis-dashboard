# 🚚 Logistics KPI Dashboard (Portfolio Project)

An interactive, executive-grade Supply Chain & Logistics KPI Dashboard built using **Streamlit**, **Pandas**, and **Plotly**. 

This application visualizes carrier performance, fleet capacity utilization, freight cost dynamics across corridors, and customer delivery compliance (OTIF).

![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.20+-3F4F75?style=for-the-badge&logo=Plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=Pandas&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=Python&logoColor=white)

---

## 🎯 Key Features

1. **Executive KPI Metric Cards**:
   - **Total Trips**: Real-time count of fleet dispatches.
   - **Average Turnaround Time (TAT_Days)**: Average elapsed transit days from dispatch to delivery.
   - **Average Truck Utilization %**: Mean payload weight loaded vs. truck rated capacity.
   - **Overall OTIF %**: On-Time In-Full fulfillment rate, reflecting service reliability.

2. **Interactive Visualizations (Plotly)**:
   - **Transporter-wise Average TAT**: Bar chart comparing carrier cycle times to identify prompt vs. lagging partners.
   - **Lane-wise Average Freight Cost Per Unit**: Horizontal ranked bar chart evaluating transit route economics.

3. **Dynamic Filtering & Resiliency**:
   - Sidebar multi-select for **Transporter** (with optional Lane drill-down).
   - Graceful empty-state error handling when filters are cleared.
   - Instant filter reset button.

4. **Data Explorer & Insights**:
   - Detailed shipment explorer with full record inspection.
   - One-click CSV export of filtered dataset.
   - Integrated Logistics KPI Reference Dictionary.

---

## 📁 Project Structure

```text
├── app.py                         # Streamlit dashboard application
├── logistics_dashboard_data.csv    # 500-record logistics shipment dataset
├── requirements.txt               # Dependencies for local and cloud deployment
└── README.md                      # Project documentation and deployment guide
```

---

## 🚀 Quickstart: Run Locally

### 1. Clone or Navigate to the Directory
```bash
cd /path/to/kpi
```

### 2. Install Required Libraries
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit App
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repository to **GitHub**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**.
4. Select your repository, branch (`main`), and set the main file path to `app.py`.
5. Click **"Deploy!"** — your dashboard will be live on the web in seconds!

---

## 📊 Logistics KPI Reference Guide

| Metric | Business Definition | Formula |
| :--- | :--- | :--- |
| **TAT (Days)** | Total turnaround time from dispatch to actual delivery | `Actual_Delivery_Date - Dispatch_Date` |
| **Utilization %** | Percentage of vehicle weight capacity utilized | `(Loaded_Weight_kg / Truck_Capacity_kg) * 100` |
| **On-Time %** | Deliveries made on or before target date | `Count(On_Time == True) / Total Trips * 100` |
| **In-Full %** | Deliveries where delivered qty equals ordered qty | `Count(In_Full == True) / Total Trips * 100` |
| **OTIF %** | Deliveries that were BOTH On-Time AND In-Full | `Count(OTIF_Status == True) / Total Trips * 100` |
| **Cost / Unit** | Unit freight transport cost efficiency | `Total_Freight_Cost / Delivered_Qty` |

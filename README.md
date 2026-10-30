# 📦 Inventory & ABC Analysis Dashboard (Portfolio Project)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Ayush81-rgb-bot/inventory-abc-analysis-dashboard&branch=main&mainModule=app.py)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=Python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.20+-3F4F75?style=for-the-badge&logo=Plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=Pandas&logoColor=white)

An interactive, executive-grade Supply Chain & Inventory Analytics Dashboard built using **Streamlit**, **Plotly**, and **Pandas**. 

This application visualizes inventory value concentration using the **Pareto Principle (ABC Analysis)**, monitors stock health metrics (**Days of Cover**), and flags replenishment priorities with dynamic **Reorder Points (ROP)** and **Safety Stock buffers**.

---

## 🎯 Key Dashboard Features

1. **Executive KPI Cards**:
   - **Total SKUs**: Total active items in the selected scope and catalog representation.
   - **Total Inventory Value**: Aggregate annual consumption value (e.g., `$352.78M`) with full precision breakdown.
   - **Average Days of Cover**: Mean buffer duration across products with min/max spread.
   - **Class A Value Share**: Real-time Pareto metric highlighting value captured by high-priority items.

2. **Interactive Visualizations (Plotly)**:
   - **ABC SKU Distribution (Donut Chart)**: Visual breakdown of catalog SKU count and percentage across Classes A, B, and C with custom brand coloring.
   - **Annual Demand vs. Unit Cost (Pareto Scatter Plot)**: Multi-dimensional scatter plot highlighting the Pareto curve, color-coded by ABC classification, with bubble size proportional to Annual Value.

3. **Reorder Alerts Table (Top 20 SKUs)**:
   - Filtered view prioritized by highest annual monetary volume.
   - Displays critical replenishment metrics: **Safety Stock (SS)**, **Reorder Point (ROP)**, **Days of Cover**, and **Lead Time**.
   - One-click CSV export button for procurement teams.

4. **Dynamic Filtering & Resilient Architecture**:
   - Sidebar multi-select filters for **Product Category** and **ABC Class**.
   - Instant "Reset All" and "Clear All" controls.
   - **Graceful Empty State Handling**: User-friendly warning banners and zeroed metric fallbacks if all filters are cleared without application crashes.

5. **Integrated Data Explorer & Methodology Guide**:
   - Complete dataset inspection and full CSV export.
   - Supply chain formula reference for Annual Value, Daily Demand, Safety Stock, and ROP.

---

## 📁 Repository Structure

```text
├── app.py                             # Streamlit dashboard application
├── inventory_analysis_calculated.csv   # 200-SKU calculated inventory dataset
├── requirements.txt                   # Production dependencies
└── README.md                          # Project documentation
```

---

## 🚀 Quickstart: Run Locally

### 1. Clone or Navigate to the Directory
```bash
git clone https://github.com/Ayush81-rgb-bot/inventory-abc-analysis-dashboard.git
cd inventory-abc-analysis-dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
The dashboard will open automatically in your default browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

Click the badge above or use the direct deployment link:
👉 **[Deploy on Streamlit Community Cloud](https://share.streamlit.io/deploy?repository=Ayush81-rgb-bot/inventory-abc-analysis-dashboard&branch=main&mainModule=app.py)**

1. Push your repository to **GitHub**:
   ```bash
   git add .
   git commit -m "Deploy Inventory & ABC Analysis Dashboard"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**.
4. Select `Ayush81-rgb-bot/inventory-abc-analysis-dashboard`, branch `main`, and main file path `app.py`.
5. Click **"Deploy!"** — your portfolio dashboard will be live on the web in seconds.

---

## 📊 Business Methodology & Inventory Formulae

| Metric | Formula | Definition |
| :--- | :--- | :--- |
| **Annual Value** | $\text{Annual Demand} \times \text{Unit Cost}$ | Total annual monetary throughput per SKU |
| **Avg Daily Demand ($\bar{D}$)** | $\frac{\text{Annual Demand}}{365}$ | Baseline daily consumption rate |
| **Safety Stock ($SS$)** | $Z \times \sqrt{(\bar{L} \times \sigma_D^2) + (\bar{D}^2 \times \sigma_L^2)}$ | Buffer protecting against lead time & demand variation ($Z=1.65$ for 95% service level) |
| **Reorder Point ($ROP$)** | $(\bar{D} \times \bar{L}) + SS$ | Inventory threshold triggering replenishment order |
| **Days of Cover** | $\frac{SS}{\bar{D}}$ | Inventory buffer duration in operational demand days |

---

## 🏷️ ABC Classification Rules (Pareto 80/20)

- **Class A (~80% of Value, ~10-20% of SKUs):** Mission-critical products. Requires tight cycle counts, strict lead-time adherence, and continuous monitoring.
- **Class B (~15% of Value, ~30% of SKUs):** Moderate-volume items. Standard periodic inventory review and automated replenishment.
- **Class C (~5% of Value, ~50% of SKUs):** High-variety, low-value items. Simple, bulk ordering policies to minimize order processing costs.

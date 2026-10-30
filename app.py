import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Logistics KPI Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for executive cards and sleek UI
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        margin-bottom: 15px;
        transition: transform 0.15s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-subtext {
        font-size: 0.8rem;
        color: #475569;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .badge-info {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        background: #e0f2fe;
        color: #0369a1;
    }
    .badge-success {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        background: #dcfce7;
        color: #15803d;
    }
    /* Section dividers */
    .custom-divider {
        margin-top: 10px;
        margin-bottom: 25px;
        border-bottom: 1px solid #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. Data Loading & Preprocessing
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "logistics_dashboard_data.csv"
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    
    # Parse date columns
    date_cols = ["Dispatch_Date", "Target_Delivery_Date", "Actual_Delivery_Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            
    # Ensure boolean columns are standardized
    bool_cols = ["On_Time", "In_Full", "OTIF_Status"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)
            
    return df


df_raw = load_data()

# Graceful fallback if dataset is missing
if df_raw is None:
    st.error("⚠️ Dataset `logistics_dashboard_data.csv` was not found in the workspace.")
    uploaded_file = st.file_uploader("Upload logistics_dashboard_data.csv to continue:", type=["csv"])
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
    else:
        st.stop()


# -----------------------------------------------------------------------------
# 3. Sidebar Filtering
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/delivery-truck.png",
        width=70,
    )
    st.title("Logistics Controls")
    st.caption("Supply Chain & Fleet Analytics")
    st.markdown("---")

    # Multi-select Transporter Filter (Required)
    all_transporters = sorted(df_raw["Transporter"].dropna().unique().tolist())
    
    st.subheader("Filter by Carrier")
    selected_transporters = st.multiselect(
        "Select Transporter(s):",
        options=all_transporters,
        default=all_transporters,
        help="Choose one or more carriers to inspect KPI performance."
    )

    # Optional Lane filter for enhanced drill-down
    all_lanes = sorted(df_raw["Lane"].dropna().unique().tolist())
    selected_lanes = st.multiselect(
        "Select Lane(s) (Optional):",
        options=all_lanes,
        default=all_lanes,
        help="Optionally refine analysis across specific transit corridors."
    )

    st.markdown("---")
    
    # Filter helper reset quick action
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("### 📌 Portfolio Project")
    st.caption(
        "**Logistics KPI Dashboard**\n"
        "Engineered with Streamlit & Plotly\n"
        "Showcases Fleet Turnaround, Capacity Utilization, and OTIF Service Level."
    )


# -----------------------------------------------------------------------------
# 4. Filter Validation & Empty State Handling
# -----------------------------------------------------------------------------
if not selected_transporters:
    st.warning("⚠️ **No Transporter Selected**: Please select at least one transporter from the sidebar filter to view KPIs and visualizations.")
    st.info("💡 *Tip: Check 'Select Transporter(s)' in the sidebar on the left to restore data display.*")
    st.stop()

# Apply Filters
filtered_df = df_raw[
    (df_raw["Transporter"].isin(selected_transporters)) &
    (df_raw["Lane"].isin(selected_lanes))
]

if filtered_df.empty:
    st.warning("⚠️ **No Matching Records**: No shipments match the combination of selected transporters and lanes. Please broaden your selection.")
    st.stop()


# -----------------------------------------------------------------------------
# 5. Header Section
# -----------------------------------------------------------------------------
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("🚚 Logistics & Fleet KPI Performance Dashboard")
    st.markdown(
        "Monitor end-to-end supply chain execution, turnaround cycle times, freight economics, and customer delivery compliance."
    )
with header_col2:
    st.markdown(
        f"""
        <div style="text-align: right; padding-top: 18px;">
            <span class="badge-info">Active Carriers: {len(selected_transporters)}/{len(all_transporters)}</span><br>
            <span class="badge-success" style="margin-top: 6px;">Trips Filtered: {len(filtered_df):,}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. Top-Level KPI Metric Cards (4 Key Metrics)
# -----------------------------------------------------------------------------
total_trips = len(filtered_df)
avg_tat = filtered_df["TAT_Days"].mean()
avg_utilization = filtered_df["Utilization_Pct"].mean()
otif_pct = (filtered_df["OTIF_Status"].mean()) * 100

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">📦 Total Trips</div>
            <div class="metric-value">{total_trips:,}</div>
            <div class="metric-subtext">Completed fleet dispatches</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    tat_badge = "badge-success" if avg_tat <= 6.0 else "badge-info"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">⏱️ Average Turnaround</div>
            <div class="metric-value">{avg_tat:.1f} <span style="font-size: 1.1rem; font-weight: 500;">Days</span></div>
            <div class="metric-subtext"><span class="{tat_badge}">Benchmark: &le;6.0 Days</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    util_badge = "badge-success" if avg_utilization >= 75.0 else "badge-info"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">⚖️ Avg Truck Utilization</div>
            <div class="metric-value">{avg_utilization:.1f}%</div>
            <div class="metric-subtext"><span class="{util_badge}">Target: &ge;75% Capacity</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    otif_color = "badge-success" if otif_pct >= 50.0 else "badge-info"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">🎯 Overall OTIF %</div>
            <div class="metric-value">{otif_pct:.1f}%</div>
            <div class="metric-subtext"><span class="{otif_color}">On-Time & In-Full Deliveries</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 7. Visualizations Section
# -----------------------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

# --- Visualization 1: Transporter-wise Average TAT ---
with col_chart1:
    st.subheader("Transporter-wise Average TAT")
    
    # Group and calculate mean TAT
    df_transporter_tat = (
        filtered_df.groupby("Transporter", as_index=False)["TAT_Days"]
        .mean()
        .round(2)
        .sort_values(by="TAT_Days", ascending=False)
    )

    fig_tat = px.bar(
        df_transporter_tat,
        x="Transporter",
        y="TAT_Days",
        text="TAT_Days",
        color="TAT_Days",
        color_continuous_scale="Blues",
        labels={"TAT_Days": "Average TAT (Days)", "Transporter": "Transporter Name"},
        title="Average Turnaround Time (TAT) by Transporter",
    )

    fig_tat.update_traces(
        texttemplate="%{text:.2f} d",
        textposition="outside",
        cliponaxis=False,
        marker_line_color="#1e293b",
        marker_line_width=1,
    )
    
    fig_tat.update_layout(
        template="plotly_white",
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="", tickfont=dict(size=12, color="#334155")),
        yaxis=dict(
            title="Avg TAT (Days)",
            range=[0, max(df_transporter_tat["TAT_Days"].max() * 1.25, 5)],
            gridcolor="#f1f5f9",
        ),
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig_tat, use_container_width=True)


# --- Visualization 2: Lane-wise Average Freight Cost Per Unit ---
with col_chart2:
    st.subheader("Lane-wise Average Freight Cost Per Unit")

    # Group and calculate mean Cost Per Unit
    df_lane_cost = (
        filtered_df.groupby("Lane", as_index=False)["Cost_Per_Unit"]
        .mean()
        .round(2)
        .sort_values(by="Cost_Per_Unit", ascending=True)  # Ascending so highest is top in horizontal chart
    )

    fig_cost = px.bar(
        df_lane_cost,
        x="Cost_Per_Unit",
        y="Lane",
        orientation="h",
        text="Cost_Per_Unit",
        color="Cost_Per_Unit",
        color_continuous_scale="Teal",
        labels={"Cost_Per_Unit": "Avg Cost Per Unit (₹)", "Lane": "Transit Lane"},
        title="Average Freight Cost Per Unit across Transit Corridors",
    )

    fig_cost.update_traces(
        texttemplate="₹%{text:.2f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_color="#0f766e",
        marker_line_width=1,
    )

    fig_cost.update_layout(
        template="plotly_white",
        height=420,
        margin=dict(l=20, r=40, t=50, b=20),
        xaxis=dict(
            title="Avg Freight Cost / Unit (₹)",
            range=[0, max(df_lane_cost["Cost_Per_Unit"].max() * 1.25, 20)],
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(title="", tickfont=dict(size=12, color="#334155")),
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig_cost, use_container_width=True)


# -----------------------------------------------------------------------------
# 8. Portfolio Exploratory & Data Table Section
# -----------------------------------------------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

tab_overview, tab_data, tab_dictionary = st.tabs([
    "📈 Operational Summary",
    "📋 Shipment Data Explorer",
    "📖 KPI Dictionary & Formulas"
])

with tab_overview:
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    
    with sum_col1:
        fastest_transporter = df_transporter_tat.sort_values("TAT_Days").iloc[0]
        st.info(
            f"⚡ **Fastest Carrier**: **{fastest_transporter['Transporter']}** "
            f"with an average TAT of **{fastest_transporter['TAT_Days']:.2f} days**."
        )

    with sum_col2:
        most_economical_lane = df_lane_cost.sort_values("Cost_Per_Unit").iloc[0]
        st.success(
            f"💰 **Most Economical Lane**: **{most_economical_lane['Lane']}** "
            f"averaging **₹{most_economical_lane['Cost_Per_Unit']:.2f} per unit**."
        )

    with sum_col3:
        on_time_pct = (filtered_df["On_Time"].mean()) * 100
        in_full_pct = (filtered_df["In_Full"].mean()) * 100
        st.markdown(
            f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px;">
                <div style="font-size: 0.82rem; font-weight: 600; color: #475569;">Delivery Breakdown</div>
                <div style="font-size: 0.9rem; color: #0f172a; margin-top: 4px;">
                    • <b>On-Time Delivery Rate:</b> {on_time_pct:.1f}%<br>
                    • <b>In-Full Quantity Fulfillment:</b> {in_full_pct:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with tab_data:
    st.write(f"Showing **{len(filtered_df):,}** shipments matching your filter criteria:")
    
    # Display styled dataframe
    st.dataframe(
        filtered_df[[
            "Trip_ID", "Transporter", "Lane", "Dispatch_Date", "Actual_Delivery_Date",
            "TAT_Days", "Utilization_Pct", "Cost_Per_Unit", "On_Time", "In_Full", "OTIF_Status"
        ]],
        use_container_width=True,
        hide_index=True,
    )
    
    # Download filtered CSV
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Shipments CSV",
        data=csv_data,
        file_name="filtered_logistics_kpi_data.csv",
        mime="text/csv",
    )

with tab_dictionary:
    st.markdown(
        """
        ### 📊 Logistics KPI Reference Guide
        
        | KPI | Description | Formula / Business Logic |
        | :--- | :--- | :--- |
        | **Total Trips** | Aggregate number of dispatched shipments within the selected scope | `Count(Trip_ID)` |
        | **Turnaround Time (TAT)** | Total elapsed time in days from carrier dispatch to final delivery arrival | `Actual_Delivery_Date - Dispatch_Date` |
        | **Truck Utilization %** | Percentage of truck payload weight capacity utilized per trip | `(Loaded_Weight_kg / Truck_Capacity_kg) * 100` |
        | **On-Time Rate %** | Deliveries fulfilled on or before the target committed delivery date | `(Count(On_Time == True) / Total Trips) * 100` |
        | **In-Full Rate %** | Deliveries where delivered volume fully satisfies ordered volume | `(Count(In_Full == True) / Total Trips) * 100` |
        | **OTIF %** | Ultimate gold-standard logistics service metric: On-Time AND In-Full | `(Count(On_Time == True & In_Full == True) / Total Trips) * 100` |
        | **Freight Cost / Unit** | Unit transport logistics cost for landed cargo efficiency | `Total_Freight_Cost / Delivered_Qty` |
        """
    )

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & LAYOUT
# ==============================================================================
st.set_page_config(
    page_title="Inventory & ABC Analysis Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CUSTOM CSS STYLING
# ==============================================================================
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        margin-bottom: 12px;
        transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.95rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-subtext {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Section Subheadings */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Dark mode adaptability */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: #1e293b;
            border-color: #334155;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
        }
        .metric-title {
            color: #94a3b8;
        }
        .metric-value {
            color: #f8fafc;
        }
        .metric-subtext {
            color: #94a3b8;
        }
        .section-header {
            color: #f1f5f9;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. COLOR PALETTE CONSTANTS
# ==============================================================================
ABC_COLOR_MAP = {
    "A": "#10B981",  # Emerald Green (High Value)
    "B": "#F59E0B",  # Amber Gold (Moderate Value)
    "C": "#6366F1",  # Indigo Blue (Low Value)
}

# ==============================================================================
# 4. DATA INGESTION & CACHING
# ==============================================================================
@st.cache_data
def load_data(filepath: str = "inventory_analysis_calculated.csv") -> pd.DataFrame:
    """
    Load and preprocess the calculated inventory analysis dataset.
    Ensures robust path resolution for both local and Streamlit Cloud environments.
    """
    if not os.path.exists(filepath):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(base_dir, filepath)
        if os.path.exists(alt_path):
            filepath = alt_path
        else:
            raise FileNotFoundError(f"Dataset not found at '{filepath}' or '{alt_path}'.")
    
    df = pd.read_csv(filepath)
    
    numeric_cols = [
        "Unit_Cost", "Annual_Demand", "Avg_Daily_Demand", "Std_Dev_Demand",
        "Avg_Lead_Time_Days", "Std_Dev_Lead_Time", "Annual_Value",
        "Cum_Value", "Cum_Value_Pct", "Safety_Stock", "Reorder_Point",
        "Days_of_Cover"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    if "ABC_Class" in df.columns:
        df["ABC_Class"] = df["ABC_Class"].astype(str).str.strip().str.upper()
    
    return df

# Load primary dataset
try:
    raw_df = load_data()
except Exception as e:
    st.error(f"Failed to load inventory dataset: {e}")
    st.stop()

TOTAL_BASE_SKUS = len(raw_df)
TOTAL_BASE_VALUE = raw_df["Annual_Value"].sum()

# ==============================================================================
# 5. SIDEBAR CONTROLS & MULTI-SELECT FILTERS
# ==============================================================================
with st.sidebar:
    st.title("Filters")
    st.markdown("Filter catalog by **Category** and **ABC Classification**.")
    st.markdown("---")

    all_categories = sorted(raw_df["Category"].dropna().unique().tolist())
    all_abc_classes = ["A", "B", "C"]

    # Filter reset handlers using session_state
    def reset_to_all():
        st.session_state["category_filter"] = all_categories
        st.session_state["abc_filter"] = all_abc_classes

    def clear_all_filters():
        st.session_state["category_filter"] = []
        st.session_state["abc_filter"] = []

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Reset All", on_click=reset_to_all, use_container_width=True)
    with btn_col2:
        st.button("Clear All", on_click=clear_all_filters, use_container_width=True)

    # Multi-select 1: Category
    selected_categories = st.multiselect(
        label="Product Category",
        options=all_categories,
        default=st.session_state.get("category_filter", all_categories),
        key="category_filter",
        help="Select one or more categories."
    )

    # Multi-select 2: ABC Class
    selected_abc = st.multiselect(
        label="ABC Class",
        options=all_abc_classes,
        default=st.session_state.get("abc_filter", all_abc_classes),
        key="abc_filter",
        help="A: Top ~80% Value (Critical) | B: ~15% Value (Moderate) | C: ~5% Value (Low)"
    )

    st.markdown("---")

    # Apply filters
    filtered_df = raw_df[
        (raw_df["Category"].isin(selected_categories)) &
        (raw_df["ABC_Class"].isin(selected_abc))
    ].copy()

    # Dynamic scope summary
    active_count = len(filtered_df)
    st.markdown("### Portfolio Scope")
    st.markdown(f"- **Active SKUs:** `{active_count}` of `{TOTAL_BASE_SKUS}` ({active_count / TOTAL_BASE_SKUS * 100:.1f}%)")
    if not filtered_df.empty:
        filtered_val = filtered_df["Annual_Value"].sum()
        st.markdown(f"- **Active Value:** `${filtered_val:,.2f}`")
        st.markdown(f"- **Portfolio Share:** `{filtered_val / TOTAL_BASE_VALUE * 100:.1f}%`")
    else:
        st.markdown("- **Active Value:** `$0.00`")
        st.markdown("- **Portfolio Share:** `0.0%`")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #64748b; line-height: 1.4;">
            <strong>Data Analytics Portfolio</strong><br>
            Inventory & ABC Analysis Dashboard<br>
            Built with Streamlit, Plotly & Pandas.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# 6. MAIN CONTENT HEADER
# ==============================================================================
st.title("📦 Inventory & ABC Analysis Dashboard")
st.markdown(
    "An executive analytics dashboard evaluating **SKU classification (Pareto principle)**, "
    "**annual inventory valuation**, and **reorder replenishment targets (Safety Stock & Reorder Points)**."
)

# ==============================================================================
# 7. EMPTY STATE GRACEFUL HANDLING
# ==============================================================================
if filtered_df.empty:
    st.warning(
        "⚠️ **No data available for the selected filters.**\n\n"
        "Please select at least one **Category** and one **ABC Class** from the sidebar to display metrics and charts."
    )
    
    # Render fallback zeroed KPI cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Total SKUs</div>
                <div class="metric-value">0</div>
                <div class="metric-subtext">0.0% of catalog</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Total Inventory Value</div>
                <div class="metric-value">$0.00</div>
                <div class="metric-subtext">Sum of Annual Value: $0.00</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Average Days of Cover</div>
                <div class="metric-value">0.0 Days</div>
                <div class="metric-subtext">No active items in scope</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Class A Value Share</div>
                <div class="metric-value">0.0%</div>
                <div class="metric-subtext">Pareto high-value concentration</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.button("Reset Filters to Default", on_click=reset_to_all)
    st.stop()

# ==============================================================================
# 8. TOP-LEVEL KPI METRICS
# ==============================================================================
total_skus = len(filtered_df)
total_value = filtered_df["Annual_Value"].sum()
avg_days_of_cover = filtered_df["Days_of_Cover"].mean()

# Pareto Class A Value Share
class_a_val = filtered_df[filtered_df["ABC_Class"] == "A"]["Annual_Value"].sum()
class_a_share = (class_a_val / total_value * 100) if total_value > 0 else 0.0

# Value formatting
if total_value >= 1_000_000:
    formatted_val = f"${total_value / 1_000_000:,.2f}M"
elif total_value >= 1_000:
    formatted_val = f"${total_value / 1_000:,.1f}K"
else:
    formatted_val = f"${total_value:,.2f}"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    sku_pct = (total_skus / TOTAL_BASE_SKUS) * 100
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total SKUs</div>
            <div class="metric-value">{total_skus:,}</div>
            <div class="metric-subtext">{sku_pct:.1f}% of catalog ({TOTAL_BASE_SKUS} items)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    val_pct = (total_value / TOTAL_BASE_VALUE) * 100
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total Inventory Value</div>
            <div class="metric-value">{formatted_val}</div>
            <div class="metric-subtext">${total_value:,.2f} ({val_pct:.1f}% of total)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    min_doc = filtered_df["Days_of_Cover"].min()
    max_doc = filtered_df["Days_of_Cover"].max()
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Average Days of Cover</div>
            <div class="metric-value">{avg_days_of_cover:.1f} <span style="font-size:1.1rem; font-weight:500; color:#64748b;">Days</span></div>
            <div class="metric-subtext">Range: {min_doc:.1f}d to {max_doc:.1f}d</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    class_a_count = len(filtered_df[filtered_df["ABC_Class"] == "A"])
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Class A Value Share</div>
            <div class="metric-value">{class_a_share:.1f}%</div>
            <div class="metric-subtext">{class_a_count} Class A items drive majority value</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 9. INTERACTIVE VISUALIZATIONS (PLOTLY)
# ==============================================================================
chart_col1, chart_col2 = st.columns([4, 6])

with chart_col1:
    st.markdown("<div class='section-header'>🍩 Distribution of SKUs across ABC Classes</div>", unsafe_allow_html=True)
    
    donut_df = (
        filtered_df.groupby("ABC_Class", as_index=False)
        .agg(
            SKU_Count=("SKU_ID", "count"),
            Total_Value=("Annual_Value", "sum")
        )
    )
    
    donut_df["Sort_Key"] = donut_df["ABC_Class"].map({"A": 1, "B": 2, "C": 3})
    donut_df = donut_df.sort_values("Sort_Key").drop(columns=["Sort_Key"])
    
    fig_donut = px.pie(
        donut_df,
        names="ABC_Class",
        values="SKU_Count",
        hole=0.55,
        color="ABC_Class",
        color_discrete_map=ABC_COLOR_MAP,
        category_orders={"ABC_Class": ["A", "B", "C"]}
    )
    
    fig_donut.update_traces(
        textposition="inside",
        textinfo="label+percent",
        textfont_size=13,
        marker=dict(line=dict(color="#ffffff", width=2)),
        hovertemplate="<b>Class %{label}</b><br>" +
                      "SKU Count: %{value:,}<br>" +
                      "Share of SKUs: %{percent}<br>" +
                      "<extra></extra>"
    )
    
    fig_donut.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=380,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        annotations=[
            dict(
                text=f"<b>{total_skus}</b><br><span style='font-size:12px; color:#64748b;'>SKUs</span>",
                x=0.5, y=0.5,
                font=dict(size=18, color="#0f172a"),
                showarrow=False
            )
        ]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with chart_col2:
    st.markdown("<div class='section-header'>📈 Annual Demand vs. Unit Cost (Pareto Principle)</div>", unsafe_allow_html=True)
    
    fig_scatter = px.scatter(
        filtered_df,
        x="Annual_Demand",
        y="Unit_Cost",
        color="ABC_Class",
        color_discrete_map=ABC_COLOR_MAP,
        category_orders={"ABC_Class": ["A", "B", "C"]},
        hover_name="SKU_ID",
        hover_data={
            "Category": True,
            "Annual_Demand": ":,",
            "Unit_Cost": ":$.2f",
            "Annual_Value": ":$,.2f",
            "Safety_Stock": ":.0f",
            "Reorder_Point": ":.0f",
            "Days_of_Cover": ":.1f",
            "ABC_Class": True
        },
        size="Annual_Value",
        size_max=22,
        opacity=0.85
    )
    
    fig_scatter.update_traces(
        marker=dict(line=dict(width=1, color="#ffffff"))
    )
    
    fig_scatter.update_layout(
        margin=dict(t=20, b=20, l=40, r=20),
        height=380,
        xaxis=dict(
            title="<b>Annual Demand</b> (Units / Year)",
            gridcolor="#f1f5f9",
            zeroline=False
        ),
        yaxis=dict(
            title="<b>Unit Cost</b> ($ / Unit)",
            gridcolor="#f1f5f9",
            zeroline=False,
            tickprefix="$"
        ),
        legend=dict(
            title=dict(text="<b>ABC Class</b>"),
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 10. REORDER ALERTS SECTION (TOP 20 BY ANNUAL VALUE)
# ==============================================================================
st.markdown("<div class='section-header'>🚨 Reorder Alerts: Top 20 Items by Annual Value</div>", unsafe_allow_html=True)
st.caption(
    "High-priority inventory replenishment watchlist. Focus on maintaining required "
    "**Safety Stock buffers** and monitoring **Reorder Points (ROP)** to avoid costly stockouts."
)

# Extract top 20 items sorted by Annual Value descending
top_20_reorder = (
    filtered_df.sort_values(by="Annual_Value", ascending=False)
    .head(20)
    .copy()
)

display_cols = [
    "SKU_ID",
    "Category",
    "ABC_Class",
    "Annual_Value",
    "Annual_Demand",
    "Unit_Cost",
    "Safety_Stock",
    "Reorder_Point",
    "Days_of_Cover",
    "Avg_Lead_Time_Days"
]

table_df = top_20_reorder[display_cols].reset_index(drop=True)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "SKU_ID": st.column_config.TextColumn("SKU ID", width="medium"),
        "Category": st.column_config.TextColumn("Category"),
        "ABC_Class": st.column_config.TextColumn("ABC Class", width="small"),
        "Annual_Value": st.column_config.NumberColumn(
            "Annual Value ($)",
            format="$%.2f",
            help="Annual Demand x Unit Cost"
        ),
        "Annual_Demand": st.column_config.NumberColumn(
            "Annual Demand",
            format="%d units",
            help="Total annual unit demand"
        ),
        "Unit_Cost": st.column_config.NumberColumn(
            "Unit Cost ($)",
            format="$%.2f",
            help="Acquisition cost per unit"
        ),
        "Safety_Stock": st.column_config.NumberColumn(
            "Safety Stock",
            format="%.0f units",
            help="Buffer stock to absorb demand and lead-time variability"
        ),
        "Reorder_Point": st.column_config.NumberColumn(
            "Reorder Point (ROP)",
            format="%.0f units",
            help="Replenishment trigger: (Avg Daily Demand x Lead Time) + Safety Stock"
        ),
        "Days_of_Cover": st.column_config.NumberColumn(
            "Days of Cover",
            format="%.1f days",
            help="Safety buffer duration in operational demand days"
        ),
        "Avg_Lead_Time_Days": st.column_config.NumberColumn(
            "Lead Time",
            format="%d days",
            help="Supplier procurement lead time in days"
        )
    }
)

csv_reorder = table_df.to_csv(index=False).encode("utf-8")
col_dl1, col_dl2 = st.columns([2, 8])
with col_dl1:
    st.download_button(
        label="📥 Download Top 20 Alerts (CSV)",
        data=csv_reorder,
        file_name="top_20_reorder_alerts.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_dl2:
    st.caption(f"Displaying top {len(table_df)} items by Annual Value from current filtered selection of {len(filtered_df)} SKUs.")

# ==============================================================================
# 11. COMPREHENSIVE DATA EXPLORER & METHODOLOGY GUIDE
# ==============================================================================
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

with st.expander("🔍 Explore Complete Filtered Dataset & Export"):
    st.markdown(f"**Filtered Records:** `{len(filtered_df)}` SKUs")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "Annual_Value": st.column_config.NumberColumn(format="$%.2f"),
            "Unit_Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Cum_Value": st.column_config.NumberColumn(format="$%.2f"),
            "Cum_Value_Pct": st.column_config.NumberColumn(format="%.2f%%"),
            "Safety_Stock": st.column_config.NumberColumn(format="%.0f"),
            "Reorder_Point": st.column_config.NumberColumn(format="%.0f"),
            "Days_of_Cover": st.column_config.NumberColumn(format="%.1f"),
        }
    )
    full_csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Filtered Dataset (CSV)",
        data=full_csv,
        file_name="filtered_inventory_analysis.csv",
        mime="text/csv"
    )

with st.expander("📘 Business Methodology & Inventory Formulae"):
    st.markdown(
        """
        ### 🎯 ABC Classification & The Pareto Principle
        ABC analysis segments inventory into three categories based on annual monetary volume:
        - **Class A (~80% of Total Value, ~10-20% of SKUs):** Tight inventory control, frequent cycle counts, proactive replenishment, and strict vendor lead-time monitoring.
        - **Class B (~15% of Total Value, ~30% of SKUs):** Routine inventory management with automated reordering triggers.
        - **Class C (~5% of Total Value, ~50% of SKUs):** Simplified stock policies, bulk orders to leverage volume discounts and minimize transaction costs.

        ---

        ### 📐 Inventory Calculations
        - **Annual Value:** `Annual Demand * Unit Cost`
        - **Average Daily Demand:** `Annual Demand / 365`
        - **Safety Stock (SS):** Buffer against lead-time and demand variance:
          `Z * sqrt( (Lead_Time * Var_Demand) + (Demand^2 * Var_Lead_Time) )` (at 95% service level, Z = 1.65)
        - **Reorder Point (ROP):** `(Avg Daily Demand * Avg Lead Time) + Safety Stock`
        - **Days of Cover:** `Safety Stock / Avg Daily Demand`
        """
    )

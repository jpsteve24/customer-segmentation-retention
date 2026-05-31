import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Customer Segmentation & Retention Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

.metric-card {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
}

.sidebar .sidebar-content {
    background-color: #111827;
}

.stButton>button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("📊 E-Commerce Customer Segmentation & Retention Dashboard")

st.markdown("""
Advanced customer analytics platform using:
- Customer Segmentation
- Churn Analysis
- Sales Forecasting
- Market Basket Analysis
- Business Intelligence
""")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

try:
    customer_df = pd.read_csv("outputs/customer_segments.csv")
    sales_df = pd.read_csv("outputs/sales_forecast.csv")
    rules_df = pd.read_csv("outputs/association_rules.csv")

    # --------------------------------------------
    # RENAME CUSTOMER CLUSTERS
    # --------------------------------------------

    cluster_names = {
        0: "💎 VIP Customers",
        1: "⚠️ Churn Risk Customers",
        2: "🛍️ Regular Customers",
        3: "❤️ Loyal Customers"
    }

    if "Cluster" in customer_df.columns:
        customer_df["Customer Segment"] = (
            customer_df["Cluster"].map(cluster_names)
        )

except FileNotFoundError as e:
    st.error(f"{e.filename} not found.")
    st.stop()
# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.title("📌 Dashboard Navigation")

section = st.sidebar.radio(
    "Select Section",
    [
        "Overview",
        "Customer Segments",
        "Churn Analysis",
        "CLV Analysis",
        "Sales Forecast",
        "Customer Data",
        "Market Basket Analysis",
        "Business Recommendations"
    ]
)

# ---------------------------------------------------
# PERSONA FILTER
# ---------------------------------------------------
if "Persona" in customer_df.columns:

    personas = customer_df["Persona"].unique()

    selected_persona = st.sidebar.selectbox(
        "🎯 Customer Persona",
        ["All"] + list(personas)
    )

    if selected_persona != "All":
        customer_df = customer_df[
            customer_df["Persona"] == selected_persona
        ]

# ---------------------------------------------------
# KPI METRICS
# ---------------------------------------------------
total_customers = len(customer_df)

avg_spending = 0
if "Monetary" in customer_df.columns:
    avg_spending = round(customer_df["Monetary"].mean(), 2)

segment_count = 0
if "Cluster" in customer_df.columns:
    segment_count = customer_df["Cluster"].nunique()

# ---------------------------------------------------
# OVERVIEW SECTION
# ---------------------------------------------------
if section == "Overview":

    st.header("📈 Business Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Customers", total_customers)
    col2.metric("💰 Avg Spending", avg_spending)
    col3.metric("🧩 Customer Segments", segment_count)

    st.subheader("📊 Cluster Distribution")

    if "Cluster" in customer_df.columns:

        fig = px.histogram(
            customer_df,
            x="Customer Segment",
            color="Customer Segment",
            title="Customer Segment Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔥 Spending Distribution")

    if "Monetary" in customer_df.columns:

        fig = px.box(
            customer_df,
            y="Monetary",
            color="Customer Segment" if "Cluster" in customer_df.columns else None,
            title="Customer Spending Analysis"
        )

        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# CUSTOMER SEGMENTS
# ---------------------------------------------------
elif section == "Customer Segments":

    st.header("👥 Customer Segmentation Analysis")

    st.dataframe(customer_df.head())

    numeric_cols = customer_df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    selected_feature = st.selectbox(
        "Select Feature",
        numeric_cols
    )

    if "Cluster" in customer_df.columns:

        fig = px.box(
            customer_df,
            x="Customer Segment",
            y=selected_feature,
            color="Customer Segment",
            title=f"{selected_feature} Across Customer Segments"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📌 Correlation Heatmap")

    corr = customer_df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)

# ---------------------------------------------------
# CHURN ANALYSIS
# ---------------------------------------------------
# ---------------------------------------------------
# CHURN ANALYSIS
# ---------------------------------------------------
elif section == "Churn Analysis":

    st.header("⚠️ Customer Churn Analysis")

    st.markdown("""
    Customers with:
    - low purchase frequency
    - low recency
    - declining spending
    are considered high churn risk.
    """)

    st.dataframe(customer_df.head())

    if "Cluster" in customer_df.columns:

        churn_counts = customer_df["Cluster"].value_counts()

        fig = px.pie(
            values=churn_counts.values,
            names=churn_counts.index,
            title="Customer Risk Segments"
        )

        st.plotly_chart(fig, use_container_width=True)

    numeric_cols = customer_df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    if len(numeric_cols) > 0:

        selected_metric = st.selectbox(
            "Select Churn Metric",
            numeric_cols
        )

        fig = px.histogram(
            customer_df,
            x=selected_metric,
            color="Customer Segment" if "Cluster" in customer_df.columns else None,
            title=f"{selected_metric} Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    if "Monetary" in customer_df.columns:

        fig = px.box(
            customer_df,
            x="Customer Segment" if "Cluster" in customer_df.columns else None,
            y="Monetary",
            color="Customer Segment" if "Cluster" in customer_df.columns else None,
            title="Customer Spending vs Churn Risk"
        )

        st.plotly_chart(fig, use_container_width=True)
# ---------------------------------------------------
# SALES FORECAST
# ---------------------------------------------------
elif section == "Sales Forecast":

    st.header("📉 Sales Forecasting")

    st.dataframe(sales_df.head())

    if len(sales_df.columns) >= 2:

        x_col = sales_df.columns[0]
        y_col = sales_df.columns[1]

        fig = px.line(
            sales_df,
            x=x_col,
            y=y_col,
            title="Sales Forecast Trend"
        )

        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------
# MARKET BASKET ANALYSIS
# ---------------------------------------------------
elif section == "Market Basket Analysis":

    st.header("🛒 Market Basket Analysis")

    st.dataframe(rules_df.head())

    available_cols = rules_df.columns.tolist()

    st.write("Available Columns:", available_cols)

    if "lift" in rules_df.columns:

        top_rules = rules_df.sort_values(
            by="lift",
            ascending=False
        ).head(10)

        fig = px.bar(
            top_rules,
            x="lift",
            y=top_rules.index.astype(str),
            orientation="h",
            title="Top Product Associations"
        )

        st.plotly_chart(fig, use_container_width=True)

    if (
        "support" in rules_df.columns and
        "confidence" in rules_df.columns and
        "lift" in rules_df.columns
    ):

        fig = px.scatter(
            rules_df,
            x="support",
            y="confidence",
            size="lift",
            title="Association Rule Strength"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(
            "Scatter plot unavailable because support/confidence/lift columns are missing."
        )

# ---------------------------------------------------
# BUSINESS RECOMMENDATIONS
# ---------------------------------------------------
elif section == "Business Recommendations":

    st.header("💡 Strategic Business Recommendations")

    st.markdown("""
    ### 🎯 Customer Retention
    - Focus on high-risk churn customers
    - Introduce personalized loyalty programs
    - Offer targeted discounts for inactive customers

    ### 🛍️ Product Recommendations
    - Use market basket analysis for cross-selling
    - Recommend complementary products
    - Create bundle offers

    ### 📈 Revenue Optimization
    - Focus marketing on high-value customers
    - Increase retention for premium customer segments
    - Optimize pricing based on purchasing behavior

    ### 🚀 Future Improvements
    - Real-time customer analytics
    - AI recommendation engine
    - Deep learning churn prediction
    - Cloud deployment pipelines
    """)

# ---------------------------------------------------
# CUSTOMER DATA
# ---------------------------------------------------
elif section == "Customer Data":

    st.header("🧾 Customer Dataset Explorer")

    st.dataframe(customer_df)

    st.subheader("Dataset Information")

    info_df = pd.DataFrame({
        "Column": customer_df.columns,
        "Data Type": customer_df.dtypes.astype(str)
    })

    st.dataframe(info_df)

    st.subheader("Missing Values")

    missing_df = pd.DataFrame({
        "Column": customer_df.columns,
        "Missing Values": customer_df.isnull().sum()
    })

    st.dataframe(missing_df)

# ---------------------------------------------------
# CLV ANALYSIS
# ---------------------------------------------------
elif section == "CLV Analysis":

    st.header("💰 Customer Lifetime Value Analysis")

    if "Monetary" in customer_df.columns:

        customer_df["CLV"] = (
            customer_df["Monetary"] * 12
        )

        st.dataframe(
            customer_df[["CustomerID", "Monetary", "CLV"]].head()
        )

        fig = px.histogram(
            customer_df,
            x="CLV",
            nbins=30,
            title="Customer Lifetime Value Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        top_customers = customer_df.sort_values(
            by="CLV",
            ascending=False
        ).head(10)

        fig = px.bar(
            top_customers,
            x="CustomerID",
            y="CLV",
            title="Top High Value Customers"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Monetary column not found.")
# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.markdown("Built By JP Steve Akash")

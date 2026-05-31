git
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3 {
    color: #FFFFFF;
}

.stMetric {
    background-color: #1E1E1E;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("📊 E-Commerce Customer Segmentation & Retention Dashboard")

st.markdown("""
### 🚀 Advanced Customer Intelligence Platform

This dashboard includes:

- 👥 Customer Segmentation
- ⚠️ Churn Analysis
- 💰 CLV Analysis
- 📈 Sales Forecasting
- 🛒 Market Basket Analysis
- 💡 Business Intelligence
""")

# =========================================================
# LOAD DATA
# =========================================================
try:
    customer_df = pd.read_csv("outputs/customer_segments.csv")
except:
    st.error("❌ customer_segments.csv not found in outputs folder")
    st.stop()

try:
    sales_df = pd.read_csv("outputs/sales_forecast.csv")
except:
    sales_df = pd.DataFrame()

try:
    rules_df = pd.read_csv("outputs/association_rules.csv")
except:
    rules_df = pd.DataFrame()

# =========================================================
# RENAME CUSTOMER CLUSTERS
# =========================================================
cluster_names = {
    0: "💎 VIP Customers",
    1: "⚠️ Churn Risk Customers",
    2: "🛍 Regular Customers",
    3: "❤️ Loyal Customers"
}

if "Cluster" in customer_df.columns:
    customer_df["Customer Segment"] = (
        customer_df["Cluster"].map(cluster_names)
    )

# =========================================================
# SIDEBAR
# =========================================================
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

# =========================================================
# PERSONA FILTER
# =========================================================
if "Customer Segment" in customer_df.columns:

    persona = st.sidebar.selectbox(
        "🎭 Customer Persona",
        ["All"] + list(customer_df["Customer Segment"].dropna().unique())
    )

    if persona != "All":
        customer_df = customer_df[
            customer_df["Customer Segment"] == persona
        ]

# =========================================================
# KPI METRICS
# =========================================================
st.subheader("📈 Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Customers", len(customer_df))

with col2:
    if "Monetary" in customer_df.columns:
        st.metric(
            "💰 Avg Revenue",
            f"${customer_df['Monetary'].mean():.2f}"
        )

with col3:
    if "Frequency" in customer_df.columns:
        st.metric(
            "🛒 Avg Purchase Frequency",
            round(customer_df["Frequency"].mean(), 2)
        )

with col4:
    if "Recency" in customer_df.columns:
        st.metric(
            "📅 Avg Recency",
            round(customer_df["Recency"].mean(), 2)
        )

# =========================================================
# OVERVIEW
# =========================================================
if section == "Overview":

    st.header("🚀 Business Overview")

    if (
        "Frequency" in customer_df.columns and
        "Monetary" in customer_df.columns
    ):

        fig = px.scatter(
            customer_df,
            x="Frequency",
            y="Monetary",
            color="Customer Segment",
            title="💸 Customer Spending Behaviour",
            hover_data=["Recency"]
        )

        st.plotly_chart(fig, use_container_width=True)

    if "Customer Segment" in customer_df.columns:

        segment_count = (
            customer_df["Customer Segment"]
            .value_counts()
            .reset_index()
        )

        segment_count.columns = ["Segment", "Count"]

        fig = px.pie(
            segment_count,
            names="Segment",
            values="Count",
            title="📊 Customer Segment Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# CUSTOMER SEGMENTS
# =========================================================
elif section == "Customer Segments":

    st.header("👥 Customer Segmentation Analysis")

    st.dataframe(customer_df.head())

    numeric_cols = customer_df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    selected_feature = st.selectbox(
        "📌 Select Feature",
        numeric_cols
    )

    if "Customer Segment" in customer_df.columns:

        fig = px.box(
            customer_df,
            x="Customer Segment",
            y=selected_feature,
            color="Customer Segment",
            title=f"📊 {selected_feature} Across Customer Segments"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔥 Correlation Heatmap")

    corr = customer_df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)

# =========================================================
# CHURN ANALYSIS
# =========================================================
elif section == "Churn Analysis":

    st.header("⚠️ Customer Churn Analysis")

    if "Recency" in customer_df.columns:

        customer_df["Churn Risk"] = np.where(
            customer_df["Recency"] >
            customer_df["Recency"].median(),
            "High Risk",
            "Low Risk"
        )

        churn_counts = (
            customer_df["Churn Risk"]
            .value_counts()
            .reset_index()
        )

        churn_counts.columns = ["Risk", "Count"]

        fig = px.bar(
            churn_counts,
            x="Risk",
            y="Count",
            color="Risk",
            title="📉 Churn Risk Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# CLV ANALYSIS
# =========================================================
elif section == "CLV Analysis":

    st.header("💰 Customer Lifetime Value Analysis")

    if (
        "Frequency" in customer_df.columns and
        "Monetary" in customer_df.columns
    ):

        customer_df["CLV"] = (
            customer_df["Frequency"] *
            customer_df["Monetary"]
        )

        fig = px.histogram(
            customer_df,
            x="CLV",
            color="Customer Segment",
            nbins=30,
            title="💎 Customer Lifetime Value Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏆 Top Customers by CLV")

        top_customers = customer_df.sort_values(
            by="CLV",
            ascending=False
        ).head(10)

        st.dataframe(top_customers)

# =========================================================
# SALES FORECAST
# =========================================================
elif section == "Sales Forecast":

    st.header("📈 Sales Forecasting Dashboard")

    if not sales_df.empty:

        st.subheader("📋 Forecast Dataset")
        st.dataframe(sales_df.head())

        numeric_cols = sales_df.select_dtypes(
            include=["int64", "float64"]
        ).columns

        # ------------------------------------------------
        # KPI METRICS
        # ------------------------------------------------
        st.subheader("📊 Forecast KPIs")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "💰 Total Forecast Sales",
                f"${sales_df[numeric_cols[1]].sum():,.2f}"
            )

        with col2:
            st.metric(
                "📈 Average Forecast",
                f"${sales_df[numeric_cols[1]].mean():,.2f}"
            )

        with col3:
            st.metric(
                "🚀 Peak Forecast",
                f"${sales_df[numeric_cols[1]].max():,.2f}"
            )

        # ------------------------------------------------
        # FORECAST LINE CHART
        # ------------------------------------------------
        st.subheader("📈 Forecast Trend")

        fig = px.line(
            sales_df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            markers=True,
            title="Sales Forecast Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------------
        # BAR CHART
        # ------------------------------------------------
        st.subheader("📊 Forecast Distribution")

        fig = px.bar(
            sales_df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            color=numeric_cols[1],
            title="Forecasted Sales Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------------
        # MOVING AVERAGE
        # ------------------------------------------------
        st.subheader("📉 Moving Average Trend")

        sales_df["Moving Average"] = (
            sales_df[numeric_cols[1]]
            .rolling(window=3)
            .mean()
        )

        fig = px.line(
            sales_df,
            x=numeric_cols[0],
            y="Moving Average",
            title="Moving Average Sales Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------------
        # HISTOGRAM
        # ------------------------------------------------
        st.subheader("📦 Sales Frequency Distribution")

        fig = px.histogram(
            sales_df,
            x=numeric_cols[1],
            nbins=20,
            title="Forecast Sales Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ sales_forecast.csv not found")


# =========================================================
# CUSTOMER DATA
# =========================================================
elif section == "Customer Data":

    st.header("📋 Customer Dataset Explorer")

    st.dataframe(customer_df)

    st.subheader("📊 Dataset Information")

    info_df = pd.DataFrame({
        "Column": customer_df.columns,
        "Data Type": customer_df.dtypes.astype(str)
    })

    st.dataframe(info_df)

# =========================================================
# MARKET BASKET ANALYSIS
# =========================================================
elif section == "Market Basket Analysis":

    st.header("🛒 Market Basket Analysis")

    if not rules_df.empty:

        st.subheader("📦 Association Rules")

        st.dataframe(rules_df.head())

        required_columns = [
            "support",
            "confidence",
            "lift"
        ]

        if all(col in rules_df.columns for col in required_columns):

            fig = px.scatter(
                rules_df,
                x="support",
                y="confidence",
                size="lift",
                color="lift",
                hover_name="antecedents",
                title="📊 Association Rule Strength Analysis"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(
                "⚠️ Required columns missing in association_rules.csv"
            )

    else:
        st.warning("⚠️ association_rules.csv not found")

# =========================================================
# BUSINESS RECOMMENDATIONS
# =========================================================
elif section == "Business Recommendations":

    st.header("💡 Strategic Business Recommendations")

    st.markdown("""
### 🎯 Customer Retention Strategies
- Focus on high-risk churn customers
- Create personalized loyalty campaigns
- Offer targeted discount coupons

### 🛍 Product Recommendation Strategies
- Use market basket analysis for cross-selling
- Suggest complementary products
- Create bundle offers

### 📈 Revenue Optimization
- Focus marketing on VIP customers
- Improve loyal customer retention
- Increase customer lifetime value

### 🚀 Future Enhancements
- AI-powered recommendation engine
- Real-time analytics dashboard
- Automated campaign optimization
- Deep learning-based churn prediction
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown(
    "Built By JP Steve Akash"
)

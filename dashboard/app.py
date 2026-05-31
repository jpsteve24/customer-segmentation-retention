import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
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

h1, h2, h3, h4 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #333333;
}

.sidebar .sidebar-content {
    background-color: #111111;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

rfm_path = "../outputs/customer_segments.csv"

if os.path.exists(rfm_path):
    rfm = pd.read_csv(rfm_path)
else:
    st.error("customer_segments.csv not found.")
    st.stop()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("📌 Navigation")

section = st.sidebar.radio(
    "Go To",
    [
        "Overview",
        "Customer Segments",
        "Churn Analysis",
        "CLV Analysis",
        "Sales Forecasting",
        "Market Basket Analysis",
        "Customer Data",
        "Business Recommendations"
    ]
)

# Persona Filter
persona_filter = st.sidebar.multiselect(
    "Filter by Persona",
    options=rfm["Persona"].unique(),
    default=rfm["Persona"].unique()
)

filtered_rfm = rfm[rfm["Persona"].isin(persona_filter)]

# ---------------------------------------------------
# KPI METRICS
# ---------------------------------------------------

total_customers = filtered_rfm.shape[0]
average_clv = filtered_rfm["CLV"].mean()
high_risk = (filtered_rfm["ChurnRisk"] == "High Risk").sum()
avg_frequency = filtered_rfm["Frequency"].mean()

# ---------------------------------------------------
# OVERVIEW SECTION
# ---------------------------------------------------

if section == "Overview":

    st.title("📈 Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Average CLV", f"{average_clv:.2f}")
    col3.metric("High Risk Customers", high_risk)
    col4.metric("Avg Purchase Frequency", f"{avg_frequency:.2f}")

    st.markdown("---")

    # Persona Distribution
    st.subheader("Customer Persona Distribution")

    fig1 = px.histogram(
        filtered_rfm,
        y="Persona",
        color="Persona",
        title="Distribution of Customer Personas"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Revenue by Persona
    st.subheader("Revenue Contribution by Persona")

    revenue_data = (
        filtered_rfm.groupby("Persona")["Monetary"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        revenue_data,
        x="Persona",
        y="Monetary",
        color="Persona",
        title="Revenue by Persona"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# CUSTOMER SEGMENTS
# ---------------------------------------------------

elif section == "Customer Segments":

    st.title("👥 Customer Segments")

    fig3 = px.scatter(
        filtered_rfm,
        x="Frequency",
        y="Monetary",
        color="Persona",
        size="CLV",
        hover_data=["CustomerID"],
        title="Customer Segmentation Scatter Plot"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------
# CHURN ANALYSIS
# ---------------------------------------------------

elif section == "Churn Analysis":

    st.title("⚠️ Churn Analysis")

    churn_counts = (
        filtered_rfm["ChurnRisk"]
        .value_counts()
        .reset_index()
    )

    churn_counts.columns = ["ChurnRisk", "Count"]

    fig4 = px.pie(
        churn_counts,
        names="ChurnRisk",
        values="Count",
        title="Churn Risk Distribution"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------
# CLV ANALYSIS
# ---------------------------------------------------

elif section == "CLV Analysis":

    st.title("💰 Customer Lifetime Value Analysis")

    fig5 = px.histogram(
        filtered_rfm,
        x="CLV",
        nbins=40,
        title="CLV Distribution"
    )

    st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------
# SALES FORECASTING
# ---------------------------------------------------

elif section == "Sales Forecasting":

    st.title("📉 Future Sales Forecast")

    forecast_path = "../outputs/sales_forecast.csv"

    if os.path.exists(forecast_path):

        sales_forecast = pd.read_csv(forecast_path)

        fig_forecast = px.line(
            sales_forecast,
            x="ds",
            y="yhat",
            title="Predicted Future Sales"
        )

        fig_forecast.update_layout(
            xaxis_title="Date",
            yaxis_title="Predicted Sales"
        )

        st.plotly_chart(fig_forecast, use_container_width=True)

        st.subheader("Forecast Data Preview")
        st.dataframe(sales_forecast.tail())

    else:
        st.warning("sales_forecast.csv not found.")

# ---------------------------------------------------
# MARKET BASKET ANALYSIS
# ---------------------------------------------------

elif section == "Market Basket Analysis":

    st.title("🛒 Market Basket Analysis")

    rules_path = "../outputs/association_rules.csv"

    if os.path.exists(rules_path):

        rules = pd.read_csv(rules_path)

        # Check if rules dataframe is empty
        if rules.empty:

            st.warning(
                "No association rules generated. "
                "Dataset too small or support threshold too high."
            )

        else:

            st.subheader("Association Rules")

            st.dataframe(rules.head(20))

            # Convert columns safely
            rules["support"] = pd.to_numeric(
                rules["support"],
                errors="coerce"
            )

            rules["confidence"] = pd.to_numeric(
                rules["confidence"],
                errors="coerce"
            )

            rules["lift"] = pd.to_numeric(
                rules["lift"],
                errors="coerce"
            )

            # Remove invalid rows
            rules = rules.dropna(
                subset=["support", "confidence", "lift"]
            )

            if rules.empty:

                st.warning(
                    "No valid rules available for visualization."
                )

            else:

                fig_rules = px.scatter(
                    rules,
                    x="support",
                    y="confidence",
                    size="lift",
                    color="lift",
                    hover_data=["lift"],
                    title="Association Rule Strength"
                )

                st.plotly_chart(
                    fig_rules,
                    use_container_width=True
                )

    else:
        st.warning("association_rules.csv not found.")

# ---------------------------------------------------
# CUSTOMER DATA
# ---------------------------------------------------

elif section == "Customer Data":

    st.title("📄 Customer Data Preview")

    st.dataframe(filtered_rfm)

# ---------------------------------------------------
# BUSINESS RECOMMENDATIONS
# ---------------------------------------------------

elif section == "Business Recommendations":

    st.title("💡 Business Recommendations")

    st.markdown("""
    ### Key Insights & Recommendations

    #### 🎯 VIP Customers
    - Offer premium loyalty rewards
    - Provide early product access
    - Use personalized marketing campaigns

    #### ⚠️ At-Risk Customers
    - Launch retention campaigns
    - Offer discount coupons
    - Send personalized email reminders

    #### 🛒 Budget Buyers
    - Promote bundle offers
    - Target with seasonal discounts

    #### 📈 Sales Forecasting
    - Expected future revenue trend is increasing
    - Plan inventory accordingly

    #### 🧠 Market Basket Insights
    - Frequently purchased products can be bundled
    - Improve cross-selling strategy
    """)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown("""
### About This Project

Built by JP Steve Akash

#### Technologies Used:
- Python
- Streamlit
- Pandas
- Scikit-learn
- Prophet
- Plotly
- Seaborn
- Matplotlib
""")
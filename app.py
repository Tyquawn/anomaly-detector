import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Financial Anomaly Detector")
st.write("Enter a company's SEC number to check for earnings manipulation risk.")

cik = st.text_input("SEC CIK Number", "320193")

if st.button("Analyze"):
    st.write("Fetching data from SEC EDGAR...")
    cik_padded = str(cik).zfill(10)
    url = "https://data.sec.gov/api/xbrl/companyfacts/CIK" + cik_padded + ".json"
    headers = {"User-Agent": "yourname@email.com"}
    r = requests.get(url, headers=headers)
    data = r.json()
    company_name = data["entityName"]
    st.write("Company: " + company_name)
    revenues = data["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
    df = pd.DataFrame(revenues)
    df = df[df["form"] == "10-K"]
    df = df[["start", "end", "val"]].tail(10)
    df.columns = ["Start", "End", "Revenue"]
    df["Revenue"] = df["Revenue"] / 1000000000
    fig = px.bar(df, x="End", y="Revenue", title="Annual Revenue (billions)")
    st.plotly_chart(fig)
    st.subheader("Earnings Manipulation Risk")
    revenue_values = df["Revenue"].values
    if len(revenue_values) >= 2:
        growth = (revenue_values[-1] - revenue_values[-2]) / revenue_values[-2]
        if growth > 0.1:
            st.error("⚠️ High revenue growth detected: " + str(round(growth * 100, 1)) + "%. Warrants closer review.")
        else:
            st.success("✅ Revenue growth looks normal: " + str(round(growth * 100, 1)) + "%")

import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Load the Dataset
sheet_id = "1okER7T-pSffxHfqkm_imKEkJpV7pVx3-wNOjpUuxVr8"
gid = "0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(url)
# Renaming the column name as per standard
df.columns = df.columns.str.replace(" ","_")
df = df.rename(columns={"Plot_Size_(SQFT)_Actual":"Plot_Size_Actual","Plot_Size_(SQFT)_TNCP":"Plot_Size_TNCP","Diff_(Actual_-_TNCP)":"Diff_Size"})
df.columns = df.columns.str.lower()

# Clean the Dataset
df["rate"] = df["rate"].str.replace(",","")
df["amount_received"] = df["amount_received"].str.replace(",","")

# Change the data types
df = df.astype({'rate':'float', 'plot_price':'float',
       'amount_received':'float', 'receivable':'float',
       'registry_number':'str','contact_number':"str",
       'cheque_number':'str'})

# Fill NaN with 0
df = df.fillna(0)

# Select township for working
township = st.sidebar.selectbox("Township:",df["township_name"].unique())
st.header(township)

# Display KPI's Crad
col5,col6,col7,col8 = st.columns(4)

with col5:
    with st.container(border=True,height="stretch"):
       total_plots = df[df["township_name"] == township]["plot_size_actual"].sum()
       st.markdown("**Total Size(SQFT)**")
       st.markdown(f"##### {total_plots:.0f}")
with col6:
    with st.container(border=True,height="stretch"):
       total_sales = df[df["township_name"] == township]["plot_price"].agg("sum")
       st.markdown("**Total Sales**")
       st.markdown(f"##### {total_sales:,}")
with col7:
    with st.container(border=True,height="stretch"):
       total_received = df[df["township_name"] == township]["amount_received"].sum()
       st.markdown("**Total Received**")
       st.markdown(f"##### {total_received:,}")
with col8:
    with st.container(border=True,height="stretch"):
       total_receivable = df[df["township_name"] == township]["receivable"].sum()
       st.markdown("**Total Receivable**")
       st.markdown(f"##### {total_receivable:,}")
st.markdown("---")
# Making filter Columns
owner = st.sidebar.multiselect(
        "Owner:",
        options= df[df["township_name"] == township]["ownership"].unique(),
        default=df[df["township_name"] == township]["ownership"].unique()
)
status =st.sidebar.multiselect(
        "Status:",
        options= df[df["township_name"] == township]["status"].unique(),
        default=df[df["township_name"] == township]["status"].unique()
)
registry_status =st.sidebar.multiselect(
        "Registry Status:",
        options= df[df["township_name"] == township]["registry_status"].unique(),
        default=df[df["township_name"] == township]["registry_status"].unique()
)

col = st.multiselect("Select columns:",df.columns)


if st.button("Filter Data"):
    df_selection = df.query(
        "ownership == @owner & status ==@status & registry_status == registry_status"
    )
    st.dataframe(df_selection[df_selection["township_name"]== township][col])
else:
    df_selection = df.query(
        "ownership == @owner & status ==@status & registry_status == registry_status"
    )
    st.dataframe(df_selection[df_selection["township_name"]== township])




import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# ---- Sidebar Title ----
st.sidebar.title("Filters")
# ---- Sidebar Font Size Styling ----
st.markdown("""
<style>
/* Sidebar label text */
section[data-testid="stSidebar"] label {
    font-size: 24px !important;
    font-weight: 600;
}

/* Sidebar multiselect selected values */
section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    font-size: 14px !important;
    background-color: #87CEFA !important;
    color: #000000 !important;
}

/* Sidebar multiselect dropdown options */
section[data-testid="stSidebar"] ul li {
    font-size: 14px !important;
    background-color: #6A89A7 !important;
}
/* Sidebar header */
section[data-testid="stSidebar"] .css-1d391kg h2 {
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* background color of sidebar */
section[data-testid="stSidebar"] {
    background-color: #40E0D0;
}
/* background color of main area */
section[data-testid="stMain"] {
    background-color: #01B8AA;
}
/* Main Area Header*/
section[data-testid="stMain"] .css-1d391kg h1 {
    font-size: 24px !important;
}

/* KPI container styling */
div[role="listitem"] {
    background-color: #40E0D0;
}
/* full page background color */
body {
    background-color: #01B8AA;

</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="Township Dashboard", page_icon=":bar_chart:", layout="wide")

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
df["rate"] = df["rate"].str.replace('',"")
df["amount_received"] = df["amount_received"].str.replace(",","")
df["amount_received"] = df["amount_received"].str.replace('',"")
df["plot_price"] = df["plot_price"].str.replace(",","")
df["plot_price"] = df["plot_price"].str.replace('',"")
df["receivable"] = df["receivable"].str.replace(",","")
df["receivable"] = df["receivable"].str.replace('',"")

# Change the data types
df = df.astype({'rate':'float', 'plot_price':'float',
       'amount_received':'float', 'receivable':'float',
       'registry_number':'str','contact_number':"str",
       'cheque_number':'str'})

# Fill NaN with 0
df = df.fillna(0)
df = df.drop(columns="id")
df = df.set_index("plot_no.")

# Select township for working
township = st.sidebar.selectbox("Township:",df["township_name"].unique())
st.header(township)

# Making filter Columns

owner = st.sidebar.multiselect(
        "Owner:",
        options= df[df["township_name"] == township]["ownership"].unique(),
        default=df[df["township_name"] == township]["ownership"].unique(),
        label_visibility="visible"
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


# Display KPI's based on Township and ownership

col5,col6,col7,col8 = st.columns(4)

with col5:
    with st.container(border=True,height="stretch"):
       total_plots = df[(df["township_name"] == township) & (df["ownership"].isin(owner))]["plot_size_actual"].sum()
       st.markdown("**Total Size(SQFT)**")
       st.markdown(f"##### {total_plots:.0f}")
with col6:
    with st.container(border=True,height="stretch"):
       total_sales = df[(df["township_name"] == township) & (df["ownership"].isin(owner))]["plot_price"].agg("sum")
       st.markdown("**Total Sales**")
       st.markdown(f"##### {total_sales:,}")
with col7:
    with st.container(border=True,height="stretch"):
       total_received = df[(df["township_name"] == township) & (df["ownership"].isin(owner))]["amount_received"].sum()
       st.markdown("**Total Received**")
       st.markdown(f"##### {total_received:,}")
with col8:
    with st.container(border=True,height="stretch"):
       total_receivable = df[(df["township_name"] == township) & (df["ownership"].isin(owner))]["receivable"].sum()
       st.markdown("**Total Receivable**")
       st.markdown(f"##### {total_receivable:,}")
st.markdown("---")

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




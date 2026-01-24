import pandas as pd
import numpy as np
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import json
# -------------------------------------------------
# STREAMLIT PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Township Dashboard",
    page_icon="🏘️",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------
st.markdown("""
<style>
header[data-testid="stHeader"] {background-color: #00b3a4;}
section[data-testid="stSidebar"] {background-color: #40E0D0;}
section[data-testid="stSidebar"] label {font-size:18px;font-weight:600;}
section[data-testid="stMain"] {background-color: #01B8AA;}
body {background-color: #01B8AA;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# GOOGLE SHEET CONNECTION (WITH GID)
# -------------------------------------------------
def load_google_sheet():
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds_dict = dict(st.secrets["gcp_service_account"])

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=scope
        )

        client = gspread.authorize(creds)

        SPREADSHEET_ID = "1okER7T-pSffxHfqkm_imKEkJpV7pVx3-wNOjpUuxVr8"
        GID = 0   # <-- change if your sheet tab GID is different

        sheet = client.open_by_key(SPREADSHEET_ID)

        worksheet = None
        for ws in sheet.worksheets():
            if ws.id == GID:
                worksheet = ws
                break

        if worksheet is None:
            st.error(f"❌ Worksheet with GID {GID} not found")
            st.stop()

        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        return df, worksheet

    except Exception as e:
        st.error(f"❌ Google Sheet connection failed: {e}")
        st.stop()


df, worksheet = load_google_sheet()

# -------------------------------------------------
# DATA CLEANING
# -------------------------------------------------
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Rename only if these original names exist
rename_map = {
    "plot_size_(sqft)_actual": "plot_size_actual",
    "plot_size_(sqft)_tncp": "plot_size_tncp",
    "diff_(actual_-_tncp)": "diff_size"
}
df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)

numeric_cols = [
    "rate","amount_received","plot_price",
    "receivable","plot_size_actual","registry_amount"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "registry_date" in df.columns:
    df["registry_date"] = pd.to_datetime(df["registry_date"], errors="coerce")

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.title("Filters")

township = st.sidebar.selectbox(
    "Select Township",
    df["township_name"].unique()
)

owner_filter = st.sidebar.multiselect(
    "Owner",
    options=df[df["township_name"] == township]["ownership"].unique(),
    default=df[df["township_name"] == township]["ownership"].unique()
)

status_filter = st.sidebar.multiselect(
    "Status",
    options=df[df["township_name"] == township]["status"].unique(),
    default=df[df["township_name"] == township]["status"].unique()
)

registry_filter = st.sidebar.multiselect(
    "Registry Status",
    options=df[df["township_name"] == township]["registry_status"].unique(),
    default=df[df["township_name"] == township]["registry_status"].unique()
)

# -------------------------------------------------
# FILTERED DATA
# -------------------------------------------------
df_filtered = df[
    (df["township_name"] == township) &
    (df["ownership"].isin(owner_filter)) &
    (df["status"].isin(status_filter)) &
    (df["registry_status"].isin(registry_filter))
]

st.header(f"🏘️ {township}")

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
c1,c2,c3,c4 = st.columns(4)

if "plot_size_actual" in df_filtered.columns:
    c1.metric("Total Size (SQFT)", f"{df_filtered['plot_size_actual'].sum():,.2f}")
else:
    c1.metric("Total Size (SQFT)", "Column not found")

c2.metric("Total Sales", f"{df_filtered['plot_price'].sum():,.0f}")
c3.metric("Total Received", f"{df_filtered['amount_received'].sum():,.0f}")
c4.metric("Total Receivable", f"{df_filtered['receivable'].sum():,.0f}")

st.divider()

# -------------------------------------------------
# PLOT DETAILS
# -------------------------------------------------
plot_no = st.selectbox(
    "Select Plot No",
    df_filtered["plot_no."].unique()
)

selected_plot = df_filtered[df_filtered["plot_no."] == plot_no]
st.dataframe(selected_plot, use_container_width=True)

# -------------------------------------------------
# UPDATE SECTION
# -------------------------------------------------
with st.expander("✏️ Update Plot Details"):

    editable_fields = [
        'status','plot_size_actual','rate','plot_price',
        'amount_received','registry_status','registry_date',
        'registry_number','buyer_name','contact_number',
        'cheque_number','registry_amount'
    ]

    field_to_update = st.selectbox("Select Field", editable_fields)

    if field_to_update in numeric_cols:
        new_value = st.number_input("Enter New Value", value=0.0)
    elif field_to_update == "registry_date":
        new_value = st.date_input("Select Date", datetime.date.today())
    else:
        new_value = st.text_input("Enter New Value")

    if st.button("Update Plot Info"):

        # Update local dataframe
        df.loc[
            (df["township_name"] == township) &
            (df["plot_no."] == plot_no),
            field_to_update
        ] = new_value

        # ---- Clean dataframe for Google Sheets ----
        df_clean = df.copy()
        df_clean.replace([np.inf, -np.inf], "", inplace=True)
        df_clean = df_clean.fillna("")

        for col in df_clean.columns:
            if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype(str)

        # ---- Push to Google Sheet ----
        try:
            worksheet.update(
                "A1",
                [df_clean.columns.tolist()] + df_clean.values.tolist()
            )
            st.success("✅ Plot updated successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Sheet update failed: {e}")

# -------------------------------------------------
# COLUMN VIEW
# -------------------------------------------------
st.divider()
st.subheader("📊 View Filtered Data")

selected_columns = st.multiselect(
    "Select Columns",
    df_filtered.columns.tolist(),
    default=df_filtered.columns.tolist()
)

st.dataframe(df_filtered[selected_columns], use_container_width=True)

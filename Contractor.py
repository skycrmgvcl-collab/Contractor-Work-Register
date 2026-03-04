import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Contractor Work Monitoring", layout="wide")

st.title("⚡ Contractor Work Monitoring Dashboard")

DATA_FILE = "contractor_work_register.xlsx"

contractor_list = [
    "ABC Contractor",
    "XYZ Infra",
    "Patel Electrical",
    "Om Power Works"
]

# ---------------------------------------------------
# LOAD EXISTING REGISTER
# ---------------------------------------------------

if os.path.exists(DATA_FILE):
    saved_df = pd.read_excel(DATA_FILE)
else:
    saved_df = pd.DataFrame()

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file = st.file_uploader("Upload PPR Report", type=["xls","xlsx","csv"])

if file:

    # READ FILE
    if file.name.endswith(".csv"):
        ppr = pd.read_csv(file)

    elif file.name.endswith(".xlsx"):
        ppr = pd.read_excel(file, engine="openpyxl")

    elif file.name.endswith(".xls"):
        ppr = pd.read_excel(file, engine="xlrd")

    ppr.columns = ppr.columns.str.strip()

    # FILTER B C D
    ppr = ppr[ppr["Survey Category"].isin(["B","C","D"])]

    base_columns = [
        "SR Number",
        "Consumer No",
        "Name Of Applicant",
        "Village Or City",
        "Survey Category",
        "Name Of Scheme",
        "Demand Load",
        "HT Line Lenght",
        "LT Line Lenght",
        "TC Capacity"
    ]

    ppr = ppr[[c for c in base_columns if c in ppr.columns]]

    ppr.insert(0,"Sr No",range(1,len(ppr)+1))

# ---------------------------------------------------
# ADD MANUAL ENTRY COLUMNS
# ---------------------------------------------------

    manual_cols = [
        "Contractor Name",
        "MR Number",
        "MR Date",
        "Work Allotted Date",
        "Work Completion Date",
        "Bill Submitted",
        "Bill Submitted Date",
        "Bill Processed Date",
        "Remarks"
    ]

    for col in manual_cols:
        if col not in ppr.columns:
            ppr[col] = None

# ---------------------------------------------------
# MERGE WITH SAVED DATA
# ---------------------------------------------------

    if not saved_df.empty:

        ppr = ppr.merge(
            saved_df[["SR Number"] + manual_cols],
            on="SR Number",
            how="left",
            suffixes=("","_old")
        )

        for col in manual_cols:
            ppr[col] = ppr[col+"_old"].combine_first(ppr[col])
            ppr.drop(columns=[col+"_old"], inplace=True)

# ---------------------------------------------------
# DASHBOARD METRICS
# ---------------------------------------------------

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Contractor Works", len(ppr))

    col2.metric(
        "Work Not Allotted",
        ppr["Contractor Name"].isna().sum()
    )

    col3.metric(
        "Work Completed",
        ppr["Work Completion Date"].notna().sum()
    )

    col4.metric(
        "Bill Submitted",
        (ppr["Bill Submitted"]=="Yes").sum()
    )

# ---------------------------------------------------
# DATA ENTRY TABLE
# ---------------------------------------------------

    edited_df = st.data_editor(

        ppr,

        use_container_width=True,

        column_config={

            "Contractor Name": st.column_config.SelectboxColumn(
                "Contractor Name",
                options=contractor_list
            ),

            "MR Date": st.column_config.DateColumn("MR Date"),

            "Work Allotted Date": st.column_config.DateColumn("Work Allotted Date"),

            "Work Completion Date": st.column_config.DateColumn("Work Completion Date"),

            "Bill Submitted": st.column_config.SelectboxColumn(
                "Bill Submitted",
                options=["Yes","No"]
            ),

            "Bill Submitted Date": st.column_config.DateColumn("Bill Submitted Date"),

            "Bill Processed Date": st.column_config.DateColumn("Bill Processed Date")

        }

    )

# ---------------------------------------------------
# SAVE DATA
# ---------------------------------------------------

    if st.button("💾 Save Register"):

        edited_df.to_excel(DATA_FILE,index=False)

        st.success("Register Saved Successfully")

# ---------------------------------------------------
# DOWNLOAD REGISTER
# ---------------------------------------------------

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE,"rb") as f:

            st.download_button(
                "⬇ Download Contractor Register",
                f,
                file_name="contractor_work_register.xlsx"
            )

else:

    st.info("Upload PPR Report to Begin")

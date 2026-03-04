import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Contractor Work Monitoring", layout="wide")

st.title("⚡ Contractor Work Monitoring Dashboard")

DATA_FILE = "contractor_work_register.xlsx"

# ---------------------------------------------------
# CONTRACTOR MASTER LIST
# ---------------------------------------------------

contractor_list = [
    "Riken Patel",
    "Ramesh Patel",
    "Auto Forge",
    "Divyesh Patel"
]

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file = st.file_uploader(
    "Upload PPR Report",
    type=["xls", "xlsx", "csv"]
)

if file:

    # ---------------- READ FILE ----------------

    if file.name.endswith(".csv"):
        ppr = pd.read_csv(file)

    elif file.name.endswith(".xlsx"):
        ppr = pd.read_excel(file, engine="openpyxl")

    elif file.name.endswith(".xls"):
        ppr = pd.read_excel(file, engine="xlrd")

    else:
        st.error("Unsupported file format")
        st.stop()

    # ---------------- CLEAN COLUMNS ----------------

    ppr.columns = ppr.columns.str.strip()

    # ---------------- FILTER B/C/D ----------------

    ppr = ppr[ppr["Survey Category"].isin(["B", "C", "D"])]

    # ---------------- REQUIRED COLUMNS ----------------

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

    ppr.insert(0, "Sr No", range(1, len(ppr) + 1))

    # ---------------- ADD MANUAL ENTRY COLUMNS ----------------

    ppr["Contractor Name"] = None
    ppr["MR Number"] = ""
    ppr["MR Date"] = pd.NaT
    ppr["Work Allotted Date"] = pd.NaT
    ppr["Work Completion Date"] = pd.NaT
    ppr["Bill Submitted"] = None
    ppr["Bill Submitted Date"] = pd.NaT
    ppr["Bill Processed Date"] = pd.NaT
    ppr["Remarks"] = ""

    # ---------------------------------------------------
    # DASHBOARD METRICS
    # ---------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

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
        (ppr["Bill Submitted"] == "Yes").sum()
    )

    col5.metric(
        "Bill Processed",
        ppr["Bill Processed Date"].notna().sum()
    )

    # ---------------------------------------------------
    # DATA ENTRY TABLE
    # ---------------------------------------------------

    st.subheader("Contractor Work Register")

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
                options=["Yes", "No"]
            ),

            "Bill Submitted Date": st.column_config.DateColumn("Bill Submitted Date"),

            "Bill Processed Date": st.column_config.DateColumn("Bill Processed Date")

        }

    )

    # ---------------------------------------------------
    # SAVE REGISTER
    # ---------------------------------------------------

    if st.button("💾 Save Register"):

        edited_df.to_excel(DATA_FILE, index=False)

        st.success("Register Saved Successfully")

    # ---------------------------------------------------
    # DOWNLOAD REGISTER
    # ---------------------------------------------------

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "rb") as f:

            st.download_button(
                "⬇ Download Contractor Register",
                f,
                file_name="contractor_work_register.xlsx"
            )

else:

    st.info("Upload PPR Report to Begin")

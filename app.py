import streamlit as st
import pandas as pd
import datetime
import openpyxl
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt

st.set_page_config(page_title="RSU Manager", layout="wide")
st.title("📊 RSU Management Dashboard")

# Sidebar inputs
st.sidebar.header("📝 RSU Input")
company = st.sidebar.text_input("Company Name", "TechCorp")
tax_rate = st.sidebar.slider("Marginal Tax Rate (%)", 0, 50, 45)

# Load sample data
if st.sidebar.button("📂 Load Sample Data"):
    st.session_state["load_sample"] = True
    st.session_state["vesting_data"] = pd.read_excel("sample_rsu_data.xlsx")
    st.session_state["sales_data"] = pd.read_excel("sample_rsu_sales.xlsx")

# Upload data
st.sidebar.markdown("### 📁 Import Data")
vesting_file = st.sidebar.file_uploader("Upload Vesting Schedule (Excel)", type=["xlsx"], key="vesting")
sales_file = st.sidebar.file_uploader("Upload RSU Sales Schedule (Excel)", type=["xlsx"], key="sales")

# Tabs
tab1, tab2, tab3 = st.tabs(["📆 Vesting Schedule", "💸 RSU Sell Tracker", "📊 Summary"])

# -------- TAB 1: VESTING --------
with tab1:
    if "vesting_data" in st.session_state:
        schedule = st.session_state["vesting_data"]
    elif vesting_file:
        schedule = pd.read_excel(vesting_file)
    else:
        grant_date = datetime.date(2023, 1, 1)
        vesting_start_date = datetime.date(2024, 1, 1)
        total_rsus = 1000
        vesting_months = 48
        stock_price = 100.0
        dates = pd.date_range(vesting_start_date, periods=vesting_months, freq='MS')
        vested_per_month = total_rsus / vesting_months
        schedule = pd.DataFrame({
            "Vesting Date": dates,
            "RSUs Vested": vested_per_month,
            "FMV at Vesting": stock_price,
            "Gross Value (AUD)": vested_per_month * stock_price,
        })

    # Ensure datetime format and calculate tax and net
    schedule["Vesting Date"] = pd.to_datetime(schedule["Vesting Date"], errors='coerce')
    schedule["Tax Payable"] = schedule["Gross Value (AUD)"] * (tax_rate / 100)
    schedule["Net Value (AUD)"] = schedule["Gross Value (AUD)"] - schedule["Tax Payable"]
    schedule["Financial Year"] = schedule["Vesting Date"].apply(lambda x: f"{x.year}-{x.year+1}" if x.month >= 7 else f"{x.year-1}-{x.year}")

    st.subheader(f"Vesting Schedule for {company}")
    st.dataframe(schedule.style.format({
        "Gross Value (AUD)": "${:,.2f}",
        "Tax Payable": "${:,.2f}",
        "Net Value (AUD)": "${:,.2f}"
    }))

    vesting_buffer = BytesIO()
    with pd.ExcelWriter(vesting_buffer, engine='openpyxl') as writer:
        schedule.to_excel(writer, index=False, sheet_name="Vesting Schedule")
    vesting_buffer.seek(0)

    st.download_button("📥 Download Vesting Schedule (Excel)",
                       data=vesting_buffer,
                       file_name="vesting_schedule.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------- TAB 2: SALES --------
with tab2:
    st.subheader("💸 RSU Sell Tracker & Capital Gains")

    if "sales_data" in st.session_state:
        sell_data = st.session_state["sales_data"]
    elif sales_file:
        sell_data = pd.read_excel(sales_file)
    else:
        sell_data = pd.DataFrame({
            "Sell Date": [datetime.date.today()],
            "Shares Sold": [100],
            "Sale Price (AUD)": [110.0],
            "FMV at Vesting (AUD)": [100.0],
            "Held > 12 Months": [False]
        })

    sell_data = pd.DataFrame(sell_data)
    sell_data = st.data_editor(sell_data, num_rows="dynamic", use_container_width=True)

    def calculate_cgt(row):
        gain = (row["Sale Price (AUD)"] - row["FMV at Vesting (AUD)"]) * row["Shares Sold"]
        return gain * 0.5 if row["Held > 12 Months"] else gain

    sell_data["Capital Gain (AUD)"] = sell_data.apply(calculate_cgt, axis=1)
    sell_data["Tax on CG"] = sell_data["Capital Gain (AUD)"] * (tax_rate / 100)
    sell_data["Net Proceeds (AUD)"] = (sell_data["Sale Price (AUD)"] * sell_data["Shares Sold"]) - sell_data["Tax on CG"]

    st.dataframe(sell_data.style.format({
        "Capital Gain (AUD)": "${:,.2f}",
        "Tax on CG": "${:,.2f}",
        "Net Proceeds (AUD)": "${:,.2f}"
    }))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(sell_data['Sell Date'], sell_data['Capital Gain (AUD)'], color='skyblue')
    ax.set_xlabel('Sell Date')
    ax.set_ylabel('Capital Gain (AUD)')
    ax.set_title('Capital Gain (AUD) per Sale Date')
    st.pyplot(fig)

    rsu_sales_buffer = BytesIO()
    with pd.ExcelWriter(rsu_sales_buffer, engine='openpyxl') as writer:
        sell_data.to_excel(writer, index=False, sheet_name="RSU Sales")
    rsu_sales_buffer.seek(0)

    st.download_button("📥 Download RSU Sales (Excel)",
                       data=rsu_sales_buffer,
                       file_name="rsu_sales.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------- TAB 3: SUMMARY --------
with tab3:
    st.subheader("📊 Summary")

    total_gross = schedule["Gross Value (AUD)"].sum()
    total_tax = schedule["Tax Payable"].sum()
    total_net = schedule["Net Value (AUD)"].sum()

    st.write(f"**Total Gross Value:** ${total_gross:,.2f}")
    st.write(f"**Total Tax Payable:** ${total_tax:,.2f}")
    st.write(f"**Total Net Value:** ${total_net:,.2f}")

    # ✅ FIX: Ensure "Financial Year" exists
    if "Financial Year" not in schedule.columns:
        schedule["Vesting Date"] = pd.to_datetime(schedule["Vesting Date"], errors="coerce")
        schedule["Financial Year"] = schedule["Vesting Date"].apply(lambda x: f"{x.year}-{x.year+1}" if x.month >= 7 else f"{x.year-1}-{x.year}")

    grouped_fy = schedule.groupby("Financial Year")[["Gross Value (AUD)", "Tax Payable", "Net Value (AUD)"]].sum().reset_index()
    st.markdown("### 📅 Financial Year-wise Tax Summary")
    st.dataframe(grouped_fy.style.format({
        "Gross Value (AUD)": "${:,.2f}",
        "Tax Payable": "${:,.2f}",
        "Net Value (AUD)": "${:,.2f}"
    }))

    if 'sell_data' in locals():
        total_gain = sell_data["Capital Gain (AUD)"].sum()
        total_cgt_tax = sell_data["Tax on CG"].sum()
        total_net_sale = sell_data["Net Proceeds (AUD)"].sum()

        st.markdown("### 💰 Capital Gains Summary")
        st.write(f"**Total Capital Gains:** ${total_gain:,.2f}")
        st.write(f"**Tax on Capital Gains:** ${total_cgt_tax:,.2f}")
        st.write(f"**Net Proceeds from RSU Sales:** ${total_net_sale:,.2f}")

        if st.button("📄 Export Summary to PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="RSU Management Summary", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Company: {company}", ln=True)
            pdf.cell(200, 10, txt=f"Total Gross Value: ${total_gross:,.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Total Tax Payable: ${total_tax:,.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Total Net Value: ${total_net:,.2f}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt="Capital Gains Summary:", ln=True)
            pdf.cell(200, 10, txt=f"Total Capital Gains: ${total_gain:,.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Tax on Capital Gains: ${total_cgt_tax:,.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Net Proceeds: ${total_net_sale:,.2f}", ln=True)

            pdf_output = pdf.output(dest='S').encode('latin1')
            buffer = BytesIO(pdf_output)
            st.download_button("📥 Download PDF Summary", data=buffer, file_name="rsu_summary.pdf", mime="application/pdf")

import streamlit as st
import pandas as pd

etf_reference = {
    "JEPI": {"expense_ratio": 0.0035, "qualified_mix": 0.17, "yield": 0.081, "bear": 0.0279, "bull": 0.1259, "sideways": 0.0382},
    "JEPQ": {"expense_ratio": 0.0035, "qualified_mix": 0.08, "yield": 0.1156, "bear": -0.1289, "bull": 0.2490, "sideways": 0.0359},
    "SPYI": {"expense_ratio": 0.0068, "qualified_mix": 0.06, "yield": 0.125, "bear": -0.0245, "bull": 0.1903, "sideways": 0.0764},
    "VYM": {"expense_ratio": 0.0006, "qualified_mix": 0.95, "yield": 0.028, "bear": -0.0045, "bull": 0.1760, "sideways": 0.0808},
}

def get_tax_rates(income, filing_status):
    if filing_status == "Single":
        if income <= 48350:
            return 0.0, 0.10
        elif income <= 48475:
            return 0.0, 0.12
        elif income <= 103350:
            return 0.15, 0.22
        elif income <= 197300:
            return 0.15, 0.24
        elif income <= 250525:
            return 0.15, 0.32
        elif income <= 533400:
            return 0.15, 0.35
        else:
            return 0.20, 0.37

    elif filing_status == "Married Filing Jointly":
        if income <= 96700:
            return 0.0, 0.10
        elif income <= 96950:
            return 0.0, 0.12
        elif income <= 206700:
            return 0.15, 0.22
        elif income <= 394600:
            return 0.15, 0.24
        elif income <= 501050:
            return 0.15, 0.32
        elif income <= 600000:
            return 0.15, 0.35
        else:
            return 0.20, 0.37

    elif filing_status == "Married Filing Separately":
        if income <= 48350:
            return 0.0, 0.10
        elif income <= 48475:
            return 0.0, 0.12
        elif income <= 103350:
            return 0.15, 0.22
        elif income <= 197300:
            return 0.15, 0.24
        elif income <= 250525:
            return 0.15, 0.32
        elif income <= 300000:
            return 0.15, 0.35
        else:
            return 0.20, 0.37

    elif filing_status == "Head of Household":
        if income <= 64750:
            return 0.0, 0.10
        elif income <= 64850:
            return 0.0, 0.12
        elif income <= 103350:
            return 0.15, 0.22
        elif income <= 197300:
            return 0.15, 0.24
        elif income <= 250500:
            return 0.15, 0.32
        elif income <= 566700:
            return 0.15, 0.35
        else:
            return 0.20, 0.37

    return 0.15, 0.24

st.set_page_config(page_title="ETF Return Analyzer", layout="wide")
st.title("📊 ETF Tax-Adjusted Return Analyzer")

st.sidebar.header("User Inputs")
investment = st.sidebar.number_input("Amount Invested ($)", value=150000)
filing_status = st.sidebar.selectbox("Filing Status", ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"])
income = st.sidebar.number_input("Annual Household Income ($)", value=276000)
tax_q, tax_nq = get_tax_rates(income, filing_status)

st.sidebar.markdown(f"**Qualified Tax Rate:** {tax_q:.0%}")
st.sidebar.markdown(f"**Non-Qualified Tax Rate:** {tax_nq:.0%}")

etf_list = st.sidebar.multiselect("Select ETFs", list(etf_reference.keys()), default=list(etf_reference.keys()))

records = []
for etf in etf_list:
    data = etf_reference[etf]
    income_amt = investment * data["yield"]
    qualified = income_amt * data["qualified_mix"]
    non_qualified = income_amt * (1 - data["qualified_mix"])
    tax = qualified * tax_q + non_qualified * tax_nq
    after_tax_income = income_amt - tax
    after_tax_return = after_tax_income / investment

    net_bear = data["bear"] + after_tax_return - data["expense_ratio"]
    net_bull = data["bull"] + after_tax_return - data["expense_ratio"]
    net_sideways = data["sideways"] + after_tax_return - data["expense_ratio"]

    records.append({
        "ETF": etf,
        "Expense Ratio": data["expense_ratio"],
        "Qualified Mix": data["qualified_mix"],
        "12M Yield": data["yield"],
        "After-Tax Yield": round(after_tax_return, 4),
        "Total Return (Bear)": round(net_bear, 4),
        "Total Return (Bull)": round(net_bull, 4),
        "Total Return (Sideways)": round(net_sideways, 4),
    })

df = pd.DataFrame(records)
st.dataframe(df.style.format({
    "Expense Ratio": "{:.2%}",
    "Qualified Mix": "{:.0%}",
    "12M Yield": "{:.2%}",
    "After-Tax Yield": "{:.2%}",
    "Total Return (Bear)": "{:.2%}",
    "Total Return (Bull)": "{:.2%}",
    "Total Return (Sideways)": "{:.2%}"
}))

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", csv, "etf_returns.csv", "text/csv")

st.subheader("📈 Return Comparison")
chart_df = df.set_index("ETF")[["Total Return (Bear)", "Total Return (Bull)", "Total Return (Sideways)"]]
st.bar_chart(chart_df)

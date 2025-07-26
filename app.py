import streamlit as st
import pandas as pd
import yfinance as yf

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

# Inputs
st.sidebar.header("User Inputs")
investment = st.sidebar.number_input("Amount Invested ($)", value=150000)
filing_status = st.sidebar.selectbox("Filing Status", ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"])
income = st.sidebar.number_input("Annual Household Income ($)", value=276000)
tax_q, tax_nq = get_tax_rates(income, filing_status)

st.sidebar.markdown(f"**Qualified Tax Rate:** {tax_q:.0%}")
st.sidebar.markdown(f"**Non-Qualified Tax Rate:** {tax_nq:.0%}")

etf_input = st.sidebar.text_input("Enter ETF Tickers (comma-separated)", "JEPI,JEPQ,SPYI,VYM")
etf_list = [etf.strip().upper() for etf in etf_input.split(",") if etf.strip()]

# Data processing
records = []
for etf in etf_list:
    try:
        ticker_data = yf.Ticker(etf)
        info = ticker_data.info

        dividend_yield = info.get("yield", 0.02)
        expense_ratio = info.get("fundExpenseRatio", 0.01)
        qualified_mix = 0.95 if "dividend" in info.get("longName", "").lower() else 0.5
        bear, bull, sideways = 0.0, 0.0, 0.0

        income_amt = investment * dividend_yield
        qualified = income_amt * qualified_mix
        non_qualified = income_amt * (1 - qualified_mix)
        tax = qualified * tax_q + non_qualified * tax_nq
        after_tax_income = income_amt - tax
        after_tax_return = after_tax_income / investment

        net_bear = bear + after_tax_return - expense_ratio
        net_bull = bull + after_tax_return - expense_ratio
        net_sideways = sideways + after_tax_return - expense_ratio

        records.append({
            "ETF": etf,
            "Expense Ratio": expense_ratio,
            "Qualified Mix": qualified_mix,
            "12M Yield": dividend_yield,
            "After-Tax Yield": round(after_tax_return, 4),
            "Total Return (Bear)": round(net_bear, 4),
            "Total Return (Bull)": round(net_bull, 4),
            "Total Return (Sideways)": round(net_sideways, 4),
        })
    except Exception as e:
        st.warning(f"Could not fetch data for {etf}: {e}")

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

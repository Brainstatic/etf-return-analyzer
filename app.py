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


import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ETF Return Analyzer", layout="wide")
st.title("📊 ETF Tax-Adjusted Return Analyzer")

# Inputs
st.sidebar.header("User Inputs")
investment = st.sidebar.number_input("Amount Invested ($)", value=150000)
filing_status = st.sidebar.selectbox("Filing Status", ["Single", "Married Filing Jointly", "Head of Household"])
income = st.sidebar.number_input("Annual Household Income ($)", value=276000)
tax_q, tax_nq = get_tax_rates(income, filing_status)

st.sidebar.markdown(f"**Qualified Tax Rate:** {tax_q:.0%}")
st.sidebar.markdown(f"**Non-Qualified Tax Rate:** {tax_nq:.0%}")

etf_input = st.sidebar.text_input("Enter ETF Tickers (comma-separated)", "JEPI,JEPQ,SPYI,VYM")
etf_list = [etf.strip().upper() for etf in etf_input.split(",") if etf.strip()]

# Allow user to input expense ratios and qualified dividend mix manually
st.sidebar.markdown("---")
st.sidebar.markdown("### ETF Details")
st.sidebar.markdown("If unsure, you can ask ChatGPT:")
st.sidebar.code("What are the current expense ratio and qualified dividend mix for the ETF SCHD?")

# User-defined ETF values
st.sidebar.markdown("### Market Assumptions")
bear_market_return = st.sidebar.number_input("Bear Market Capital Loss (%)", value=-10.0, format="%.2f") / 100
bull_market_return = st.sidebar.number_input("Bull Market Capital Gain (%)", value=15.0, format="%.2f") / 100
sideways_market_return = st.sidebar.number_input("Sideways Market Gain/Loss (%)", value=0.0, format="%.2f") / 100

# Detect market state
if bull_market_return > 0.05 and bear_market_return > -0.05:
    market_state = "🚀 Bull Market"
elif bear_market_return < -0.10:
    market_state = "🐻 Bear Market"
else:
    market_state = "⏸️ Sideways Market"
st.sidebar.markdown(f"**Current Market State (Assumed):** {market_state}")

records = []
user_expense_ratios = {}
user_qualified_mixes = {}
for etf in etf_list:
    user_expense_ratios[etf] = st.sidebar.number_input(f"Expense Ratio for {etf}", min_value=0.0, max_value=1.0, value=0.01, format="%.4f")
    user_qualified_mixes[etf] = st.sidebar.number_input(f"Qualified Dividend Mix for {etf}", min_value=0.0, max_value=1.0, value=0.5, format="%.2f")

    try:
        ticker_data = yf.Ticker(etf)
        info = ticker_data.info
        dividend_yield = info.get("yield", 0.02)
        expense_ratio = user_expense_ratios[etf]
        qualified_mix = user_qualified_mixes[etf]

        income_amt = investment * dividend_yield
        qualified = income_amt * qualified_mix
        non_qualified = income_amt * (1 - qualified_mix)
        tax = qualified * tax_q + non_qualified * tax_nq
        after_tax_income = income_amt - tax
        after_tax_return = after_tax_income / investment

        bear, bull, sideways = bear_market_return, bull_market_return, sideways_market_return
        net_bear = bear + after_tax_return - expense_ratio
        net_bull = bull + after_tax_return - expense_ratio
        net_sideways = sideways + after_tax_return - expense_ratio

        records.append({
            "ETF": etf,
            "Expense Ratio": expense_ratio,
            "Qualified Mix": qualified_mix,
            "12M Yield": dividend_yield,
            "Qualified Income": round(qualified, 2),
            "Non-Qualified Income": round(non_qualified, 2),
            "Tax on Qualified": round(qualified * tax_q, 2),
            "Tax on Non-Qualified": round(non_qualified * tax_nq, 2),
            "Total Tax": round(tax, 2),
            "After-Tax Income": round(after_tax_income, 2),
            "After-Tax Yield": round(after_tax_return, 4),
            "Bear Market Gain/Loss ($)": round(investment * bear, 2),
            "Total Return (Bear) $": round(investment * net_bear, 2),
            "Total Return (Bear) %": round(net_bear, 4),
            "Total Return (Bull) $": round(investment * net_bull, 2),
            "Total Return (Bull) %": round(net_bull, 4),
            "Total Return (Sideways) $": round(investment * net_sideways, 2),
            "Total Return (Sideways) %": round(net_sideways, 4)
        })
    except Exception as e:
        st.warning(f"Could not fetch data for {etf}: {e}")

if records:
    df = pd.DataFrame(records)
    st.markdown("### 📋 ETF Return Table")
    st.dataframe(df.style.background_gradient(cmap="RdYlGn", subset=["Total Return (Bull) %", "Total Return (Bear) %", "Total Return (Sideways) %"]))

    st.markdown("### 🧮 Summary")
    best_bull = df.loc[df["Total Return (Bull) %"].idxmax()]
    worst_bear = df.loc[df["Total Return (Bear) %"].idxmin()]
    st.markdown(f"**🏆 Best Bull Market Performer:** {best_bull['ETF']} ({best_bull['Total Return (Bull) %']*100:.2f}%)")
    st.markdown(f"**📉 Worst Bear Market Performer:** {worst_bear['ETF']} ({worst_bear['Total Return (Bear) %']*100:.2f}%)")

    view_mode = st.radio("Chart View", ["% Return", "$ Return"], horizontal=True)
    st.markdown("### 📈 Return Comparison Chart")
    if view_mode == "% Return":
        st.bar_chart(df.set_index("ETF")[["Total Return (Bear) %", "Total Return (Bull) %", "Total Return (Sideways) %"]])
    else:
        st.bar_chart(df.set_index("ETF")[["Total Return (Bear) $", "Total Return (Bull) $", "Total Return (Sideways) $"]])

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Results as CSV", data=csv, file_name="etf_returns.csv", mime="text/csv")

    import tempfile
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="ETF Tax-Adjusted Return Report", ln=True, align='C')
    pdf.ln(10)
    for index, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['ETF']}: Bull={row['Total Return (Bull) %']*100:.2f}%, Bear={row['Total Return (Bear) %']*100:.2f}%, Sideways={row['Total Return (Sideways) %']*100:.2f}%", ln=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        with open(tmp_file.name, "rb") as f:
            st.download_button("📄 Download PDF Report", data=f.read(), file_name="etf_report.pdf", mime="application/pdf")

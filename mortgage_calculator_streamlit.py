import pandas as pd
import streamlit as st

def calculate_amortization_schedule(apr, monthly_repayment, deposit, total_asset_value):
    apr_decimal = apr / 100  # Convert APR to decimal
    monthly_rate = apr_decimal / 12  # Monthly interest rate
    total_debt = total_asset_value - deposit  # Initial loan amount
    
    balance = total_debt
    month = 0
    cumulative_interest = 0  # Initialize cumulative interest
    data = []
    
    while balance > 0:
        interest_payment = balance * monthly_rate
        principal_payment = monthly_repayment - interest_payment
        balance -= principal_payment

        if balance < 0:
            principal_payment += balance  # Adjust last principal payment
            balance = 0
        
        equity = total_asset_value - balance
        cumulative_interest += interest_payment  # Update cumulative interest
        data.append([month // 12, month % 12 + 1, balance, equity, interest_payment, principal_payment, cumulative_interest])
        month += 1
    
    df = pd.DataFrame(data, columns=['Year', 'Month', 'Total Debt', 'Total Equity', 'Interest Paid', 'Principal Paid', 'Total Interest Paid'])
    return df

def mortgage_summary(df, total_debt):
    total_interest_paid = df["Interest Paid"].sum()
    total_payments = total_interest_paid + total_debt
    final_year = df.iloc[-1]["Year"]
    final_month = df.iloc[-1]["Month"]
    
    summary = pd.DataFrame({
        "Years of Repayment": [f"Year {int(final_year)} Month {int(final_month)}"],
        "Total Interest Paid": [round(total_interest_paid, 2)],
        "Total Payments": [round(total_payments, 2)]
    })
    return summary

def get_equity_at_year_month(df, year, month):
    result = df[(df['Year'] == year) & (df['Month'] == month)]
    if result.empty:
        return "Invalid year or month provided."
    return result[['Total Equity', 'Total Debt', 'Total Interest Paid']]


# Streamlit UI
def main():
    st.title("Mortgage Calculator")
    
    # User inputs
    apr = st.number_input("Annual Percentage Rate (APR) %", min_value=0.1, value=4.35)
    monthly_repayment = st.number_input("Monthly Repayment", min_value=1, value=4400)
    deposit = st.number_input("Deposit", min_value=0, value=100000)
    total_asset_value = st.number_input("Total Asset Value", min_value=1, value=520000)
    
    # Check if session state already contains df
    if "df" not in st.session_state:
        st.session_state.df = None
    
    if st.button("Calculate Mortgage"):
        st.session_state.df = calculate_amortization_schedule(apr, monthly_repayment, deposit, total_asset_value)
        summary = mortgage_summary(st.session_state.df, total_asset_value - deposit)
        
        st.subheader("Mortgage Summary")
        st.dataframe(summary)
        
        st.subheader("Amortization Schedule")
        st.dataframe(st.session_state.df)
    
    # Equity lookup (Only run if df exists)
    if st.session_state.df is not None:
        st.subheader("Retrieve Equity at Specific Time")
        year_equity = st.number_input("Year", min_value=0, value=5)
        month_equity = st.number_input("Month", min_value=1, max_value=12, value=1)
        
        if st.button("Get Equity"):
            equity = get_equity_at_year_month(st.session_state.df, year_equity, month_equity)
            st.write(equity)
    else:
        st.warning("Please calculate the mortgage first before checking equity.")

if __name__ == "__main__":
    main()

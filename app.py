import streamlit as st
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Society Maintenance Dashboard", layout="wide")

# Custom CSS for animations and styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

body {
    font-family: 'Roboto', sans-serif;
}

/* Society Name Styling */
.society-name {
    text-align: center;
    font-size: 2.5em;
    color: #4CAF50;
    animation: fadeIn 2s;
    font-weight: bold;
}

/* Chairman Line Styling */
.chairman-line {
    text-align: center;
    font-size: 1.8em;
    color: #FFFFFF;
    background-color: #FF5733; /* Highlight color */
    padding: 10px;
    border-radius: 10px;
    animation: slideIn 1.5s;
    font-weight: bold;
    margin-top: 10px;
}

/* Financial Metrics Styling */
.metrics-container {
    display: flex;
    justify-content: space-between;
    animation: fadeIn 2s;
    margin-top: 20px;
}

.metric-item {
    background-color: #4CAF50;
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 1.2em;
    font-weight: bold;
    flex: 1;
    margin: 0 5px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    transition: 0.3s;
}

.metric-item:hover {
    background-color: #45a049;
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Function to load data
@st.cache_data
def load_data(uploaded_file):
    march_25_df = pd.read_excel(uploaded_file, sheet_name='March 25')
    other_revenue_df = pd.read_excel(uploaded_file, sheet_name='OTHER REVENUE')
    expenses_df = pd.read_excel(uploaded_file, sheet_name='Expenses')
    missing_df = pd.read_excel(uploaded_file, sheet_name='Missing')
    return march_25_df, other_revenue_df, expenses_df, missing_df

# Function to calculate metrics
def calculate_metrics(march_25_df, other_revenue_df, expenses_df):
    total_expected_maintenance = march_25_df['AMOUNT'].sum()
    total_collected_maintenance = march_25_df[march_25_df['Status'] == 'Paid']['AMOUNT'].sum()
    remaining_maintenance = total_expected_maintenance - total_collected_maintenance
    other_revenue = other_revenue_df['AMOUNT'].sum()
    expenses = expenses_df['Amount'].sum()
    balance_in_society_fund = (total_collected_maintenance + other_revenue) - expenses

    return {
        "Total Expected Maintenance": total_expected_maintenance,
        "Total Collected Maintenance": total_collected_maintenance,
        "Remaining Maintenance": remaining_maintenance,
        "OTHER REVENUE": other_revenue,
        "Expenses": expenses,
        "Balance In Society fund": balance_in_society_fund
    }

# Main function
def main():
    # Header with society name and chairman's name
    st.markdown("<div class='society-name'>Sanskruti Meander A wing</div>", unsafe_allow_html=True)
    st.markdown("<div class='chairman-line'>Chairman - Shri. Deepak Kale</div>", unsafe_allow_html=True)

    # Initialize session state for file upload
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False

    # Admin upload section
    if not st.session_state.file_uploaded:
        st.markdown("Welcome to the Society Maintenance Dashboard. Please upload the Excel file to proceed.", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"], key="file_uploader")

        if uploaded_file is not None:
            st.session_state.file_uploaded = True
            st.session_state.march_25_df, st.session_state.other_revenue_df, st.session_state.expenses_df, st.session_state.missing_df = load_data(uploaded_file)
            st.success("File uploaded successfully!")

    # Display data if file is uploaded
    if st.session_state.file_uploaded:
        # Calculate metrics
        metrics = calculate_metrics(st.session_state.march_25_df, st.session_state.other_revenue_df, st.session_state.expenses_df)

        # Display Financial Metrics in one line
        st.markdown("""
        <div class='metrics-container'>
            <div class='metric-item'>Total Expected Maintenance: ₹{0:,.2f}</div>
            <div class='metric-item'>Total Collected Maintenance: ₹{1:,.2f}</div>
            <div class='metric-item'>Remaining Maintenance: ₹{2:,.2f}</div>
            <div class='metric-item'>OTHER REVENUE: ₹{3:,.2f}</div>
            <div class='metric-item'>Expenses: ₹{4:,.2f}</div>
            <div class='metric-item'>Balance In Society Fund: ₹{5:,.2f}</div>
        </div>
        """.format(
            metrics['Total Expected Maintenance'],
            metrics['Total Collected Maintenance'],
            metrics['Remaining Maintenance'],
            metrics['OTHER REVENUE'],
            metrics['Expenses'],
            metrics['Balance In Society fund']
        ), unsafe_allow_html=True)

        # Display OTHER REVENUE sheet with month filter
        st.subheader("OTHER REVENUE")
        st.session_state.other_revenue_df['DATE'] = pd.to_datetime(st.session_state.other_revenue_df['DATE'])
        st.session_state.other_revenue_df['DATE'] = st.session_state.other_revenue_df['DATE'].dt.strftime('%d-%b-%y')  # Format date as 1-Mar-25
        month_filter = st.selectbox("Select Month", pd.to_datetime(st.session_state.other_revenue_df['DATE']).dt.strftime('%B %Y').unique())
        filtered_other_revenue = st.session_state.other_revenue_df[pd.to_datetime(st.session_state.other_revenue_df['DATE']).dt.strftime('%B %Y') == month_filter]
        st.dataframe(filtered_other_revenue)

        # Display Expenses sheet with month filter and bill download links
        st.subheader("Expenses")
        st.session_state.expenses_df['Date'] = pd.to_datetime(st.session_state.expenses_df['Date'])
        st.session_state.expenses_df['Date'] = st.session_state.expenses_df['Date'].dt.strftime('%d-%b-%y')  # Format date as 1-Mar-25
        month_filter_expenses = st.selectbox("Select Month", pd.to_datetime(st.session_state.expenses_df['Date']).dt.strftime('%B %Y').unique())
        filtered_expenses = st.session_state.expenses_df[pd.to_datetime(st.session_state.expenses_df['Date']).dt.strftime('%B %Y') == month_filter_expenses]

        # Make "Link for Bill" clickable
        filtered_expenses['Link for Bill'] = filtered_expenses['Link for Bill'].apply(lambda x: f'<a href="{x}" target="_blank">Download Bill</a>' if pd.notna(x) else '')
        st.write(filtered_expenses.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Display Missing sheet
        st.subheader("Missing Maintenance")
        st.dataframe(st.session_state.missing_df)

if __name__ == "__main__":
    main()
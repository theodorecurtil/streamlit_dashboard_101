import streamlit as st
import pandas as pd
from helper import *

with st.sidebar:
    include_security_buffer = st.checkbox("Include the security deposit", False)

st.title('Credit Loan Risk')

@st.cache
def load_dataset():
    df = pd.read_csv("CaseStudy_Data.csv", usecols=["ProjektNumber", "LTV", "MarketValue", "LoanNominal", "SeniorLoan", "SecurityAmount"])
    return df


def filter_dataset(LTV_min, LTV_max, df):
    return df.query("LTV >= @LTV_min and LTV <= @LTV_max")

def get_LTV_range(df):
    return np.min(df["LTV"]).item(), np.max(df["LTV"]).item()

myDataAll = load_dataset()

## Filter by LTV
st.subheader("Filter data by LTV range")
min_LTV, max_LTV = get_LTV_range(myDataAll)
LTV_range = st.slider("LTV range", min_LTV, max_LTV, (min_LTV, max_LTV))
filtered_data = filter_dataset(LTV_range[0], LTV_range[1], myDataAll)

## Display sample of data
st.write(f"A sample of data with LTV in range {LTV_range} is shown below")
st.dataframe(filtered_data.head(), use_container_width=True)
cvs_data = convert_data_to_csv(filtered_data)
st.download_button(
   "Press to Download",
   cvs_data,
   f"my_loans_data.csv",
   "text/csv",
   key='download-csv'
)

## Plot portfolio exposure
st.subheader("Portfolio Exposure to Market Value Declines")
## Make comparison portfolio
col1, col2 = st.columns(2)

with col1:
    show_comparison = st.checkbox('Show comparison portfolio')
with col2:
   LTV_cap = st.slider("Select LTV cap", 0, 100, 80, disabled=not show_comparison)/100

with st.expander("See comparison portfolio"):
    comparison_portfolio = make_comparison_portfolio(filtered_data, LTV_cap)
    st.dataframe(comparison_portfolio.head(), use_container_width=True)

st.markdown(
    """
    We are making the following assumptions:
    1. SeniorLoan is fixed value -> only LoanNominal can be decreased.
    2. SecurityAmount is decreased to maintain the ratio SecurityAmount/LoanNominal"
    """
    )

my_figure = make_exposure_plot(filtered_data, show_comparison, LTV_cap, include_security_buffer)
st.plotly_chart(my_figure, theme=None, use_container_width=True)
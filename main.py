import streamlit as st
import pandas as pd
from helper import *

with st.sidebar:
    st.subheader("Welcome")
    st.write("The codebase underlying this Streamlit application is available on [github.com/theodorecurtil/streamlit_dashboard_101](https://github.com/theodorecurtil/streamlit_dashboard_101)")
    st.subheader("Application Parameters")
    include_security_buffer = st.checkbox("Include the security deposit", False)

## We make two tabs. One tab with the app, one tab with the method used
tab1, tab2 = st.tabs(["Application", "Details"])

with tab1:
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

    my_figure = make_exposure_plot(filtered_data, show_comparison, LTV_cap, include_security_buffer)
    st.plotly_chart(my_figure, theme=None, use_container_width=True)

with tab2:
   st.markdown(
        """
        ## Method and Assumptions

        ### Assumptions
        Throughout the case, we are making the following assumptions:
        - Company XY is the sole investor in the subordinated tranch. As such, $\\Sigma_i LN_i$ is the total exposed capital of the investment company.
        - The security amount in the dataset was deposited to the subordinated tranch. This means that it can be used in full to further absorb the losses of the subordinated tranch.
        - The security amount for one financing project is a fixed ratio of $LN$ the subordinated loan value. As such, when we cap $LTV$ by decreasing the value of the subordinated loan, we decrease the security amount to maintain the ratio.
        - The capped $LTV$ is attained by reducing the value of $LN$ the subordinated loan value only. The senior tranch is left untouched.

        ### Method

        The losses are absorbed by the different tranches as follows:
        1. Equity component
        2. Subordinated loans
        3. Senior loans

        The equity of the borrower is defined by

        $$
        E = MV - LN - SL
        $$
        where $E$ is the borrower's equity, $LN$ is the loan notional, or the subordinated debt (the investment of company XY) and $SL$ is the senior loan value, coming from banks or other lower-yield debt provider.

        In the event of a loss in market value $MV$ of $x\\%$, the loss $L_{MV} = x \\times MV / 100$ is first absorbed by the equity tranche, and then the investment of company XY gets impacted until the loan is written down to zero; and then the senior tranche gets impacted. As such, the tranche structure provides downside protection to senior lenders against a lower yield on the debt product. On the other hand, investors in the equity component or the subordinated debt get compensated with a higher yield.

        More formally, the loss on the subordinated loan is:

        $$
        L_{LN} = \\min(\\max(L_{MV} - E, 0), LN)
        $$
        which means that the loss taken by the subordinated tranche is in the interval $[0, LN]$. Indeed, if the market value loss can be fully absorbed by the equity component, the loss to the subordinated investors is 0. On the other hand, in case the market value loss is greater than $E + LN$, then both the equity and subordinated components are written down to 0, and the senior tranche starts eroding. This means the loss to subordinated investors is capped to $LN$.

        In case the security deposit is included in computations, it provides a buffer that protects both the subordinated and senior tranches. This effectively corresponds to increasing the equity of the borrower by the amount of the security deposit. Hence, the equation for the loss to the subordinated tranch becomes:

        $$
        L_{LN} = \\min(\\max(L_{MV} - E - \\mathbf{SD}, 0), LN)
        $$
        where $SD$ is the amount of the security deposit.

        Finally, the loss $L_{LN}^i(x)$ to the company XY on financing project $i$ for a market value loss of $x\\%$ is given by:

        $$
        L_{LN}^i(x) = \\min(\\max(\\frac{x \\times MV^i}{100} - E^i - SD^i, 0), LN^i)
        $$

        And the loss as a percentage of the principal value is $\\frac{L_{LN}^i(x)}{LN^i}$.

        At the portfolio level, we report two metrics:
        1. The arithmetic average of $\\frac{L_{LN}^i(x)}{LN^i}$, $\\frac 1 n \\Sigma_i \\frac{L_{LN}^i(x)}{LN^i}$
        2. The weighted average of $\\frac{L_{LN}^i(x)}{LN^i}$, which is simply the ratio of the total losses and the total invested capital: $\\frac{\\Sigma_i L_{LN}^i}{\\Sigma_i LN^i}$

        As a sanity check one can check that when a single loan is considered in the portfolio, the loss function is piecewise-linear, and the weighted and unweighted mean losses are equal.

        ### Comparison Portfolio

        To create the comparison portfolio where $LTV$ values of financing projects are capped; we create a synthetic copy of each financing project where the value $LN$ is decreased until the $LTV$ of the project is equal to $LTV^*$, the $LTV$ cap.

        The updated $LN$ value for projects where $LTV$ is greater than the $LTV$ cap is given by:

        $$
        LN^* = LTV^* \\times MV - SL
        $$

        In case $LN^*$ is negative, the synthetic project is removed from the comparison portfolio; as it means that the company XY cannot provide any debt capital to the project without the LTV being greater than the LTV cap.

        As a sanity check, one can check that the lower the LTV cap, the less risky the comparison portfolio becomes. This is because the equity tranche is inflated as the $LN$ values are decreased. Note the following:
        
        In this case, risk reduction is achieved by lowering the lended capital $LN$, meaning:
        - As the equity tranche increases in size, subordinated and senior lenders would be compensated with lower yield
        - Invested capital in some projects becomes lower, meaning that the same initial capital would have to be distributed over more projects. But the space of investable projects is limited...

        """
        )




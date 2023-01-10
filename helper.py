import pandas as pd
import numpy as np
import plotly.express as px

def convert_data_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

def compute_inv_principal_loss(loan, MV_decline, include_security_deposit = False):
    ## ["ProjektNumber", "LTV", "MarketValue", "LoanNominal", "SeniorLoan", "SecurityAmount", "EquityAmount"]
    MV_loss = MV_decline * loan[2]
    principal_loss = min(max(MV_loss - loan[-1] - loan[-2]*include_security_deposit, 0), loan[3])
    return principal_loss/loan[3]

def compute_inv_principal_loss_dollar(loan, MV_decline, include_security_deposit = False):
    ## ["ProjektNumber", "LTV", "MarketValue", "LoanNominal", "SeniorLoan", "SecurityAmount", "EquityAmount"]
    MV_loss = MV_decline * loan[2]
    principal_loss = min(max(MV_loss - loan[-1] - loan[-2]*include_security_deposit, 0), loan[3])
    return principal_loss

def aggregate_inv_princial_loss(MV_decline, df, include_security_deposit = False):
    rincipal_loss = df.apply(compute_inv_principal_loss, axis=1, args=(MV_decline[0], include_security_deposit))
    return np.mean(rincipal_loss)

def aggregate_inv_princial_loss_weighted(MV_decline, df, include_security_deposit = False):
    rincipal_loss = df.apply(compute_inv_principal_loss_dollar, axis=1, args=(MV_decline[0], include_security_deposit))
    commited_principal = df["LoanNominal"]
    return np.sum(rincipal_loss)/np.sum(commited_principal)

def make_data_to_plot(df, comparison_portfolio=False, include_security_deposit=False):
    to_plot = pd.DataFrame(np.linspace(0, 1, 200), columns=["Market Value Decline"])
    df["EquityAmount"] = df["MarketValue"] - df["LoanNominal"] - df["SeniorLoan"]
    to_plot["Investment Principal Loss" + " - comparison"*comparison_portfolio] = to_plot.apply(aggregate_inv_princial_loss, axis=1, args=(df, include_security_deposit))
    to_plot["Investment Principal Loss (weighted)" + " - comparison"*comparison_portfolio] = to_plot.apply(aggregate_inv_princial_loss_weighted, axis=1, args=(df, include_security_deposit))
    to_plot = to_plot.melt(
        id_vars=["Market Value Decline"],
        value_name="Investment Loss"
        )
    return to_plot

def make_comparison_portfolio(df, LTV_cap=0.2):
    new_df = df.copy()
    new_df["SecurityRatio"] = new_df["SecurityAmount"]/new_df["LoanNominal"]
    new_df["LoanNominal"] = df.apply(lambda x: LTV_cap*x["MarketValue"] - x["SeniorLoan"] if x["LTV"]>100*LTV_cap else x["LoanNominal"], axis=1)
    new_df["SecurityAmount"] = (new_df["LoanNominal"]*new_df["SecurityRatio"]).astype(int)
    new_df.drop("SecurityRatio", axis=1, inplace=True)
    new_df["LTV"] = (100*(new_df["SeniorLoan"] + new_df["LoanNominal"])/new_df["MarketValue"]).astype(int)
    return new_df[new_df["LoanNominal"]>0]


def make_exposure_plot(df, comparison_portfolio_flag = False, LTV_cap=0.8, include_security_deposit=False):
    exposure_data = make_data_to_plot(df, False, include_security_deposit)
    if comparison_portfolio_flag:
        comparison_portfolio = make_comparison_portfolio(df, LTV_cap)
        exposure_data_comparison = make_data_to_plot(comparison_portfolio, comparison_portfolio_flag, include_security_deposit)
        exposure_data = pd.concat([exposure_data, exposure_data_comparison])
    
    fig = px.line(exposure_data, x="Market Value Decline", y="Investment Loss", color="variable")
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1,
    xanchor="right",
    x=0.9
    ))
    fig.update_yaxes(range=[0, 1.02])
    return fig
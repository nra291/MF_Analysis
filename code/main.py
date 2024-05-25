

import helper_functions as h
import config as c
import time
import os
import streamlit as st



h.set_config() # Should be the first StrealLit Command in the app

with h.l.st.sidebar:
    label = "Select Person"
    options = ["S", "B", "N"]
    selected_fruit = st.selectbox(label, options)

match selected_fruit:
    case 'S':
        folder = c.rel_data_folder_s
    case 'B':
        folder = c.rel_data_folder_b
    case 'N':
        folder = c.rel_data_folder_n

d1, d2 = h.prepare_data(folder)

row1_col_1, row1_col_2= h.l.st.columns(2)
row2_col_1, row2_col_2= h.l.st.columns(2)
row3_col_1, row3_col_2= h.l.st.columns(2)

with row1_col_1:
    h.st_plot_overall(d2)
with row1_col_2:
    h.plot_pnl(d2)

data_by_key = d1[d1[c.as_of_date] == d1.groupby(c.mf_key)[c.as_of_date].transform(max)][(d1['Category']=='Equity')].sort_values(by=c.amc)
data_by_amc = d1[d1[c.as_of_date] == d1.groupby(c.amc)[c.as_of_date].transform(max)]
data_by_amc = data_by_amc.groupby(c.amc)
# data_by_amc = data_by_amc[(data_by_amc['Category']=='Equity')]

h.plot_invested_share(data_by_amc, c.amc, row2_col_1)
h.plot_invested_share(data_by_key, c.mf_key, row2_col_2)
h.plot_profit_share(data_by_amc, c.amc, row3_col_1)
h.plot_profit_share(data_by_key, c.mf_key, row3_col_2)

with h.l.st.expander("Funds Comparison"):
    h.st_comparison(d1)

h.plot_bar(data_by_amc)

# h.make_heatmap(d1, c.as_of_date, c.percent_return,c.mf_key, 'blues') #
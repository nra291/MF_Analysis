

import helper_functions as h
import config as c
import time
import os
import streamlit as st



h.set_config() # Should be the first StrealLit Command in the app

with h.l.st.sidebar:
    label = "Select Person"
    options = ["B", "S", "N"]
    selected_person = st.selectbox(label, options)

match selected_person:
    case 'S':
        folder = c.rel_data_folder_s
        name = c.silky
    case 'B':
        folder = c.rel_data_folder_b
        name = c.bablu
    case 'N':
        folder = c.rel_data_folder_n
        name = c.nitin

d1, d2 = h.prepare_data(folder, name)

row1_col_1, row1_col_2= h.l.st.columns(2)
row2_col_1, row2_col_2= h.l.st.columns(2)
row3_col_1, row3_col_2= h.l.st.columns(2)

with row1_col_1:
    h.st_plot_overall(d2)
with row1_col_2:
    h.plot_pnl(d2)

data_by_key, data_by_amc = h.summarize_key_amc(d1)

h.plot_invested_share(data_by_amc, c.amc, row2_col_1)
h.plot_invested_share(data_by_key, c.mf_key, row2_col_2)
# h.plot_profit_share(data_by_amc, c.amc, row3_col_1)
# h.plot_profit_share(data_by_key, c.mf_key, row3_col_2)


h.plot_stacked_bar(data_by_amc, c.amc)
h.plot_stacked_bar(data_by_key, c.mf_key)


with h.l.st.expander("Funds Comparison"):
    h.st_comparison(d1)


# h.make_heatmap(d1, c.as_of_date, c.percent_return,c.mf_key, 'blues') #
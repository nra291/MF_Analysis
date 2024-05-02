
import helper_functions as h
import config as c



# streamlit run "/Users/nra29/GDrive - DL02/MF_Analysis/code/main.py"
# ----------------------------------------------------------------------

# h.sl_tabs()
# 


d1, d2 = h.prepare_data(c.rel_data_folder)
h.set_config() # Should be the first StrealLit Command in the app

# top_row_col_1, top_row_col_2 = h.l.st.columns(1)
# top_row_col_1 = h.l.st.columns()


bottom_col_1, bottom_col_2= h.l.st.columns(2)

with bottom_col_1:
    h.st_plot_overall(d2)
with bottom_col_2:
    h.plot_pnl(d2)

h.st_sidebar(d1)

#
    
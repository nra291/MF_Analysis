
import helper_functions as h
import config as c



# streamlit run "/Users/nra29/GDrive - DL02/MF_Analysis/code/main.py"
# ----------------------------------------------------------------------

# h.sl_tabs()
# 


d1, d2 = h.prepare_data(c.rel_data_folder)

h.st_sidebar(d1)
h.st_total_investment(d2)


import helper_functions as h
import config as c
import time
import os
import streamlit as st


d1, d2 = h.prepare_data(c.rel_data_folder)
h.set_config() # Should be the first StrealLit Command in the app

def save_uploaded_files(uploaded_files, target_folder, overwrite_checkbox):
  if not os.path.exists(target_folder):
    os.makedirs(target_folder)

    for uploaded_file in uploaded_files:
        file_path = os.path.join(target_folder, uploaded_file.name)
        if os.path.exists(file_path):
            if overwrite_checkbox:
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                    st.success(f"File {uploaded_file.name} uploaded successfully (overwritten).")

            else:
                st.info(f"Skipping '{uploaded_file.name}' due to existing file.")
        else:
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
                st.success(f"File {uploaded_file.name} uploaded successfully!")

    st.session_state['uploaded'] = True  # Update session state for successful upload
    

if 'uploaded' not in st.session_state:
  st.session_state['uploaded'] = False  # Initialize session state

with h.l.st.sidebar:
    uploaded_files = h.l.st.file_uploader(label="Upload the Detailed Statmement you got from MF Central", 
                                          accept_multiple_files=True)
    overwrite_checkbox = st.checkbox("Overwrite if FIle Exists ?")
    if uploaded_files:
        save_uploaded_files(uploaded_files, c.rel_data_folder, overwrite_checkbox)


row2_col_1, row2_col_2= h.l.st.columns(2)

with row2_col_1:
    h.st_plot_overall(d2)
with row2_col_2:
    h.plot_pnl(d2)

with h.l.st.expander("Funds Comparison"):
    h.st_comparison(d1)

h.make_heatmap(d1, c.as_of_date, c.percent_return,c.mf_key, 'blues')
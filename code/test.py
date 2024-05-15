
import helper_functions as h
import config as c
import time
import os
import streamlit as st


d1, d2 = h.prepare_data(c.rel_data_folder)
h.set_config() # Should be the first StrealLit Command in the app



h.st_comparison(d1)


# import plotly.express as px

# # z = [[.1, .3, .5, .7, .9],
# #      [1, .8, .6, .4, .2],
# #      [.2, 0, .5, .7, .9],
# #      [.9, .8, .4, .2, 0],
# #      [.3, .4, .5, .7, 1]]

# fig = px.imshow(d1, text_auto=True)
# fig.show()asdfa
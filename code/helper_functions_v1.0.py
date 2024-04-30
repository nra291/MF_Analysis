import library as l
import config as c


import warnings

# Suppress FutureWarnings from pandas
warnings.simplefilter(action='ignore', category=FutureWarning)


def get_full_path(file, sub_folder=None):

    rel_folder = "data"

    if sub_folder != None:
        rel_folder = rel_folder + "/" + sub_folder

    print(f"Relative Folder is {rel_folder}\n")
    print(f"Sub Folder is {sub_folder}\n")

    current_path = l.Path(__file__).parent  # Get the parent directory of the current script
    main_path = current_path.parent
    relative_path = l.Path(rel_folder) / file  # Construct a relative path using pathlib operators
    full_path = main_path / relative_path
    return full_path



def read_detailed(file, sub_folder=None):
    df_d = l.pd.read_excel(get_full_path(file, sub_folder),header=1)
    df_d = df_d[df_d['NAV'] != 0]
    df_d['Day'] = l.pd.to_datetime(df_d['Date']).dt.day
    df_d['Month'] = l.pd.to_datetime(df_d['Date']).dt.month
    df_d['Year'] = l.pd.to_datetime(df_d['Date']).dt.year
    return df_d


def read_consol(file, as_of_date, sub_folder=None):
    print(f"Sub Folder is {sub_folder}\n")
    df_c = l.pd.read_excel(get_full_path(file, sub_folder),header=1)
    df_c["As_of_Date"] = l.pd.to_datetime(as_of_date)
    return df_c


def get_filenames(folder_path):
  xlsx_filenames = []
  for filename in l.os.listdir(folder_path):
    if filename.endswith(".xlsx"):
      # Get filename without extension
      filename_without_ext = l.os.path.splitext(filename)[0]
      xlsx_filenames.append(filename_without_ext)
  return xlsx_filenames


def read_data_new(file_path):
    import pandas as pd
    from openpyxl import load_workbook, styles

    def custom_default_style():
        default_style = styles.NamedStyle(name="DefaultStyle")
        default_style.font = styles.Font(name="Calibri", size=11)
        default_style.alignment = styles.Alignment(horizontal="left", vertical="center")
        return default_style

    with pd.ExcelFile(file_path) as xlsx:
        # Load the workbook and apply the custom style
        wb = load_workbook(xlsx)
        wb.set_default_style(custom_default_style())

        # Read the data from a particular sheet
        df = pd.read_excel(xlsx, sheet_name=0, skiprows=11)  # Replace 'Sheet1' with actual sheet name
        return df
    # Continue working with your DataFrame (df)



def read_data(file_path):
  try:
    # Read data using pandas, skip first 9 rows (start from row 10)
    df = l.pd.read_excel(file_path, sheet_name=0, skiprows=11)
    return df
  except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
    return None

def consolidate_data():
    folder_path = "/Users/nra29/GDrive - DL02/MF_Analysis/data/Excel CAS/2024"  # Replace with your actual folder path
    xlsx_filenames = get_filenames(folder_path)
    df_final = l.pd.DataFrame()

    idx = 0
    if xlsx_filenames:
        for filename in xlsx_filenames:
            df_day = read_data(folder_path + '/' + filename + '.xlsx')
            # print(folder_path + '/' + filename + '.xlsx')
            idx = idx + 1
            df_day[c.as_of_date] = l.pd.to_datetime(filename)
            if idx == 1:
                df_final = df_day
                
            else:
                df_final = l.pd.concat([df_final, df_day], axis=1, ignore_index=True)
                    # Append the new data to the DataFrame
                df_final = df_final.append(df_day, ignore_index=True)
                print("- - - - - - - - -Number of rows added in DataFrame:", df_day.shape[0], '\n')

        print("- - - - - - - - -Total Number of rows added in DataFrame:", df_final.shape[0], '\n')
        return df_final
    
    else:
        print("No xlsx files found in the specified folder.")
        return None



# Remove unwanted strings
def remove_strings(text):
    text = text.lower()
    text = text.replace("-", "")
    text = text.replace("growth", "")
    text = text.replace("fund", "")
    text = text.replace("direct", "")
    text = text.replace("plan", "")
    text = text.replace("option", "")

    text = text.replace("quant quantamental", "QQM")
    text = text.replace("quant momentum", "QMO")
    text = text.replace("quant small cap", "QSC")
    text = text.replace("quant flexi cap", "QFC")
    text = text.replace("quant liquid    ", "QLI")

    text = text.replace("hdfc small cap", "HSC")
    text = text.replace("icici prudential nifty alpha lowvolatility 30 etf fof    ", "IAL")
    text = text.replace("parag parikh liquid     ", "PLI")
    text = text.replace("parag parikh flexi cap     (formerly parag parikh long term value )", "PFC")


    text = text.replace("nippon india small cap", "NSC")
    text = text.replace("nippon india liquid", "NLI")
    text = text.replace("nippon india", "NIP") # always keep it at the last

    text = text.replace("uti liquid  (formerly uti liquid cash )", "ULI")


    text = text.replace(" ", "") # Remove unwanted spaces at the last

    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")

    return text


    
# Stream Lit Function with Single Dashboard
def sl_single(df):
    # Sidebar for filtering
    l.st.sidebar.title('Filters')
    selected_amc = l.st.sidebar.selectbox(c.amc, df[c.amc].unique())
    selected_category = l.st.sidebar.selectbox(c.category, df[c.category].unique())
    selected_scheme = l.st.sidebar.selectbox(c.scheme, df[(df[c.amc] == selected_amc) & (df[c.category] == selected_category)][c.scheme].unique())
    selected_folio = l.st.sidebar.selectbox(' ', df[df[c.scheme] == selected_scheme][c.folio].unique())

    # Filter data based on selection
    # filtered_df = df[(df['Scheme Name'] == selected_scheme) & (df['Month'] == selected_month) & (df['Year'] == selected_year) ]
    filtered_df = df[(df[c.scheme] == selected_scheme) & (df[c.folio] == selected_folio)]

    # Display filtered data
    # l.st.write('Filtered Data:', filtered_df)

    # Visualizations
    l.st.subheader('Visualizations')

    # Plot : "Invested & Current Value over Time"
    fig = l.px.line(
        filtered_df,
        x=c.as_of_date,
        y=["Invested Value", "Current Value"],
        title="Invested & Current Value over Time"
    )
    l.st.plotly_chart(fig)


    # Plot : Returns over time
    fig = l.px.line(filtered_df, x=c.as_of_date, y='Returns', title='Returns over Time')
    l.st.plotly_chart(fig)

    # Plot : Units over time
    fig = l.px.line(filtered_df, x=c.as_of_date, y='Units', title='Units over Time')
    l.st.plotly_chart(fig)



# Stream Lit Function with Tabs
def sl_tabs(df):


    # Visualizations
    l.st.subheader('Mutual Funds Portfolio')

    selected_category = l.st.toggle('Fund Category')

    if selected_category:
        l.st.write('Equity')
    else:
        l.st.write('Liquid')



    tab1, tab2 = l.st.tabs(["Single Fund-Folio", "Multiple Funds"])

    with tab1:

        filtered_df = df

        # --------------------------------- -------- ----------- Data Selections
        l.st.subheader('Fund Selections')
        selected_amc = l.st.selectbox(c.amc, filtered_df[c.amc].unique(), key='001')
        selected_scheme = l.st.selectbox(c.scheme, filtered_df[(filtered_df[c.amc] == selected_amc) & (filtered_df[c.category] == selected_category)][c.scheme].unique(), key='002')
        selected_folio = l.st.selectbox(' ', filtered_df[filtered_df[c.scheme] == selected_scheme][c.folio].unique(), key='003')

        # Filter data based on selection
        filtered_df = df[(df[c.scheme] == selected_scheme) & (df[c.folio] == selected_folio)]
        # --------------------------------- -------- ----------- 

        # Plot : "Invested & Current Value over Time"
        fig = l.px.line(
            filtered_df,
            x=c.as_of_date,
            y=["Invested Value", "Current Value"],
            title="Invested & Current Value over Time"
        )
        l.st.plotly_chart(fig)


        # Plot : Returns over time
        fig = l.px.line(filtered_df, x=c.as_of_date, y='Returns', title='Returns over Time')
        l.st.plotly_chart(fig)


    with tab2:

        filtered_source = df
        filtered_target = df
        
        # --------------------------------- -------- ----------- Source Selections
        l.st.subheader('Source Selections')
        source_amc = l.st.selectbox(c.amc, filtered_source[c.amc].unique(), key='004')
        source_scheme = l.st.selectbox(c.scheme, filtered_source[(filtered_source[c.amc] == source_amc) & (filtered_source[c.category] == selected_category)][c.scheme].unique(), key='005')
        source_folio = l.st.selectbox(' ', filtered_source[filtered_source[c.scheme] == source_scheme][c.folio].unique(), key='006')

        # Filter data based on selection
        filtered_source = filtered_source[(filtered_source[c.scheme] == source_scheme) & (filtered_source[c.folio] == source_folio)]
        # --------------------------------- -------- ----------- 

        # --------------------------------- -------- ----------- target Selections
        l.st.subheader('Target Selections')
        target_amc = l.st.selectbox(c.amc, filtered_target[c.amc].unique(), key='007')
        target_scheme = l.st.selectbox(c.scheme, filtered_target[(filtered_target[c.amc] == target_amc) & (filtered_target[c.category] == selected_category)][c.scheme].unique(), key='008')
        target_folio = l.st.selectbox(' ', filtered_target[filtered_target[c.scheme] == target_scheme][c.folio].unique(), key='009')

        # Filter data based on selection
        filtered_target = filtered_target[(filtered_target[c.scheme] == target_scheme) & (filtered_target[c.folio] == target_folio)]
        # --------------------------------- -------- ----------- 
        
        data = l.pd.concat([filtered_source, filtered_target], axis=0)

        chart = l.alt.Chart(data).mark_circle().encode(
                x=c.as_of_date,
                y=c.returns,
                color=c.amc,
                ).interactive()
        l.st.altair_chart(chart, theme="streamlit", use_container_width=True)




# Stream Lit Function with Tabs
def sl_tabs_2(df):


    selected_category = l.st.toggle('Fund Category')

    if selected_category:
        l.st.write('Equity')
    else:
        l.st.write('Liquid')


    


    # Visualizations
    l.st.subheader('Visualizations')



    # --------------------------------- -------- ----------- Source Selections
    l.st.subheader('Source Selections')
    source_amc = l.st.selectbox(c.amc, df[c.amc].unique())
    source_scheme = l.st.selectbox(c.scheme, df[(df[c.amc] == source_amc) & (df[c.category] == selected_category)][c.scheme].unique())
    source_folio = l.st.selectbox(' ', df[df[c.scheme] == source_scheme][c.folio].unique())

    # Filter data based on selection
    filtered_source = df[(df[c.scheme] == source_scheme) & (df[c.folio] == source_folio)]
    # --------------------------------- -------- ----------- 

    # --------------------------------- -------- ----------- target Selections
    l.st.subheader('Target Selections')
    target_amc = l.st.selectbox(c.amc, df[c.amc].unique())
    target_scheme = l.st.selectbox(c.scheme, df[(df[c.amc] == target_amc) & (df[c.category] == selected_category)][c.scheme].unique())
    target_folio = l.st.selectbox(' ', df[df[c.scheme] == target_scheme][c.folio].unique())

    # Filter data based on selection
    filtered_target = df[(df[c.scheme] == target_scheme) & (df[c.folio] == target_folio)]
    # --------------------------------- -------- ----------- 
    
    data = l.pd.concat([filtered_source, filtered_target], axis=0)

    chart = l.alt.Chart(data).mark_circle().encode(
            x=c.as_of_date,
            y=c.returns,
            color=c.amc,
            ).interactive()
    l.st.altair_chart(chart, theme="streamlit", use_container_width=True)



def sl_multi(df):

    sorted_fund_keys = sorted(df["mf_key"].unique())
    options = l.st.multiselect(
        'Select the Funds to compare',
        sorted_fund_keys)

    if options:
        # Filter the DataFrame based on selected options
        filtered_df = df[df['mf_key'].isin(options)]
        # l.st.line_chart(filtered_df, x = c.as_of_date, y = c.percent_return, color = c.mf_key)

        
        # Create the line chart with hover template
        fig = l.px.line(filtered_df, x = c.as_of_date, y = c.percent_return, color = c.mf_key, hover_data=c.percent_return)
        l.st.plotly_chart(fig)



    else:
        # Display a message if no options are selected
        l.st.write("Please select at least one fund for comparison.")



def sl_tab_chart(df, f_key):

    sorted_fund_keys = sorted(df["mf_key"].unique())
    options = l.st.multiselect(
        'Select the Funds to compare',
        # sorted_fund_keys)
        sorted_fund_keys, key=f_key)

    if options:
        # Filter the DataFrame based on selected options
        filtered_df = df[df['mf_key'].isin(options)]


        # Create the line chart with hover template
        fig = l.px.line(filtered_df, x = c.as_of_date, y = c.percent_return, color = c.mf_key,hover_data=c.percent_return)#,responsive=True, width=400, height=300)
                    # Update layout to disable zoom and adjust font size (optional)
        fig.update_layout(
                        xaxis_fixedrange=True,  # Fix x-axis range
                        yaxis_fixedrange=True,  # Fix y-axis range
                        # Optional: Adjust font size for mobile readability
                        title_font_size=14,
                        xaxis_title_font_size=12,
                        yaxis_title_font_size=12,)
        
        # fig.update_layout(width=1440, height=600)
        
        l.st.plotly_chart(fig)



    else:
        # Display a message if no options are selected
        l.st.write("Please select at least one fund for comparison.")


# Stream Lit Function with Tabs
def sl_tabs():

    l.st.set_page_config(layout="wide")

    # Add this CSS to your app
    body = {
        "margin": "0",
        "padding": "0",
        "overflow": "hidden",
    }

    l.st.write(f"<style>{body}</style>", unsafe_allow_html=True)

    # # Visualizations
    # l.st.subheader('SBN - Portfolio')
    # l.st.text("")
    # selected_category = l.st.toggle('Include Liquid Funds ?')
    # l.st.text("")
    # l.st.text("")



    tab1, tab2, tab3 = l.st.tabs(["AKDPA0263E", "AKDPA0314N", "AIXPA3414D" ])

    with tab1:

        df_s = prepare_data(c.rel_data_folder)

        # sl_line_chart(df_s)
        sl_tab_chart(df_s, "k1")

    with tab2:

        l.st.text("")
        df_b = prepare_data(c.rel_data_folder)
        # sl_line_chart(df_b)
        sl_tab_chart(df_s, "k2")

    with tab3:

        l.st.text("")
        df_n = prepare_data(c.rel_data_folder)
        # sl_line_chart(df_n)
        sl_tab_chart(df_s, "k3")
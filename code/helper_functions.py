import os
import pandas as pd
import library as l
import config as c


class NoDataException(Exception):
    pass

class NoFilesFoundException(Exception):
    pass

def prepare_data_old(folder):
    """
    Prepare data from xlsx files in the specified folder.

    Args:
        folder (str): The folder path containing the xlsx files.

    Returns:
        pd.DataFrame: The prepared data.

    Raises:
        NoDataException: If no data was read for processing.
        NoFilesFoundException: If no xlsx files were found in the specified folder.
    """
    xlsx_filenames = get_filenames(folder)
    df_main = pd.DataFrame()

    if xlsx_filenames:
        df_list = []
        for filename in xlsx_filenames:
            df_day = read_data(os.path.join(folder, f'{filename}.xlsx'))
            if df_day is not None:
                df_day['As_of_Date'] = filename
                df_list.append(df_day)

        if df_list:
            df_main = pd.concat(df_list, ignore_index=True, sort=False)
            df_main = data_massaging(df_main)
            return df_main
        else:
            raise NoDataException("No Data was read for processing")
    else:
        raise NoFilesFoundException("No xlsx files found in the specified folder.")

def prepare_data(folder):
    xlsx_filenames = get_filenames(folder)
    df_all_days = pd.DataFrame()
    df_total_inv = pd.DataFrame()

    if xlsx_filenames:
        df_list_day = []
        df_list_total_inv = []

        for filename in xlsx_filenames:
            file_data = read_data(os.path.join(folder, filename+'.xlsx'))
            if file_data is not None:
                # Get all data from row 12 onwards
                df_day = file_data.iloc[12:]
                # Assign the first row values to column names
                df_day.columns = file_data.iloc[11]  
                # Get the name from the first row
                df_day['Person'] = file_data.iloc[0][1]
                # Get the To date from row 7
                todate = l.datetime.datetime.strptime((file_data.iloc[6][1]).strip(), "%d-%b-%Y")
                df_day['As_of_Date'] = todate
                # Keep appending the transaction data for all days
                df_list_day.append(df_day)
                

                # Get data from rows 9 and 10
                df_inv = file_data.iloc[9:10,:3]
                # Assign the first row values to column names
                df_inv.columns = file_data.iloc[8,:3]
                # Get the To date from row 7
                df_inv['As_of_Date'] = todate
                # Keep appending the total Investment data for all days
                df_list_total_inv.append(df_inv)

        if df_list_day:
            df_all_days = pd.concat(df_list_day, ignore_index=True)
            df_all_days = data_massaging(df_all_days)

            df_total_inv = pd.concat(df_list_total_inv, ignore_index=True)
            df_total_inv = data_massaging_2(df_total_inv)

            return df_all_days, df_total_inv
        else:
            raise Exception("No Data was read for processing")
    else:
        raise Exception("No xlsx files found in the specified folder.")

def data_massaging_2(df):
    df[c.current_portfolio_value] = df[c.current_portfolio_value].astype(float)
    df[c.total_inv] = df[c.total_inv].astype(float)
    df[c.pnl] = df[c.pnl].astype(float)

    if c.as_of_date in df.columns:
        df[c.as_of_date] = l.pd.to_datetime(df[c.as_of_date])
        df[c.as_of_date] = df[c.as_of_date].dt.strftime("%d-%m-%Y")
        df[c.as_of_date] = l.pd.to_datetime(df[c.as_of_date], format="%d-%m-%Y")

    # sort the data on AS_of_Date
    df.sort_values(by=c.as_of_date, inplace=True)

    return df

def ensure_relative_path(folder):
    # Normalize the path first
    normalized_path = l.os.path.normpath(folder)
    
    # Convert to relative path from current working directory
    relative_path = l.os.path.relpath(normalized_path)
    
    return relative_path

def get_filenames(folder_path):
  xlsx_filenames = []
  for filename in l.os.listdir(folder_path):
    if filename.endswith(".xlsx") and not filename.startswith('~'):
      # Get filename without extension
      filename_without_ext = l.os.path.splitext(filename)[0]
      xlsx_filenames.append(filename_without_ext)
  return xlsx_filenames

def read_data(file_path):
  try:
    # Read data using pandas, skip first 9 rows (start from row 10)
    # df = l.pd.read_excel(file_path, sheet_name=0, skiprows=11)
    df = l.pd.read_excel(file_path, header=None)
    return df
  except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
    return None

def data_massaging(df):
   #Remove all the Rows with no values

    df[c.current] = df[c.current].astype(float)
    df[c.invested] = df[c.invested].astype(float)

    df = df[df[c.invested] != 0]

    print(df.columns)

    if c.as_of_date in df.columns:
        df[c.as_of_date] = l.pd.to_datetime(df[c.as_of_date])
        df[c.as_of_date] = df[c.as_of_date].dt.strftime("%d-%m-%Y")
        df[c.as_of_date] = l.pd.to_datetime(df[c.as_of_date], format="%d-%m-%Y")

    # sort the data on AS_of_Date
    df.sort_values(by=c.as_of_date, inplace=True)

    df = consolidate_categories(df)

    df[c.scheme_short] = df[c.scheme].apply(remove_strings_2)

    # Convert the 'Folio No.' column to string type
    df[c.folio] = df[c.folio].astype(str)

    # Concatenate the values of the 'Category' and 'Folio No.' columns into a new column named 'Combined'
    df[c.mf_key] = df[c.scheme_short].str.cat(df[c.folio], sep='-')


    # Calculate percentage return, round to two decimals, and create a new column
    df[c.percent_return] = ((df[c.current] - df[c.invested]) / df[c.invested] * 100).round(2)

    df = df[df[c.scheme_short]!=c.nip]

    return df

def consolidate_categories(df):
# prompt: Convert category values from EQUITY to Equity,  Liquid Fund to Liquid, Cash to Liquid
    df['Category'] = df['Category'].replace(['EQUITY'], 'Equity')
    df['Category'] = df['Category'].replace(['EQUITY FUND'], 'Equity')
    df['Category'] = df['Category'].replace(['LIQUID FUND'], 'Liquid')
    df['Category'] = df['Category'].replace(['CASH'], 'Liquid')
    df['Category'] = df['Category'].replace(['LIQUID'], 'Liquid')
    return df

def remove_strings(text):
#   Remove unwanted strings
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
    text = text.replace("uti nifty200 momentum 30 index", "UTI-Momentum")
    # UTI Nifty200 Momentum 30 Index Fund - Direct Plan


    text = text.replace(" ", "") # Remove unwanted spaces at the last

    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")

    return text

def remove_strings_2(text):
    text = text.lower()
    text = text.replace("-", "")
    text = text.replace("growth", "")
    text = text.replace("fund", "")
    text = text.replace("direct", "")
    text = text.replace("plan", "")
    text = text.replace("option", "")

    text = text.replace("quant quantamental", "Quant-Quantamental")
    text = text.replace("quant momentum", "Quant-Momentum")

    text = text.replace("quant small cap", "Quant-SmallCap")

    text = text.replace("quant flexi cap", "Quant-FlexiCap")

    text = text.replace("quant liquid    ", "Quant-Liquid")

    text = text.replace("hdfc small cap", "HDFC-SmallCap")
    
    text = text.replace("icici prudential nifty alpha lowvolatility 30 etf fof    ", "ICICI-AlphaLow")
    
    text = text.replace("parag parikh liquid     ", "PPFAS-Liquid")
    text = text.replace("parag parikh flexi cap     (formerly parag parikh long term value )", "PPFAS-FlexiCap")


    text = text.replace("nippon india small cap", "Nippon-SmallCap")

    text = text.replace("nippon india liquid", "Nippon-Liquid")

    text = text.replace("nippon india", "NIP") # always keep it at the last
    text = text.replace("nippon india", "NIP") # always keep it at the last

    text = text.replace("uti liquid  (formerly uti liquid cash )", "UTI-Liquid")
    text = text.replace("uti nifty200 momentum 30 index", "UTI-Momentum")

    text = text.replace(" ", "") # Remove unwanted spaces at the last

    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    # text = text.replace("", "")

    return text

def sl_line_chart_1(df):

    sorted_fund_keys = sorted(df["mf_key"].unique())
    options = l.st.multiselect(
        'Select the Funds to compare',
        sorted_fund_keys)
        # sorted_fund_keys, key=l.np.random.randint(1, 10000))

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

def set_config():
    l.st.set_page_config(
    page_title="SBN Portfolio", # Title for the Web-Page in the browser
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="collapsed")

    l.st.title(" :bar_chart: SBN Portfolio") # Title inside the Dashboard
    l.st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

def st_sidebar(df):

    # Using object notation
    add_selectbox = l.st.sidebar.selectbox(
        "Name",
        ("Silky", "Bablu", "Nitin")
    )
    l.st.text("")

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = l.st.selectbox('Select a color theme', color_theme_list)

    checked_values = []  # Empty list to store selected checkbox values
    key_values = []  # Empty list to store selected checkbox values

    # Using "with" notation
    with l.st.sidebar:
        sorted_fund_keys = sorted(df["mf_key"].unique())
        for fund in sorted_fund_keys:
            # l.st.checkbox(label=fund, key=fund)
            checked_values.append(l.st.checkbox(label=fund, key=fund))


    key_values = [sorted_fund_keys[i] for i in range(len(sorted_fund_keys)) if checked_values[i]]


    # Filter the DataFrame based on selected options
    filtered_df = df[df['mf_key'].isin(key_values)]

    line_chart(filtered_df,c.as_of_date, c.percent_return, c.mf_key)

def st_comparison(df):
    sorted_fund_keys = sorted(df["mf_key"].unique()) # Only Select Equity Funds
    default_options = sorted(df[(df['AMC Name'] == 'Quant MF') & (df['Category']=='Equity') & (df[c.scheme_short] != 'ICICI-AlphaLow')]["mf_key"].unique()) # Only Select Equity Funds
    #  = sorted(df[(df['Category']=='Equity') & ()])]["mf_key"].unique()) # Only Select Equity Funds
    options = l.st.multiselect(
        label='Select the Funds to compare',
        options=sorted_fund_keys,
        default=default_options)

    if options:
        # Filter the DataFrame based on selected options
        filtered_df = df[df['mf_key'].isin(options)]
        line_chart(filtered_df,c.as_of_date, c.percent_return, c.mf_key)

def line_chart(input_df, input_x, input_y, input_color):
    # Create the line chart with hover template
    fig = l.px.line(input_df, 
                    x = input_x, 
                    y = input_y, 
                    color = input_color,
                    markers=True,
                    text=c.percent_return,
                    hover_data=c.percent_return,
                    height=1000)
    
    fig.update_layout(
        xaxis=dict(
            showspikes=True,  # Enable hover spike lines
            spikemode="across",  # Draw spike line across the plot
            spikesnap="cursor",  # Snap spike to cursor position
            showline=True,  # Show x-axis line
            showgrid=True,  # Show grid lines
        ),
        hovermode="x",  # Display x-axis value on hover
        
    )

    
    l.st.plotly_chart(fig, use_container_width=True)
    
def plot_pnl(df):
    fig = l.px.line(df,
                    x=c.as_of_date,
                    y=[c.pnl],
                    title="PnL Over Time", 
                    )

    fig.update_layout(
        xaxis=dict(
            showspikes=True,  # Enable hover spike lines
            spikemode="across",  # Draw spike line across the plot
            spikesnap="cursor",  # Snap spike to cursor position
            showline=True,  # Show x-axis line
            showgrid=True,  # Show grid lines
        ),
        hovermode="x",  # Display x-axis value on hover
    )

    l.st.plotly_chart(fig, use_container_width=True)

def st_plot_overall(df):

    fig = l.px.line(df,
                    x=c.as_of_date,
                    y=[c.total_inv, c.current_portfolio_value],
                    title="Invested & Current Value over Time"
                    )
    
    fig.update_layout(
        xaxis=dict(
            showspikes=True,  # Enable hover spike lines
            spikemode="across",  # Draw spike line across the plot
            spikesnap="cursor",  # Snap spike to cursor position
            showline=True,  # Show x-axis line
            showgrid=True,  # Show grid lines
        ),
        hovermode="x",  # Display x-axis value on hover
    )

    l.st.plotly_chart(fig, use_container_width=True)

def plot_donut(df, chart_title, category_col, values_col):
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    data = df.groupby(category_col)[values_col]

    # Create donut chart with plotly express
    fig = px.pie(
        data, values=values_col, names=category_col, title=chart_title, hole=0.8
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)

def plot_mf_share(df):
    plot_donut(df, 'Fund Allocation', c.amc, c.invested)

def make_heatmap(input_df, input_x, input_y, input_color, input_color_theme):



    # Create the heatmap
    l.plt.figure(figsize=(10, 6))
    l.plt.pcolor(input_df[input_y], vmin=-50, vmax=50, cmap='RdBu_r')  # Colormap for red (negative) to blue (positive)

    # Add labels and title with customizations
    l.plt.xticks(l.np.arange(len(input_df['Date'])), rotation=45, ha='right')  # Use formatted dates for labels
    l.plt.yticks(l.np.arange(len(input_y)), input_y)
    l.plt.colorbar(label='Percentage Change (%)')
    l.plt.title('Daily Stock Percentage Changes (Generated from a DataFrame with Real Dates)')

    # Enhance readability with grid and annotation options (uncomment if desired)
    # l.plt.grid(True, which='both', linestyle='--', linewidth=0.5)  # Add grid lines

    # Annotate values on the heatmap (uncomment if desired)
    # for i in range(len(df['Date'])):
    #     for j in range(len(stocks)):
    #         l.plt.text(i, j, f"{df.iloc[j, i]:.2f}", ha='center', va='center', fontsize=8)  # Adjust formatting as needed

    l.plt.tight_layout()
    l.plt.show()

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

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

def prepare_data(folder, selected_person):
    xlsx_filenames = get_filenames(folder)
    df_all_days = pd.DataFrame()
    df_total_inv = pd.DataFrame()

    if xlsx_filenames:
        df_list_day = []
        df_list_total_inv = []

        for filename in xlsx_filenames:
            file_data = read_data(os.path.join(folder, filename+'.xlsx'))
            if file_data is not None:
                # Get the name from the first row
                person = ''
                # this converts first character to upper case and all other lower case.  Also removes leading spaces
                person = file_data.iloc[0][1].title().lstrip()  
                # Process Data only for the selected person
                if person == selected_person:

                    # Get all data from row 12 onwards
                    df_day = file_data.iloc[12:]
                    # Assign the first row values to column names
                    df_day.columns = file_data.iloc[11]  
                    df_day['Person'] = person
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
    df[c.category] = df[c.category].replace(['EQUITY'], c.equity)
    df[c.category] = df[c.category].replace(['EQUITY FUND'], c.equity)
    df[c.category] = df[c.category].replace(['LIQUID FUND'], 'Liquid')
    df[c.category] = df[c.category].replace(['CASH'], 'Liquid')
    df[c.category] = df[c.category].replace(['LIQUID'], 'Liquid')
    return df

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

    text = text.replace("GEETIKA ANAND", c.silky)
    text = text.replace("UMESH ANAND", c.bablu)
    text = text.replace("NITIN ANAND", c.nitin)
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
    l.st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

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
    default_options = sorted(df[(df['AMC Name'] == 'Quant MF') & (df[c.category]==c.equity) & (df[c.scheme_short] != 'ICICI-AlphaLow')]["mf_key"].unique()) # Only Select Equity Funds
    #  = sorted(df[(df[c.category]==c.equity) & ()])]["mf_key"].unique()) # Only Select Equity Funds
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

def plot_donut(df, chart_title, category_col, values_col, layout_col):
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    # Create donut chart with plotly express
    fig = px.pie(
        df, values=values_col, names=category_col, title=chart_title, hole=0.5
    )

    with layout_col:
        # layout_col.subheader(chart_title)
        # Display the chart in Streamlit
        st.plotly_chart(fig)

def plot_invested_share(df,col_val, layout_col):
    if col_val == c.mf_key:
        plot_donut(df, 'Allocation by Fund-Folio', col_val, c.invested, layout_col)
    elif col_val == c.amc:
        plot_donut(df, 'Allocation by AMC', col_val, c.invested, layout_col)

def plot_profit_share(df,col_val, layout_col):
    if col_val == c.mf_key:
        plot_donut(df, 'Profit by Fund-Folio', col_val, c.returns, layout_col)
    elif col_val == c.amc:
        plot_donut(df, 'Profit by AMC', col_val, c.returns, layout_col)

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

def plot_stacked_bar(df, x_value):

    if x_value == c.mf_key:
        my_title = 'Investment and Profits by Folio'
    elif x_value == c.amc:
        my_title = 'Investment and Profits by AMC'

    df[c.invested] = df[c.invested].astype(float)
    df[c.returns] = df[c.returns].astype(float)

    df = df.sort_values(by=c.percent_return, ascending=False)

    # Melt the dataframe
    df_melted = df.melt(id_vars=x_value, value_vars=[c.invested, c.returns], var_name='Type', value_name='Amount')

    # Create the stacked bar chart
    fig = l.px.bar(df_melted, x=x_value, y='Amount', color='Type', title=my_title)

    # df_melted[c.invested] = df_melted['Amount'].astype(float)

    # Add annotations for the percentage
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row[x_value],
            y=row[c.invested] + row[c.returns],
            text=f"{row[c.percent_return]:.2f}%",
            showarrow=False,
            yshift=10
        )

    # Update layout to increase the y-axis range
    # fig.update_yaxes(range=[0, max(df_melted['Amount'])*1.5])  # Increase range by 20%
    # fig.update_yaxes(type='linear')
    fig.update_layout(yaxis_tickformat=',d', yaxis_title='Value (Thousands)')


    l.st.plotly_chart(fig, use_container_width=True)


def summarize_key_amc(d1):
    # data_by_key = d1[d1[c.as_of_date] == d1.groupby(c.mf_key)[c.as_of_date].transform(max)][(d1[c.category]==c.equity)].sort_values(by=c.amc)
    # data_by_amc = d1[d1[c.as_of_date] == d1.groupby(c.amc)[c.as_of_date].transform(max)]
    # data_by_amc = data_by_amc[(data_by_amc[c.category]==c.equity)]

    d1[c.invested] = d1[c.invested].astype(float)
    d1[c.returns] = d1[c.returns].astype(float)

    # Convert As_of_Date to datetime if not already
    d1[c.as_of_date] = l.pd.to_datetime(d1[c.as_of_date])

    # Get the latest As_of_Date for each AMC using transform
    d1['Latest_As_of_Date'] = d1.groupby(c.amc)[c.as_of_date].transform('max')

    # Filter the DataFrame based on the latest As_of_Date
    latest_data = d1[d1[c.as_of_date] == d1['Latest_As_of_Date']].drop(columns=['Latest_As_of_Date'])


    # Filter the DataFrame based on the latest As_of_Date
    data_by_amc = latest_data.groupby(c.amc).agg({
        c.invested: 'sum',
        c.returns: 'sum',
        c.as_of_date: 'max'
    }).reset_index()

    # Calculate percentage return, round to two decimals, and create a new column
    data_by_amc[c.percent_return] = (( data_by_amc[c.returns] / data_by_amc[c.invested] ) * 100).round(2)
    data_by_amc[c.percent_return] = data_by_amc[c.percent_return].astype('float64')

    data_by_key = d1[d1[c.as_of_date] == d1.groupby(c.mf_key)[c.as_of_date].transform(max)][(d1[c.category]==c.equity)].sort_values(by=c.amc)

    data_by_amc.sort_values(c.percent_return, ascending=False).reset_index(drop=True)

    return data_by_key, data_by_amc
import library as l
import config as c


def prepare_data(folder):
    xlsx_filenames = get_filenames(folder)
    df_main = l.pd.DataFrame()

    if xlsx_filenames:
        for filename in xlsx_filenames:
            
            df_day = read_data(folder + '/' + filename+'.xlsx')
            if df_day is not None:
                df_day['As_of_Date'] = filename
                df_main = l.pd.concat([df_main, df_day], ignore_index=True)
            

        if df_main is not None:
            df_main = data_massaging(df_main)
            return df_main
        else:
            print("No Data was read for processing")
            return None
        

    else:
        print("No xlsx files found in the specified folder.")



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
    df = l.pd.read_excel(file_path, sheet_name=0, skiprows=11)
    return df
  except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
    return None




def data_massaging(df):
   #Remove all the Rows with no values


    # filtered_data = list(filter(lambda row: not any(value == 0 for value in row), df))

    df = df[df[c.invested] != 0]


    # df = l.pd.DataFrame(df)
    # del filtered_data

    print(df.columns)

    if c.as_of_date in df.columns:
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



# prompt: Convert category values from EQUITY to Equity,  Liquid Fund to Liquid, Cash to Liquid

def consolidate_categories(df):
    df['Category'] = df['Category'].replace(['EQUITY'], 'Equity')
    df['Category'] = df['Category'].replace(['LIQUID FUND'], 'Liquid')
    df['Category'] = df['Category'].replace(['CASH'], 'Liquid')
    df['Category'] = df['Category'].replace(['LIQUID'], 'Liquid')
    return df



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



def sl_tab_chart(df, f_key):

    sorted_fund_keys = sorted(df["mf_key"].unique())
    options = l.st.multiselect(
        'Select the Funds to compare',
        # sorted_fund_keys)
        sorted_fund_keys, key=f_key)

    if options:
        # Filter the DataFrame based on selected options
        filtered_df = df[df['mf_key'].isin(options)]
        # l.st.line_chart(filtered_df, x = c.as_of_date, y = c.percent_return, color = c.mf_key)


        # Create the line chart with hover template
        fig = l.px.line(filtered_df, x = c.as_of_date, y = c.percent_return, color = c.mf_key, hover_data=c.percent_return)
        fig.update_layout(width=1440, height=600)
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

        l.st.text("")

        df_s = prepare_data(c.data_folder)

        # sl_line_chart(df_s)
        sl_tab_chart(df_s, "k1")

    with tab2:

        l.st.text("")
        df_b = prepare_data(c.data_folder)
        # sl_line_chart(df_b)
        sl_tab_chart(df_s, "k2")

    with tab3:

        l.st.text("")
        df_n = prepare_data(c.data_folder)
        # sl_line_chart(df_n)
        sl_tab_chart(df_s, "k3")
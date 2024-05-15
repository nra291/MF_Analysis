
import helper_functions as h
import config as c



def read_data(file_path):
  try:
    # Read data using pandas, skip first 9 rows (start from row 10)
    df = h.l.pd.read_excel(file_path, sheet_name=0, skiprows=0)
    return df
  except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
    return None


df = read_data('/Users/nra29/GDrive - DL02/MF_Analysis/data/Excel CAS/df_main.xlsx')

df["Scheme Name Short"] = df["Scheme Name"].apply(h.remove_strings)

# Convert the 'Folio No.' column to string type
df['Folio No.'] = df['Folio No.'].astype(str)

# Concatenate the values of the 'Category' and 'Folio No.' columns into a new column named 'Combined'
df['mf_key'] = df['Scheme Name Short'].str.cat(df['Folio No.'], sep='-')

# Calculate percentage return, round to two decimals, and create a new column
df["Percentage Returns"] = ((df["Current Value"] - df["Invested Value"]) / df["Invested Value"] * 100).round(2)

# Remove NIP as it has 800% Gain
df = df[df["Scheme Name Short"]!='NIP']

h.sl_multi(df)

h.sl_single(df)

# h.sl_tabs(df)

# -------------------- RUN STREAM LIT COMMAND -------
# streamlit run "/Users/nra29/GDrive - DL02/MF_Analysis/code/v_2.0.py"
# ----------------------------------------------------
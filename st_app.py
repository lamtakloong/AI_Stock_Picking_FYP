import streamlit as st
import os
import shutil
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime as dtt

import yfinance as yf



TODAY = dtt.today().strftime('%Y-%m-%d')
CLEARCACHE = ['stock_hist','output']
# Confit sidebar : auto expanded collapsed
st.set_page_config(initial_sidebar_state='auto')

@st.cache
def GetHKstockFromGoogleFinance():
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('temp/GFcred.json',scope)
    client = gspread.authorize(creds)
    sheet = client.open('stocklist').sheet1
    df_fa = pd.DataFrame(sheet.get_all_records())
    ##### 
    df_fa.to_csv('temp/stock_FA_GF.csv')
    df_fa = pd.read_csv('temp/stock_FA_GF.csv',index_col=0)
    df_fa['tradetime'] = pd.to_datetime(df_fa['tradetime']) 
    laset_tradedate = df_fa['tradetime'].max()
    df_fa = df_fa[df_fa.tradetime == laset_tradedate]
    df_fa = df_fa.drop(columns=['Symbol'])
    return df_fa

for d in CLEARCACHE:
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)

############## Loading Stock Data
st.title('AI Stock Picking')
data_load_state = st.text('Loading data...')
df_fa = GetHKstockFromGoogleFinance()
data_load_state.text(TODAY + ' Loading data...done!')

############## Display Stock Data
st.dataframe(df_fa)
# df = pd.DataFrame()
# symbols_name = df['symbols_name'] = df_fa['Symbol'] + ' ' + df_fa['name']
# symbols_name = df_fa['id']
# stock_choice = st.selectbox('Stock',(df_fa['name']))
# df_fa_loc = df_fa[(df_fa.name==stock_choice)].index.tolist()[0]
# df_fa_loc = df_fa['id'].iloc[df_fa_loc]
# st.write(stock_choice)
# df = pdr.get_data_yahoo(df_fa_loc)
# st.line_chart(df['Adj Close'])

df = pd.DataFrame(df_fa, columns= ['id', 'name'])
options = df.values.tolist()
option = st.selectbox("The selected Stock : ",options, 0)
df = pdr.get_data_yahoo(option[0])
chosen = st.radio('Atts',("Adj Close", "Close"))
st.write(f"You select {chosen}!")
st.line_chart(df[{chosen}])





###################### Testing #####################
### Widgets
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

### Layout
st.sidebar
# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)

# Checkbox
agree = st.sidebar.checkbox("I agree")
if agree:
    st.sidebar.checkbox("Great", value = True)

# Date
d3 = st.sidebar.date_input("range, no dates", [])
st.write(d3)

d3 = st.sidebar.date_input("Range, one date", [dtt.date(2019, 7, 6)])
st.write(d3)

d5 = st.sidebar.date_input("date range without default", [dtt.date(2019, 7, 6), dtt.date(2019, 7, 8)])
st.sidebar.write(d5)
    
    
# left_column, right_column = st.beta_columns(2)
# # You can use a column just like st.sidebar:
# left_column.button('Press me!')

# # Or even better, call Streamlit functions inside a "with" block:
# with right_column:
#     chosen = st.radio(
#         'Sorting hat',
#         ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
#     st.write(f"You are in {chosen} house!")

###########################################

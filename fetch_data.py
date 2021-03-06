import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import pprint

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('temp/GFcred.json',scope)
client = gspread.authorize(creds)
sheet = client.open('stocklist').sheet1
df = pd.DataFrame(sheet.get_all_records())
df.to_csv('temp/stock_FA_GF.csv',index=False)
df_fa = pd.read_csv('temp/stock_FA_GF.csv')
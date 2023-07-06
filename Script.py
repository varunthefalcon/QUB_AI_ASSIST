import gspread
import streamlit as st
import pandas as pd

gc = gspread.service_account(
    filename="D:/UK/assignment/dissertation/beaming-bliss-387514-ff0710635e8b.json"
)

sh = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1MFytQYnb3xHhBW3-hWcPrb2vni0mBcYDkT9yca7UlwI"
)

worksheet = sh.get_worksheet(0)

val = worksheet.acell("A1").value


list_of_lists = worksheet.get_all_values()

print(val, len(list_of_lists), list_of_lists)

st.write("Here's our first attempt at using data to create a table:")
st.write(
    pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
)

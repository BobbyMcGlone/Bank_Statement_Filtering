import re
import tkinter
import pandas as pd
from tkinter import filedialog as fd
from tkinter.constants import TRUE

BANK_STATEMENT_VALUES = 'Amount'
BANK_STATEMENT_INFO   = 'Description'

def filter_dataframe(dataframe, unwanted_keywords):
    unwanted_transactions = dataframe[dataframe[BANK_STATEMENT_INFO].str.contains('|'.join(unwanted_keywords))]
    dataframe = dataframe.drop(unwanted_transactions.index)
    return dataframe

def CalculatePurchases(dataframe, specifiers):
    AmountSpent = 0
    purchase_list = []
    pattern = '|'.join(specifiers)
    purchases = dataframe.loc[dataframe[BANK_STATEMENT_INFO].str.extract(f'({pattern})', expand=False).notna()]
    AmountSpent = purchases[BANK_STATEMENT_VALUES].sum()
    purchase_list = purchases[[BANK_STATEMENT_INFO, BANK_STATEMENT_VALUES]].values.tolist()
    dataframe = dataframe.drop(purchases.index)
    return int(AmountSpent), dataframe, purchase_list, pattern

filename = fd.askopenfilename()
specifiers_df = pd.read_csv('specifiers.csv', header=0)
specifiers_df.columns = specifiers_df.columns.str.strip()
df = pd.read_csv(filename)
df_copy = df.copy()

categories = {"GroceriesSpecifiers":0, "HomeRenoSpecifiers":0,
              "TakeAwaysSpecifiers":0, "PartyingSpecifiers":0, "BillsSpecifiers":0,
              "PetrolSpecifiers":0, "BuyingThingsSpecifiers":0, "PhysicalHealthSpecifiers":0,
              "PayeesSpecifiers":0, "DirectCredits":0}

purchase_df = pd.DataFrame(columns=["Category", "Description", "Amount"])
takeAway_purchase_list = []

for category_name in categories.keys():
    if category_name == "PetrolSpecifiers":
        unwanted_keywords_petrol = ["2 Degrees", 'NIGHT \'N DAY']
        df = filter_dataframe(df, unwanted_keywords_petrol)
    keyword = specifiers_df[category_name].dropna().tolist()
    AmountSpent, df, purchase_list, pattern = CalculatePurchases(df, keyword)
    purchases = df_copy.loc[df_copy[BANK_STATEMENT_INFO].str.extract(f'({pattern})', expand=False).notna()]
    df_copy = df_copy.drop(purchases.index)
    if category_name == "PetrolSpecifiers":
        for purchase in purchase_list:
            if purchase[1] < 80:
                takeAway_purchase_list.append(purchase)
                purchase_list.remove(purchase)
    categories[category_name] += AmountSpent
    for purchase in purchase_list:
        purchase_df = purchase_df.append({"Category": category_name, "Description": purchase[0], "Amount": purchase[1]}, ignore_index=True)
purchase_df.to_csv("purchases.csv")

# print transactions that were not added to any categories
df_copy = filter_dataframe(df_copy, [i for cat in categories for i in specifiers_df[cat].dropna().tolist()])
print("Transactions not added to any categories: ")
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', 100)
print(df_copy)

takeAway_amount = sum([purchase[1] for purchase in takeAway_purchase_list])
categories["TakeAwaysSpecifiers"] += takeAway_amount

for category_name, AmountSpent in categories.items():
    print(f"Amount spent on {category_name}: ${AmountSpent}")

# print category expenses
while True:
    category = input("Enter category name to print expenses for (enter 'q' to quit): ")
    if category == "q":
        break
    if category not in categories.keys():
        print("Invalid category name.")
        continue
    print(purchase_df.loc[purchase_df["Category"] == category])

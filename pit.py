import pandas as pd
from datetime import datetime

exchange_rate = 0
exchange_rate_table = 0
transaction_date_ymd = 0

stocks = {}
pln_stocks_2023 = {}
pln_stocks_2024 = {}

price = 0
pln_2023 = 0
pln_2024 = 0


def exchange_rate_year(exch_year):
    global exchange_rate_table
    if exch_year[:4] == '2023':
        exchange_rate_table = pd.read_excel('2023kurssredni.xlsx')
    elif exch_year[:4] == '2024':
        exchange_rate_table = pd.read_excel('2024kurssredni.xlsx')


def adjust_date(date_str):
    global transaction_date_ymd
    date_int = int(date_str)
    date_int -= 1
    transaction_date_ymd = str(date_int)
    return


def creating_stock_indexes():
    if stock_name not in pln_stocks_2023 and stock_name not in pln_stocks_2024:
        pln_stocks_2023[stock_name] = [0, 0]
        pln_stocks_2024[stock_name] = [0, 0]


def converting_to_pln(t_date):
    global pln_2023
    global pln_2024
    global transaction_date_ymd
    exchange_rate_table['data'] = exchange_rate_table['data'].astype(str).str.replace('-', '').str[:8]
    transaction_date_ymd = t_date.replace('-', '')[:8]
    while True:
        filtered_row = exchange_rate_table[(exchange_rate_table['data']) == (str(int(transaction_date_ymd) - 1))]
        if not filtered_row.empty:
            usd_value = filtered_row['1 USD'].iloc[0]
            if transaction_type in ["SELL - MARKET", "SELL - STOP"] and transaction_date[:4] == '2023':
                pln_stocks_2023[stock_name] = [pln_stocks_2023[stock_name][0] - stock_quantity,
                                               pln_stocks_2023[stock_name][1] + (stock_price * usd_value)]
            if transaction_type in ["SELL - MARKET", "SELL - STOP"] and transaction_date[:4] == '2024':
                if pln_stocks_2023[stock_name][0] != 0 and pln_stocks_2023[stock_name][1] < 0:
                    pln_stocks_2024[stock_name][0] = pln_stocks_2024[stock_name][0] + pln_stocks_2023[stock_name][0]
                    pln_stocks_2024[stock_name][1] = pln_stocks_2024[stock_name][1] + pln_stocks_2023[stock_name][1]
                    pln_stocks_2023[stock_name][0] = 0
                    pln_stocks_2023[stock_name][1] = 0
                pln_stocks_2024[stock_name] = [pln_stocks_2024[stock_name][0] - stock_quantity,
                                               pln_stocks_2024[stock_name][1] + (stock_price * usd_value)]
            elif transaction_type == "BUY - MARKET" and transaction_date[:4] == '2023':
                pln_stocks_2023[stock_name] = [pln_stocks_2023[stock_name][0] + stock_quantity,
                                               pln_stocks_2023[stock_name][1] - (stock_price * usd_value)]
            elif transaction_type == "BUY - MARKET" and transaction_date[:4] == '2024':
                pln_stocks_2024[stock_name] = [pln_stocks_2024[stock_name][0] + stock_quantity,
                                               pln_stocks_2024[stock_name][1] - (stock_price * usd_value)]
            if transaction_type == "DIVIDEND" and transaction_date[:4] == '2023':
                pln_2023 = pln_2023 + (stock_price * usd_value)
            elif transaction_type == "DIVIDEND" and transaction_date[:4] == '2024':
                pln_2024 = pln_2024 + (stock_price * usd_value)
            break
        if filtered_row.empty:
            adjust_date(transaction_date_ymd)


def main_function(t_date):
    exchange_rate_year(t_date)
    creating_stock_indexes()
    converting_to_pln(t_date)


stock_transactions = pd.read_excel('revolut.xlsx')
stock_transactions = stock_transactions.dropna(subset=["Ticker"])


for index, row in stock_transactions.iterrows():
    stock_name = row["Ticker"]
    stock_quantity = row["Quantity"]
    transaction_type = row["Type"]
    stock_price = row["Total Amount"]
    transaction_date = row["Date"]
    main_function(transaction_date)

for every_element in pln_stocks_2023:
    pln_2023 += pln_stocks_2023[every_element][1]

for every_element in pln_stocks_2024:
    pln_2024 += pln_stocks_2024[every_element][1]

print(pln_2023)
print(pln_2024)

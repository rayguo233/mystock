import sys
from datetime import datetime
import pandas as pd
from django.contrib.auth.models import User
from decimal import Decimal
import pytz
from portfolio.models import Holding, Transaction, DepositAndWithdrawal


def get_start_n_end(lines: list[str], start_str: str) -> tuple[int, int]:
    first_line_num = None
    for i, line in enumerate(lines, start=1):
        if first_line_num and not line.startswith(start_str):
            return first_line_num, i - 1
        if not first_line_num and line.startswith(start_str):
            first_line_num = i
    return first_line_num, len(lines)

def process_stock_trade_csv(raw_file_name: str):
    read_csv_file = open(f'{raw_file_name}.csv')
    lines = read_csv_file.readlines()
    read_csv_file.close()
    write_csv_file = open(f'{raw_file_name}_processed_trade_data.csv', "w")
    for line in lines:
        if line.startswith('Trades,Header') or line.startswith('Trades,Data'):
            write_csv_file.write(line)
    write_csv_file.close()


def import_trade_data(csv):
    process_stock_trade_csv(csv)
    df = pd.read_csv(f'{csv}_processed_trade_data.csv')
    df = df.loc[df['Header']=='Data']
    user = User.objects.get(pk=1)
    for index, row in df.iterrows():
        dt = datetime.strptime(row['Date/Time'], '%Y-%m-%d, %H:%M:%S')
        dt = pytz.timezone('America/New_York').localize(dt)
        t, created = Transaction.objects.get_or_create(
            user=user, 
            ticker=row['Symbol'],
            num_shares=int(row['Quantity']),
            currency=row['Currency'], 
            total_cost=round(- Decimal(row['Proceeds']) - Decimal(row['Comm/Fee']), 6),  # round to 6 digits after decimal point
            transaction_fee=round(- Decimal(row['Comm/Fee']), 6),
            transaction_time=dt)
        if created:
            holding = Holding.objects.get_or_create(user=user, ticker=t.ticker, 
                defaults={'num_shares': 0, 'total_cost': 0})[0]
            holding.num_shares += t.num_shares
            holding.total_cost += t.total_cost
            holding.save()
        print(t.__dict__)

def process_deposit_withdraw_csv(raw_file_name: str):
    read_csv_file = open(f'{raw_file_name}.csv')
    lines = read_csv_file.readlines()
    read_csv_file.close()
    write_csv_file = open(f'{raw_file_name}_processed_deposit_withdraw.csv', "w")
    for line in lines:
        if line.startswith('Deposits & Withdrawals,Header') or line.startswith('Deposits & Withdrawals,Data,USD'):
            write_csv_file.write(line)
    write_csv_file.close()


def import_deposit_withdraw_data(csv):
    process_deposit_withdraw_csv(csv)
    df = pd.read_csv(f'{csv}_processed_deposit_withdraw.csv')
    df = df.loc[df['Header']=='Data']
    user = User.objects.get(pk=1)
    for index, row in df.iterrows():
        dt = datetime.strptime(row['Settle Date'], '%Y-%m-%d')
        dt = pytz.timezone('America/New_York').localize(dt)
        DepositAndWithdrawal.objects.create(
            user=user, 
            amount=int(row['Amount']),
            currency=row['Currency'], 
            transaction_fee=0,
            transaction_time=dt)

FILE_NAME = "raw_data/ikbr_20201201_20210923"

# import_trade_data(FILE_NAME)
import_deposit_withdraw_data(FILE_NAME)

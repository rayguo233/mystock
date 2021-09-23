import sys
from datetime import datetime
import pandas as pd
from django.contrib.auth.models import User
from decimal import Decimal
import pytz
from portfolio.models import Transaction


def get_start_n_end(lines: list[str], start_str: str) -> tuple[int, int]:
    first_line_num = None
    for i, line in enumerate(lines, start=1):
        if first_line_num and not line.startswith(start_str):
            return first_line_num, i - 1
        if not first_line_num and line.startswith(start_str):
            first_line_num = i
    return first_line_num, len(lines)

FILE_PATH = "raw_data/ikbr_20201201_20210920.csv"

csv_file = open(FILE_PATH)
lines = csv_file.readlines()
csv_file.close()
start, end = get_start_n_end(lines, "Trades,")
print(start, end)
df = pd.read_csv(FILE_PATH, skiprows=start - 1, nrows=end - start)
df = df.loc[df['Header']=='Data']
user = User.objects.get(pk=1)
for index, row in df.iterrows():
    dt = datetime.strptime(row['Date/Time'], '%Y-%m-%d, %H:%M:%S')
    dt = dt.replace(tzinfo=pytz.timezone('America/New_York'))
    Transaction.objects.get_or_create(
        user=user, ticker=row['Symbol'],
        num_shares=int(row['Quantity']),
        currency=row['Currency'], 
        total_cost= - Decimal(row['Proceeds']) - Decimal(row['Comm/Fee']),
        transaction_fee= - Decimal(row['Comm/Fee']),
        transaction_time=dt)
    break
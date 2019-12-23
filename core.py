import random
import pandas as pd
from datetime import datetime as dt
import datetime
import dateutil.parser

class LineItems(object):

    def __init__(self, transactions):
        assert isinstance(transactions,pd.DataFrame)
        self.transactions=transactions
        self.sum_transactions=self.transactions['Betrag'].sum()


    def get_line_items_940(self):
        df=self.transactions
        self.transaction_list=[]
        for index, row in df.iterrows():
            gvc=str(row['GVC'])
            if len(gvc)==2:
                gvc='0'+gvc
            elif len(gvc)==1:
                gvc='00'+gvc

            amount=row['Betrag']
            swift_code=row['Swift Code']
            ref=row['Referenz']
            value_date=row['Valutadatum'].strftime('%y%m%d')
            entry_date = row['Valutadatum'].strftime('%m%d')
            text=row['Buchungstext']
            if amount >=0:
                booking_symbol = "C"
            else:
                booking_symbol = "D"
            amount=abs(amount)
            amount=f"{amount:.2f}".replace('.',',')
            income_line = f''':61:{value_date}{entry_date}{booking_symbol}{amount}{swift_code}{ref}\n'''
            purpose_line = f":86:{gvc}?00{text}\n"
            self.transaction_list.append(income_line)
            self.transaction_list.append(purpose_line)

        self.line_item_text=''.join(self.transaction_list)
        return self


    def get_line_items_942(self):
        df = self.transactions
        self.transaction_list = []
        for index, row in df.iterrows():
            amount=row['Betrag']
            value_date = row['Valutadatum'].strftime('%y%m%d')
            transaction_type="NTRF" #TODO: make it dynamic, if intended to be user input; MAX 4 letters

            if amount >=0:
                booking_symbol = "EC"
            else:
                booking_symbol = "ED"
            amount=abs(amount)
            amount = f"{amount:.2f}".replace('.', ',')
            desc=f"{index+1:0{4}}TRANSFER"
            income_line = f''':61:{value_date}{booking_symbol}{amount}{transaction_type}\n'''
            purpose_line = f":86:{desc}\n"
            self.transaction_list.append(income_line)
            self.transaction_list.append(purpose_line)

        self.line_item_text = ''.join(self.transaction_list)
        return self


class Account(object):

    def __init__(self,bank_code,account_number):
        self.bank_code = str(bank_code)
        self.account_number = str(account_number)
        self.account_text = f":25:{self.bank_code}/{self.account_number}\n"
        '''if len(self.bank_code)>8:
            raise Exception("Bank Code may only be 8 digits long")
        if len(self.account_number)>23:
            raise Exception("Account number may only be 23 digits long")'''



class Balance(object):

    def __init__(self,opening_balance,line_items,opening_date,currency):

        assert isinstance(line_items,LineItems)

        self.opening_balance = opening_balance
        self.currency = str(currency)
        self.line_items = line_items
        self.delta = line_items.sum_transactions
        self.ending_date = None
        if isinstance(opening_date,datetime.date):
            self.opening_date = opening_date
        else:
            self.opening_date = dateutil.parser.parse(opening_date)




    def get_balance(self):


        self.opening_date = dt.strftime(self.opening_date, '%y%m%d')
        self.ending_balance = self.opening_balance + self.delta


        if self.opening_balance >= 0:
            self.booking_symbol_op = "C"
        else:
            self.booking_symbol_op = "D"

        if self.ending_balance >= 0:
            self.booking_symbol_end = "C"
        else:
            self.booking_symbol_end = "D"

        self.opening_balance_text = f":60F:{self.booking_symbol_op}{self.opening_date}{self.currency}" \
            f"{abs(self.opening_balance):.2f}\n".replace('.', ',')

        self.ending_date=self.line_items.transactions['Valutadatum'].max().strftime('%y%m%d')
        self.ending_balance_text = f":62F:{self.booking_symbol_end}{self.ending_date}{self.currency}" \
            f"{abs(self.ending_balance):.2f}\n".replace('.', ',')

        return self


class Statement(Account,LineItems,Balance):

    def __init__(self, bank_code,acc_no,opening_date=None,opening_balance=None,order_ref=None,\
                 currency=None,order_no=None):

        self.id = None
        self.statement_text = None

        self.currency = currency
        self.opening_date = opening_date
        self.opening_balance = opening_balance

        if order_ref is None:
            self.order_ref=f":20:{str(random.randint(1,100))}\n"
        else:
            self.order_ref=f":20:{order_ref}\n"

        if order_no is None:
            self.order_no = ":28C:1/1\n"
        else:
            self.order_no = f":28C:{order_no}\n"

        timestamp = dt.now().strftime('%y%m%d%H%M')
        timestamp = ":13D:"+ timestamp + "+0100\n"
        floor_indicator = ":34F:EUR0,\n"

        self.timestamp = timestamp
        self.floor_indicator = floor_indicator
        self.account = Account(bank_code = bank_code,account_number = acc_no)


    def generate_mt942(self):

        transactions = pd.read_excel('transactions/GUI_short.xlsx', "MT942")
        lineitems = LineItems(transactions).get_line_items_942()
        self.line_items = lineitems
        self.id = "MT942"

        exporter = []

        exporter.append(self.order_ref)
        exporter.append(self.account.account_text)
        exporter.append(self.order_no)
        exporter.append(self.floor_indicator)
        exporter.append(self.timestamp)
        for line_item in self.line_items.transaction_list:
            exporter.append(line_item)

        self.statement_text = ''.join(exporter)

    def generate_mt940(self):

        # check if balance info was instantiated
        if self.opening_date is None or self.opening_balance is None or self.currency is None:
            raise ValueError("You have not provided opening date or opening balance or currency.")

        transactions = pd.read_excel('transactions/GUI_short.xlsx', "MT940")
        lineitems = LineItems(transactions).get_line_items_940()
        balance = Balance(line_items=lineitems, opening_balance=self.opening_balance, opening_date=self.opening_date,
                          currency=self.currency)
        balance.get_balance()

        self.balance = balance
        self.line_items = lineitems
        self.id = "MT940"

        exporter = []

        exporter.append(self.order_ref)
        exporter.append(self.account.account_text)
        exporter.append(self.order_no)
        exporter.append(self.balance.opening_balance_text)
        for line_item in self.line_items.transaction_list:
            exporter.append(line_item)
        exporter.append(self.balance.ending_balance_text)

        self.statement_text = ''.join(exporter)

    def generate_file(self):

        if self.id is not None:
            content = self.statement_text
            time_tag = dt.now().strftime('%y%m%d%H%M')
            filename = f"output/{self.id} - {time_tag}.sta"
            with open(filename, 'w') as f:
                    f.write(content)


        else:
            raise ValueError("No statements were generated. Please do so before exporting to file.")














import core

#Config
order_ref='VG122019'
bank_code='10040000'
account_no='10000001'
opening_balance=0
opening_date='13.12.2019'
currency='EUR'


if __name__ == "__main__":
    unit = core.Statement(bank_code=bank_code, acc_no=account_no, opening_date=opening_date,
                          opening_balance=opening_balance,
                          currency=currency)

    unit.generate_mt942()

    unit.generate_file()



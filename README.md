# BS-Generator
*Python script for bank statement generation*

## Description
This is a shallow script to quickly create dummy bank statements. Currently the following standards are implemented:
* SWIFT MT940 (only obligatory fields)
* SWIFT MT942 (only obligatory fields)

I figured it be easiest / user-friendliest if transactions are stored in an external excel sheet as opposed to an csv or other dataformat. See **Installation** for more details.

## Installation
1. Clone or manually download git repo
2. Run `main.py`for testing

Transation data is sourced from `transaction/transactions.xlsx`. So make sure you enter your intended data there. The spreadsheet has a tab for every format. 

The general workflow is as follows:
1. instantiate a `Statement` Object
example:
```python 
   unit = core.Statement(bank_code=bank_code, acc_no=account_no, opening_date=opening_date,
                          opening_balance=opening_balance,
                          currency=currency)
```
2. from there you can create multiple statements depending on the information provided in step 1) by using the `generate_*` methods
example:
```python
    unit.generate_mt942()
```
3. create a text-file to be used
example:

```python
    unit.generate_file()
```

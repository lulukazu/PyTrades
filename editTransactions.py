from datetime import *
from pathlib import Path
import pandas as pd
import numpy as np


transactionsFileName = 'data.csv'
fileInPath = Path(transactionsFileName)


def deleteTransaction(row):
    if fileInPath.exists():
        transactionsList = pd.read_csv('data.csv', sep='\t')
    else:
        print("Nothing to delete!")
        return

    transactionsList = transactionsList.drop(row)
    # transactionsList.index = range(len(transactionsList.index))
    transactionsList.to_csv('data.csv', sep='\t', index=False)


def addNewTransaction():
    todayDate = date.today
    columnNames = ['Type', 'Date', 'Stock Symbol', 'Quantity', 'Price', 'Total Amount']
    if fileInPath.exists():
        transactionsList = pd.read_csv('data.csv', sep='\t')
    else:
        transactionsList = pd.DataFrame(columns=columnNames)

    typeInput = input("Transaction type (buy/sell):")
    dateInput = input("Date (YYYY-MM-DD):")
    stockInput = input("Stock name:")
    quantInput = int(input("Quantity:"))
    priceInput = float(input("Unit price:"))
    calcCost = np.round(priceInput * quantInput, 2)

    if not dateInput:
        dateInput = todayDate

    transactionsList.loc[transactionsList.shape[0]] = [dateInput, typeInput, stockInput, quantInput, priceInput,
                                                       calcCost]

    print(transactionsList)
    transactionsList.to_csv('data.csv', sep='\t', index=False)


def addNewTransactionNoPrompt(typeInput, dateInput, stockInput, quantInput, priceInput):
    todayDate = date.today
    columnNames = ['Date', 'Type', 'Stock Symbol', 'Quantity', 'Price', 'Total Amount']
    if fileInPath.exists():
        transactionsList = pd.read_csv('data.csv', sep='\t')
    else:
        transactionsList = pd.DataFrame(columns=columnNames)
    quantInput = int(quantInput)
    priceInput = float(priceInput)
    calcCost = np.round(priceInput * quantInput, 2)

    if not dateInput:
        dateInput = todayDate

    indexNew = transactionsList.shape[0]
    transactionsList.loc[indexNew] = [dateInput, typeInput, stockInput, quantInput, priceInput,
                                      calcCost]
    transactionsList.to_csv('data.csv', sep='\t', index=False)

    return indexNew


def viewTransactions():
    if fileInPath.exists():
        transactionsList = pd.read_csv('data.csv', sep='\t')
    else:
        print("Nothing to see!")
    return transactionsList


def editListElement(row, column, newVal):
    if fileInPath.exists():
        transactionsList = pd.read_csv('data.csv', sep='\t')
    else:
        print("Nothing to edit!")
    transactionsList.loc[row, column] = newVal

    transactionsList.loc[row, 'Total Amount'] = transactionsList.loc[row, 'Price'] * transactionsList.loc[row, 'Quantity']

    transactionsList['Total Amount'] = np.round(transactionsList['Total Amount'], 2)
    print(transactionsList)
    transactionsList.to_csv('data.csv', sep='\t', index=False)


# viewTransactions()
# addNewTransaction()
# editListElement(42, 'Type', 'sell')
# deleteTransaction(43)
# deleteTransaction(43)
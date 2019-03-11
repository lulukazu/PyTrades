from pattern.web import download
import pandas as pd
from io import StringIO
from datetime import *
import numpy as np

pd.options.mode.chained_assignment = None


def downloadOne(stockName):
    URLstring = "http://financials.morningstar.com/ajax/exportKR2CSV.html?t=" + stockName
    try:
        dataString = download(URLstring, unicode=True)

        dataObj = StringIO(dataString)
        dataDF = pd.read_csv(dataObj, header=2, index_col=0, thousands=',')
        dataDFTranspose = dataDF.transpose()
        dataFrame = dataDFTranspose[['Revenue USD Mil', 'Earnings Per Share USD', 'Book Value Per Share * USD',
                                     'Dividends USD', 'Shares Mil']]
        dataFrame.rename(columns={'Revenue USD Mil': 'Revenue (Mil)', 'Earnings Per Share USD': 'Earnings Per Share',
                                  'Book Value Per Share * USD': 'Book Value Per Share', 'Shares Mil': 'Shares (Mil)'}, inplace=True)
        dataFrame.index.name = 'Date'
        dataFrame['Revenue (Mil)'] = dataFrame['Revenue (Mil)'].str.replace(',', '')
        dataFrame['Shares (Mil)'] = dataFrame['Shares (Mil)'].str.replace(',', '')

        today = date.today()
        stringToday = today.strftime('%Y-%m')
        dataFrame.index = dataFrame.index.str.replace('TTM', stringToday)

    except:
        print("No Data")
        dataFrame = []

    return dataFrame


def drawFutureTrend(dataFrame, alpha, beta, gamma):
    dataFrame = dataFrame.apply(pd.to_numeric)
    # skip today!
    dataFrame.fillna(0, inplace=True)
    lastYearData = dataFrame.tail(2)
    lastTwoYearsData = dataFrame.tail(3)
    book2years = lastTwoYearsData['Book Value Per Share']
    dBook = book2years.iloc[1]-book2years.iloc[0]
    t = np.array(range(-9, 4, 1))
    Earn0 = lastYearData['Earnings Per Share'].iloc[0]
    Div0 = lastYearData['Dividends USD'].iloc[0]
    Book0 = lastYearData['Book Value Per Share'].iloc[0]

    # waste0 = max(Earn0-Div0-dBook, 0)
    Earn_t = alpha*t + Earn0
    Div_t = beta*t + Div0
    # Eta_t = gamma*t + waste0
    Eta_t = gamma*np.ones(t.size)
    diffBook = Earn_t - Div_t - Eta_t
    Book_t = np.cumsum(diffBook)
    indToday = np.where(t == 0)[0]

    Book_t_norm = Book_t - (Book_t[indToday] - Book0)

    lastDate = lastYearData.iloc[0].name
    today = pd.to_datetime(lastDate, format='%Y-%m')

    if today.month < 6:
        freqString = '1YS'
        endDateRange = today + pd.DateOffset(years=3)
    else:
        freqString = '1Y'
        endDateRange = today + pd.DateOffset(years=4)

    print(dataFrame.index)
    startDateRange = today - pd.DateOffset(years=9)

    dateRange = pd.date_range(start=startDateRange, end=endDateRange, freq=freqString)
    print(dateRange)

    # stringToday = today.strftime('%Y-%m')

    dataOutput = {'Earnings(t)': Earn_t.tolist(), 'Dividends(t)': Div_t.tolist(), 'Book(t)': Book_t_norm.tolist()}
    dataFrameOut = pd.DataFrame(data=dataOutput, index=dateRange)

    dataFrameOut.index.name = 'Date'
    print(dataFrameOut)
    return dataFrameOut

# df = downloadOne('GOOG')
# drawFutureTrend(df, 1, 0, 0)
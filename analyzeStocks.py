import numpy as np
from datetime import *
from pathlib import Path
import pandas as pd
import importlib

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', None)
transactionsFileName = 'data.csv'
lookupTableFilename = 'pricesLookup.csv'


def reloadTransactions():
    global transactionsList
    fileInPath = Path(transactionsFileName)
    if fileInPath.exists():
        transactionsList = pd.read_csv('data.csv', sep='\t')
        startUp()
    else:
        print("Nothing here!")


def getStocksList(dataFrame):
    stockNames = dataFrame['Stock Symbol'].unique()
    stockNames.sort()
    return stockNames


def lookupPriceRange(tickerSymbolList, startDate, endDate):
    import fix_yahoo_finance
    fix_yahoo_finance = importlib.reload(fix_yahoo_finance)
    print(tickerSymbolList)
    try:
        data = fix_yahoo_finance.download(tickerSymbolList, start=startDate, end=endDate, as_panel=True)
        dataClose = data["Close"]
        print('DATA LOADED')
    except ValueError:
        print("Did not succesfully load data")
        dataClose = []

    return dataClose  # in form of dataframe


def startUp():
    transactionsPath = Path(transactionsFileName)
    lookupTablePath = Path(lookupTableFilename)
    if transactionsPath.exists():
        transactionsListLocal = pd.read_csv(transactionsFileName, sep='\t')
        globalStocksList = getStocksList(transactionsListLocal).tolist()
        todayDate = date.today()
        fiveYearsAgo = todayDate - timedelta(days=5 * 365)
        if len(globalStocksList) == 0:
            print('It is empty!')
            firstDate = fiveYearsAgo
            # this is just to put a default date
        else:
            firstDateTransactions = pd.to_datetime(transactionsListLocal['Date']).min()
            firstDate = min([firstDateTransactions.date(), fiveYearsAgo])

        firstDateStr = firstDate.strftime('%Y-%m-%d')

        todayStr = todayDate.strftime('%Y-%m-%d')
        # check if file already exists, and if so, if file spans the date range that is required

        if lookupTablePath.exists():
            globalLookupDFCurrent = pd.read_csv(lookupTableFilename, sep='\t', index_col=0)
            globalLookupDFCurrent.index = pd.to_datetime(globalLookupDFCurrent.index)
            globalLookupDFLocal = lookupOnlyDifference(globalLookupDFCurrent, globalStocksList, firstDate, todayDate)
        else:
            globalLookupDFLocal = lookupPriceRange(globalStocksList, firstDateStr, todayStr)
            if len(globalStocksList) == 1:
                series1 = globalLookupDFLocal
                df = pd.DataFrame(index=series1.index, columns=[globalStocksList[0]], data=series1.values)
                globalLookupDFLocal = df

            updateLookupTable(lookupTableFilename, globalLookupDFLocal)

        global globalLookupDF, transactionsList
        transactionsList = transactionsListLocal
        globalLookupDF = globalLookupDFLocal
    else:
        print("Nothing here!")


def updateLookupTable(path, newDF):
    global globalLookupDF
    globalLookupDF = newDF
    newDF.to_csv(path, sep='\t')


def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4:  # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate


def lookupOnlyDifference(storedDF, stocksListRequested, firstDateObj, lastDateObj):
    if isinstance(stocksListRequested, list):
        stocksListRequested = stocksListRequested
    else:
        stocksListRequested = [stocksListRequested]

    lastWeekday = prev_weekday(lastDateObj)
    dateListObj = pd.to_datetime(storedDF.index)
    minDateObj = dateListObj.min().date()
    minDateObjMinus1 = minDateObj - timedelta(days=1)
    maxDateObj = dateListObj.max().date()
    maxDateObjPlus1 = maxDateObj + timedelta(days=1)
    currentFirstDateStr = minDateObj.strftime('%Y-%m-%d')
    currentLastDateStr = maxDateObj.strftime('%Y-%m-%d')
    currentFirstDateMinus1Str = minDateObjMinus1.strftime('%Y-%m-%d')
    currentLastDatePlus1Str = maxDateObjPlus1.strftime('%Y-%m-%d')
    firstDateStr = firstDateObj.strftime('%Y-%m-%d')
    lastDateStr = lastWeekday.strftime('%Y-%m-%d')
    currentStocksList = storedDF.columns.values.tolist()
    if firstDateObj >= minDateObj and lastWeekday <= maxDateObj and set(stocksListRequested).issubset(currentStocksList):
        outputDFLocal = storedDF
    else:
        storedDFOriginal = storedDF
        # lookup only the new stocks with original dates
        if not set(stocksListRequested).issubset(currentStocksList):
            diffStocksList = list(set(stocksListRequested) - set(currentStocksList))
            lengthNewStocks = len(diffStocksList)
            newStocksDF = lookupPriceRange(diffStocksList, currentFirstDateStr, currentLastDateStr)
            if lengthNewStocks == 1:
                newStocksDF.name = diffStocksList[0]

            if newStocksDF != []:
                storedDFOriginal = pd.concat([storedDFOriginal, newStocksDF], axis=1, join_axes=[storedDFOriginal.index])

        # now lookup new date ranges
        updatedStocksList = storedDFOriginal.columns.values.tolist()
        if firstDateObj < minDateObj:
            newDatesDF1 = lookupPriceRange(updatedStocksList, firstDateStr, currentFirstDateMinus1Str)
            if newDatesDF1 != []:
                storedDFOriginal = pd.concat([storedDFOriginal, newDatesDF1], axis=0, join='outer', sort=True)
                storedDFOriginal.sort_index(axis=0, inplace=True)
                storedDFOriginal = storedDFOriginal[~storedDFOriginal.index.duplicated(keep='first')]
        if lastWeekday > maxDateObj:
            newDatesDF2 = lookupPriceRange(updatedStocksList, currentLastDatePlus1Str, lastDateStr)
            if newDatesDF2 != []:
                storedDFOriginal = pd.concat([storedDFOriginal, newDatesDF2], axis=0, join='outer', sort=True)
                storedDFOriginal.sort_index(axis=0, inplace=True)
                storedDFOriginal = storedDFOriginal[~storedDFOriginal.index.duplicated(keep='first')]
        outputDFLocal = storedDFOriginal
        # numNulls = outputDFLocal.isnull().sum().sum()
        # print(numNulls)
        updateLookupTable(lookupTableFilename, outputDFLocal)
    return outputDFLocal





def lookupPriceFromTableOnly(tickerSymbolList, startDate, endDate):
    startDate = pd.to_datetime(startDate)
    endDate = pd.to_datetime(endDate)
    df1 = globalLookupDF[tickerSymbolList]
    df = df1[(df1.index >= startDate) & (df1.index <= endDate)]
    df_nonan = df.dropna()

    return df_nonan


def lookupPriceFromTable(tickerSymbolList, startDate, endDate):

    # this is distinguished currently from the script lookupOnlyDifference because that script updates the data base each search and I'm not sure that's what we want here
    startDate = pd.to_datetime(startDate).date()
    endDate = pd.to_datetime(endDate).date()

    wholeDF = lookupOnlyDifference(globalLookupDF, tickerSymbolList, startDate, endDate)
    df1 = wholeDF[tickerSymbolList]
    df = df1[(df1.index.date >= startDate) & (df1.index.date <= endDate)]
    df_nonan = df.dropna()
    return df_nonan


def currentPrices(tickerSymbolList, thisDay):
    # today = date.today()
    aWeekAgo = pd.to_datetime(thisDay) - timedelta(days=4)
    oneWeekData = lookupPriceFromTableOnly(tickerSymbolList, aWeekAgo, thisDay)
    # print(oneWeekData)
    # print(thisDay)
    lastData = oneWeekData.iloc[-1]
    return lastData


def filterTransactions(startDate, endDate):
    startDate = pd.to_datetime(startDate)
    endDate = pd.to_datetime(endDate)
    transactionsList['Date'] = pd.to_datetime(transactionsList['Date'])
    filteredTransactions = transactionsList.loc[
        (startDate <= transactionsList['Date']) & (transactionsList['Date'] <= endDate)]
    return filteredTransactions


def getAllTransactions(stockName, dataFrame):
    selectedRows = dataFrame.loc[dataFrame['Stock Symbol'] == stockName]
    # selectedRows = selectedRows.set_index('Date')
    selectedRows['Date'] = pd.to_datetime(selectedRows['Date'])
    buyRows = selectedRows.loc[selectedRows['Type'] == 'buy']
    sellRows = selectedRows.loc[selectedRows['Type'] == 'sell']
    return {'sell': sellRows, 'buy': buyRows}


def getQuantityBought(stocksNameList, dataFrame):
    stockHoldings = []
    for stock in stocksNameList:
        transLines = getAllTransactions(stock, dataFrame)
        buyRows = transLines['buy']
        totalShares = buyRows['Quantity'].sum()
        stockHoldings.append(totalShares)
    return stockHoldings


def getQuantitySold(stocksNameList, dataFrame):
    stockHoldings = []
    for stock in stocksNameList:
        transLines = getAllTransactions(stock, dataFrame)
        sellRows = transLines['sell']
        totalShares = sellRows['Quantity'].sum()
        stockHoldings.append(totalShares)
    return stockHoldings


def getCurrentQuantities(stocksNameList, dataFrame):
    stockHoldings = np.array(getQuantityBought(stocksNameList, dataFrame)) - np.array(
        getQuantitySold(stocksNameList, dataFrame))
    return stockHoldings


def getAmountSpent(stocksNameList, dataFrame):
    stockCost = []
    for stock in stocksNameList:
        transLines = getAllTransactions(stock, dataFrame)
        buyRows = transLines['buy']
        totalAmount = buyRows['Total Amount'].sum()
        stockCost.append(totalAmount)
    stockCost = np.array(stockCost)
    return stockCost


def getAmountEarned(stocksNameList, dataFrame):
    stockEarnings = []
    for stock in stocksNameList:
        transLines = getAllTransactions(stock, dataFrame)
        sellRows = transLines['sell']
        totalAmount = sellRows['Total Amount'].sum()
        stockEarnings.append(totalAmount)
    stockEarnings = np.array(stockEarnings)
    return stockEarnings


def getCurrentValue(stocksNameList, stockHoldings, thisDay):
    stocksNameList = stocksNameList.tolist()
    pricesToday = currentPrices(stocksNameList, thisDay)
    valueList = stockHoldings * pricesToday
    return valueList


# ------------------------------------------------------------------
# Overview Scripts


def makeSummaryDF(thisDay):

    # print(thisDay)
    transactions = filterTransactions('2000-01-01', thisDay)
    names = getStocksList(transactions)
    quantities = getCurrentQuantities(names, transactions)
    spentOnly = np.round(getAmountSpent(names, transactions), 2)
    earnedOnly = np.round(getAmountEarned(names, transactions), 2)
    boughtQuant = getQuantityBought(names, transactions)
    soldQuant = getQuantitySold(names, transactions)
    pricesToday = currentPrices(names, thisDay)

    avgBuyPrice = spentOnly / boughtQuant

    currentVal = np.round(getCurrentValue(names, quantities, thisDay), 2)
    spentOnPosition = avgBuyPrice * quantities
    gainLossCumulative = np.round(currentVal - spentOnly + earnedOnly, 2)
    gainLossPercent = np.round((currentVal - spentOnPosition) / spentOnPosition * 100, 1)

    df = pd.DataFrame(columns=['Stock Symbol', 'Quantity', 'Current Price', 'Current Value', 'Current Gain/Loss %',
                               'Cumulative Gain/Loss $'],
                      index=currentVal.index.values)
    df['Stock Symbol'] = names
    df['Quantity'] = quantities
    # df['Cost'] = np.round(avgBuyPrice*quantities,2)
    df['Current Price'] = np.round(pricesToday, 2)
    df['Current Value'] = currentVal
    df['Current Gain/Loss %'] = gainLossPercent
    df['Cumulative Gain/Loss $'] = gainLossCumulative
    return df


def calcTotalGainLoss(df):
    totalGainLoss = np.round(df['Cumulative Gain/Loss $'].sum(), 2)
    return totalGainLoss


def getBuySellPoints(stock, typeBS, df):
    transLines = getAllTransactions(stock, df)
    buySellRows = transLines[typeBS]
    return buySellRows

#
# def analyzePeriod(stock, startDate, endDate):
#     dataFrame = lookupPriceFromTable(stock, startDate, endDate)
#     filteredDF = filterTransactions(startDate, endDate)
#
#     buyPoints = getBuySellPoints(stock, 'buy', filteredDF)
#     sellPoints = getBuySellPoints(stock, 'sell', filteredDF)
#
#     # Moving averages (10, 50, 200)
#     SMA20 = nDayMovingAverage(dataFrame, 20)
#     SMA50 = nDayMovingAverage(dataFrame, 50)
#     SMA200 = nDayMovingAverage(dataFrame, 200)
#
#     # 50-day RMS
#
#     RMS20 = nDayMovingStd(dataFrame, 20)
#
#     # fig, ax = plt.subplots()
#     ax = plt
#     ax.plot(dataFrame)
#     ax.fill_between(dataFrame.index, SMA20 - 2 * RMS20, SMA20 + 2 * RMS20,
#                     alpha=0.2, facecolor='#089FFF', antialiased=True, label='20-day moving RMS')
#
#     if dataFrame.size > 20:
#         ax.plot(SMA20, '--', linewidth=1, label='20-day SMA')
#     if dataFrame.size > 50:
#         ax.plot(SMA50, '--', linewidth=1, label='50-day SMA')
#     if dataFrame.size > 200:
#         ax.plot(SMA200, '--', linewidth=1, label='200-day SMA')
#
#     ax.legend()
#
#     plot1 = ax.plot(sellPoints['Date'], sellPoints['Price'], 'rv')
#     plot2 = ax.plot(buyPoints['Date'], buyPoints['Price'], 'g^')
#     for i, txt in enumerate(sellPoints['Quantity']):
#         # ax.annotate(str(txt), (mdates.date2num(sellPoints['Date'].iloc[i]), sellPoints['Price'].iloc[i]*.96))
#         ax.annotate(str(txt), (mdates.date2num(sellPoints['Date'].iloc[i]), sellPoints['Price'].iloc[i]),
#                     textcoords='offset points', xytext=(-8, -15))
#     for i, txt in enumerate(buyPoints['Quantity']):
#         # ax.annotate(str(txt), (mdates.date2num(buyPoints['Date'].iloc[i]), buyPoints['Price'].iloc[i]*.96))
#         ax.annotate(str(txt), (mdates.date2num(buyPoints['Date'].iloc[i]), buyPoints['Price'].iloc[i]),
#                     textcoords='offset points', xytext=(-8, -15))
#     plt.setp(plot1, markersize=10)
#     plt.setp(plot2, markersize=10)
#
#     titleStr = stock + ' Trades ( ' + startDate + ' to ' + endDate + ' )'
#     plt.title(titleStr)
#     plt.xlabel('Date')
#     plt.ylabel('Share Price')
#     plt.grid(True)
#     # plt.show()


def nDayMovingAverage(series, n):
    if series.size > n:
        simpleMovingAvg = series.rolling(window=n, center=False).mean()
        simpleMovingAvg = simpleMovingAvg[~np.isnan(simpleMovingAvg)]
    else:
        print('Series too short!')
        simpleMovingAvg = series
    return simpleMovingAvg


def calcTrailingStopSegment(series, percent, startDate):
    startDate = pd.to_datetime(startDate)
    seriesFiltered = series.loc[series.index > startDate]
    stopSeries = (1 - percent / 100) * seriesFiltered
    stopLine = []
    maxVal = 0
    for i, elem in enumerate(stopSeries):
        if elem >= maxVal:
            maxVal = elem
            stopLine.append(maxVal)
        else:
            stopLine.append(maxVal)
        if maxVal >= seriesFiltered[i]:
            break
    nElements = len(stopLine)
    stopLineSeries = pd.Series(data=stopLine, index=stopSeries.index[:nElements], name=stopSeries.name)
    # stopLineTruncated = stopLineSeries[stopLineSeries <= seriesFiltered]
    return stopLineSeries


def calcTrailingStop(series, percent, startDate):
    startDateOverall = pd.to_datetime(startDate)
    endDateOverall = series.tail(1).index[0]
    stopLineOut = pd.Series(name=series.name)
    startDate = startDateOverall

    while startDate < endDateOverall:
        startDateStr = startDate.strftime('%Y-%m-%d')
        stopLineSegment = calcTrailingStopSegment(series, percent, startDateStr)
        stopLineOut = stopLineOut.append(stopLineSegment)
        startDate = stopLineSegment.tail(1).index[0] + pd.Timedelta(1, unit="d")

    stopLineOut.index.name = 'Date'

    return stopLineOut


# dataSeries = lookupPriceFromTable('GE', '2017-01-01', '2018-02-04')
# calcTrailingStop(dataSeries, 10, '2017-04-01')

# def calcRMS(series, n):
#     if series.size > n:
#         RMS = np.std(series.tail(n))
#     else:
#         print('Not enough data!')
#     return RMS


def nDayMovingStd(series, n):
    if series.size > n:
        simpleMovingStd = series.rolling(window=n, center=False).std()
        simpleMovingStd = simpleMovingStd[~np.isnan(simpleMovingStd)]
    else:
        print('Series too short!')
    return simpleMovingStd


def generateGainLossOverTime(startDate, endDate):
    # stringToday = str(date.today())
    # startDate = '2017-02-01'
    startDateObj = pd.to_datetime(startDate)
    endDateObj = pd.to_datetime(endDate)
    diffDays = pd.Timedelta(endDateObj - startDateObj).days

    nPoints = 50
    frequency = max(round(diffDays / nPoints), 1)
    freqString = str(frequency) + 'D'

    rangeDate = pd.date_range(start=startDate, end=endDate, freq=freqString)
    datesPy = rangeDate.to_pydatetime()

    VTICompare = lookupPriceFromTable('VTI', startDate, endDate)
    gainLoss = []
    totalValue = []
    for i, eachDate in enumerate(datesPy):
        stringDate = eachDate.strftime('%Y-%m-%d')
        dataFrame = makeSummaryDF(stringDate)
        gainLossDay = calcTotalGainLoss(dataFrame)
        totalValueDay = dataFrame['Current Value'].sum()
        totalValue.append(totalValueDay)
        gainLoss.append(gainLossDay)

    meanValue = np.mean(totalValue)
    gainLossPercent = ((gainLoss - gainLoss[0]) / meanValue) * 100
    VTICompare = ((VTICompare - VTICompare[0]) / VTICompare[0]) * 100

    gainLossSeries = pd.Series(data=gainLossPercent, index=rangeDate, name='Gain/Loss')
    gainLossSeries.index.name = 'Date'
    return gainLossSeries, VTICompare

#
# def plotGainLoss(startDate):
#     gainLossSeries, VTICompare = generateGainLossOverTime(startDate)
#     plt.plot(gainLossSeries, label='My Portfolio')
#     plt.plot(VTICompare, label='VTI Index')
#     plt.title('Gain/Loss Since ' + startDate)
#     plt.xlabel('Date')
#     plt.ylabel('Change in Value of Investments (% Mean Investment)')
#     plt.legend()
#     plt.show()

# generateChart('COST', '2017-01-01')
# DF = generateAllCharts('2017-01-01')

#
# stringToday = str(date.today())
# DF = makeSummaryDF(stringToday)
# plotGainLoss('2017-01-01')
# plotTotalHoldings(DF)

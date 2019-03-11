from flask import Flask, render_template, send_from_directory, request, Response
from editTransactions import *
from analyzeStocks import *
import json
from fundamentals import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add-transaction/', methods=['post', 'get'])
def add_transaction():
    buySellFlag = request.form['buySell']  # takes form name
    dateInput = request.form['dateInput']
    stockInput = request.form['stockInput']
    quantityInput = request.form['quantityInput']
    priceInput = request.form['priceInput']
    newIndex = addNewTransactionNoPrompt(buySellFlag, dateInput, stockInput, quantityInput, priceInput)
    reloadTransactions()
    return str(newIndex)


@app.route('/delete-transaction/', methods=['post', 'get'])
def delete_transaction():
    rowIndex = request.form['rowInput']
    rowIndexInt = int(rowIndex)
    deleteTransaction(rowIndexInt)
    reloadTransactions()
    return str(rowIndex)


@app.route('/get-transactions-data/')
def view_transactions():
    transactionsListLocal = viewTransactions()
    csvData = transactionsListLocal.to_csv()
    return csvData


@app.route('/get-overview-table/')
def overview_table():
    stringToday = str(date.today())
    dataFrame = makeSummaryDF(stringToday)
    nonZeroDF = dataFrame.loc[dataFrame['Quantity'] != 0]
    # columnsDF = nonZeroDF.columns
    # noStockDF = dataFrame[columnsDF[1:]]
    csvData = nonZeroDF.to_csv(index=False)
    return csvData


@app.route('/get-all-fundamentals-data/<stockName>')
def get_all_fundamentals(stockName):
    alpha = float(request.args.get('alpha'))
    beta = float(request.args.get('beta'))
    gamma = float(request.args.get('gamma'))

    dataFrame = downloadOne(stockName)
    csvData = dataFrame.to_csv(header=True)
    dataFrameTrends = drawFutureTrend(dataFrame, alpha, beta, gamma)
    csvTrends = dataFrameTrends.to_csv(header=True)

    return Response(json.dumps({'data': csvData,
                                'trends': csvTrends}),
                    mimetype='application/json')


@app.route('/get-all-time-series-data/<stockName>')
def get_all_time_series(stockName):
    startDate = request.args.get('start')
    endDate = request.args.get('end')
    stopPercent = request.args.get('stop')

    dataSeries = lookupPriceFromTable(stockName, startDate, endDate)
    priceData = dataSeries.to_csv(header=True)

    filteredDF = filterTransactions(startDate, endDate)
    buyPoints = getBuySellPoints(stockName, 'buy', filteredDF)
    csvBuy = buyPoints.to_csv(header=True)
    sellPoints = getBuySellPoints(stockName, 'sell', filteredDF)
    csvSell = sellPoints.to_csv(header=True)

    SMA200 = nDayMovingAverage(dataSeries, 200)
    SMA20 = nDayMovingAverage(dataSeries, 20)

    csvSMA200 = SMA200.to_csv(header=True)
    csvSMA20 = SMA20.to_csv(header=True)

    RMS20 = nDayMovingStd(dataSeries, 20)
    csvRMS20 = RMS20.to_csv(header=True)

    stopPercentInt = int(stopPercent)
    TrailingStop15 = calcTrailingStop(dataSeries, stopPercentInt, startDate)
    csvTrailingStop = TrailingStop15.to_csv(header=True)
    return Response(json.dumps({'priceData': priceData, 'buyPoints': csvBuy, 'sellPoints': csvSell, 'SMA20': csvSMA20,
                                'SMA200': csvSMA200, 'RMS20': csvRMS20, 'trailingStop': csvTrailingStop}),
                    mimetype='application/json')


@app.route('/get-gain-loss-data/')
def get_gain_loss():
    startDate = request.args.get('start')
    endDate = request.args.get('end')
    gainLossSeries, VTICompare = generateGainLossOverTime(startDate, endDate)
    csvGainLoss = gainLossSeries.to_csv(header=True)
    csvVTI = VTICompare.to_csv(header=True)

    return Response(json.dumps({'gainLoss': csvGainLoss, 'VTI': csvVTI}),
                    mimetype='application/json')


@app.route('/files/<path:path>')
def send_js(path):
    return send_from_directory('templates', path)


if __name__ == '__main__':
  app.run(debug=False)
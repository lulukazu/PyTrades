# Installation

Built in Python 3.7.2

Install the following modules:
`pip install flask pandas pattern fix_yahoo_finance`

# Use

Run server.py and open your browser to your localhost address

You'll be greeted with the default view.  The default view is an overview of your current stock portfolio, up to the last closing price.  Table shows detailed stock performance, pie chart shows the proportion of positions held relative to full portfolio, and the line graph shows your (active) portfolio's growth relative to the Vanguard Total Index fund (VTI).  The comparison is made assuming that the average amount in your actively invested portfolio is used to buy VTI. 

![](/images/tracktrade-fullscreen.PNG?raw=true "Overview")

Add individual stock transactions using the form on the left.  No need to put them in chronological order.  If the date is left blank today's date will be filled in.

![](/images/tracktrade-add.png?raw=true "Add a Transaction")

All individual transactions will be shown overlaying the stock price in single-stock view.  Below is what single-stock view looks like.  The stock you have chosen to plot will be highlighted in the table if it is in your portfolio.  A fundamentals line chart pulls up some basic financial information about the company from the last 10 years.  Use the corresponding sliding bars above the chart to fit various linear trendlines to perform a very unsophisticated prediction of the future.

![](/images/tracktrade-fullscreen-onestock1.png?raw=true "Single-Stock View")

Individual stock charts need a more detailed explanation.  Plotted is the stock's closing price on every day within the date range set in the upper left corner.  Green triangles represent buy points, red triangles represent sell points.  Hovering these triangles gives you the price and quantity sold.  Green dashed line shows the 20-day simple moving average, with green shading showing the 2-standard-deviation bounds calculated on the same interval.  Dark blue dashed line indicates the 500-day simple moving average, and the solid grey line shows the trailing stop price.  A trailing stop follows the price of a stock when it rises, but stays constant when it falls.  It is helpful for a loss-limiting consistent exit strategy.  You can set the gap in percent also in the top left corner. 

This graph is zoomable by brushing.  Zoom out by double-clicking.

![](/images/tracktrade-stocklinechart.png?raw=true "Stock Line Chart")

Finally, the table in the center can be toggled to show either individual transactions or portfolio overview.  In individual transactions view, you can use the numbered index of each line to remove individual transactions that you have entered in error.

![](/images/tracktrade-toggle.PNG?raw=true "Table")


# Comments

This was a curiosity project for me for the dual purposes of learning python and becoming a more informed investor.  Hope it's some use to other people out there.

# Credits

Using the following JS line chart:
https://bl.ocks.org/michaschwab/bb0cd5c05fa61aa257b1e5c453cbb987

Fix_yahoo_finance package for scraping stock price data from the yahoo finance site.

Financial data downloaded from MorningStar.

__Installation__

Built in Python 3.7.2

Install the following modules:
`pip install flask pandas pattern fix_yahoo_finance`

__Use__

Run server.py and open your browser to your localhost address

You'll be greeted with the default view.  The default view is an overview of your current stock portfolio, up to the last closing price.  Table shows detailed stock performance, pie chart shows the proportion of positions held relative to full portfolio, and the line graph shows your (active) portfolio's growth relative to the Vanguard Total Index fund (VTI).  The comparison is made assuming that the average amount in your actively invested portfolio is used to buy VTI. 

![](/images/tracktrade-fullscreen.PNG?raw=true "Overview")

Add individual stock transactions using the form on the left:

![](/images/tracktrade-add.PNG?raw=true "Add a Transaction")


__Credits__

Using the following JS line chart:
https://bl.ocks.org/michaschwab/bb0cd5c05fa61aa257b1e5c453cbb987

import yfinance as yf

stock = yf.Ticker("XEQT.TO")

# get all stock info
stock.info

# get historical market data
hist = stock.history(period="1mo")

print(hist)

# show meta information about the history (requires history() to be called first)
stock.history_metadata

# show actions (dividends, splits, capital gains)
stock.actions
stock.dividends
stock.splits
stock.capital_gains  # only for mutual funds & etfs

# show share count
stock.get_shares_full(start="2022-01-01", end=None)

# show financials:
stock.calendar
stock.sec_filings
# - income statement
stock.income_stmt
stock.quarterly_income_stmt
# - balance sheet
stock.balance_sheet
stock.quarterly_balance_sheet
# - cash flow statement
stock.cashflow
stock.quarterly_cashflow
# see `Ticker.get_income_stmt()` for more options

# show holders
stock.major_holders
stock.institutional_holders
stock.mutualfund_holders
stock.insider_transactions
stock.insider_purchases
stock.insider_roster_holders

stock.sustainability

# show recommendations
stock.recommendations
stock.recommendations_summary
stock.upgrades_downgrades

# show analysts data
stock.analyst_price_targets
stock.earnings_estimate
stock.revenue_estimate
stock.earnings_history
stock.eps_trend
stock.eps_revisions
stock.growth_estimates

# Show future and historic earnings dates, returns at most next 4 quarters and last 8 quarters by default.
# Note: If more are needed use msft.get_earnings_dates(limit=XX) with increased limit argument.
stock.earnings_dates

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
stock.isin

# show options expirations
stock.options

# show news
stock.news

# get option chain for specific expiration
opt = stock.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts
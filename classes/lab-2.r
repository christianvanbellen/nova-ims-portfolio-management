# -------------------------------------------------------------------------------------------
# Asset Pricing and Portfolio Management | Heuristic portfolios
# -------------------------------------------------------------------------------------------

rm(list=ls(all.names = TRUE))
graphics.off()
close.screen(all.screens = TRUE)
erase.screen()
windows.options(record=TRUE)

library(pacman)
p_load(xts)                   # to manipulate time series of stock data
p_load(quantmod)              # to download stock data
p_load(PerformanceAnalytics)  # to compute performance measures


# -------------------------------------------------------------------------------------------
# Load stock price data and compute returns
# -------------------------------------------------------------------------------------------

# Download data from Yahoo Finance
begin_date <- "2019-01-01"
end_date   <- "2023-10-31"

# FAANG: Facebook (now Meta Platforms), Amazon, Apple, Netflix and Google (now Alphabet)
Tickers <- c("GOOG", "NFLX", "AAPL", "AMZN", "META")  # FAANG
prices <- xts()
for (i in 1:length(Tickers)) {
  tmp <- Ad(getSymbols(Tickers[i], from = begin_date, to = end_date, 
                       periodicity = "weekly", auto.assign = FALSE))  # Adjusted prices
  tmp <- na.approx(tmp, na.rm = FALSE)  # interpolate NAs
  prices <- cbind(prices, tmp)
}
colnames(prices) <- Tickers
tclass(prices) <- "Date"

# Open <- Op(AAPL)  # Open Price; High <- Hi(AAPL)    # High price; Low <- Lo(AAPL)  # Low price; 
# Close<- Cl(AAPL)  # Close Price; Volume <- Vo(AAPL) # Volume; AdjClose <- Ad(AAPL) # Adjusted close

str(prices)
head(prices, 3)
tail(prices,3)

# compute log-returns and linear returns
X_log <- CalculateReturns(prices, "log")[-1]
X_lin <- CalculateReturns(prices)[-1]

N <- ncol(X_log)  # number of stocks
T <- nrow(X_log)  # number of days

# First look at the prices of the stocks:
plot(prices/rep(prices[1, ], each = nrow(prices)), col = rainbow10equal, 
     legend.loc = "topleft", main = "Normalized prices")


# Divide the data into a training set (trn) and test set (tst)

T_trn <- round(0.70*T)  # 70% of data for training set
X_log_trn <- X_log[1:T_trn, ]
X_log_tst <- X_log[(T_trn+1):T, ]
X_lin_trn <- X_lin[1:T_trn, ]
X_lin_tst <- X_lin[(T_trn+1):T, ]


# Estimation of the expected return and covariance matrix

# Estimate directly from log returns
mu_log <- colMeans(X_log_trn)
Sigma_log <- cov(X_log_trn)

# Annualized returns
t(table.AnnualizedReturns(X_log_trn, scale = 252, Rf = 0.0))


# ------------------------------------------------------------------------------
# Buy & Hold (B&H) Strategy
# ------------------------------------------------------------------------------

# Estimate mu and sigma from the in-sample log-returns:
mu <- colMeans(X_log_trn)  # mean return
Sigma <- cov(X_log_trn)    # var-cov matrix

# Var(di�ria) * 252 = Var(anual)
# sd(di�ria) * sqrt(252) = sd(anual)

# Buy & Hold simply means to allocate the whole budget to one stock and stick to it
# Since we have N=9 stocks in our universe, we can define N=9 different 
# B&H portfolios, which we will store as column vectors

# a B&H portfolio is trivially the zero vector with a one on the stock held
w_BnH <- diag(N)
rownames(w_BnH) <- colnames(X_lin)
colnames(w_BnH) <- colnames(X_lin)
w_BnH


# compute the performance of those N=10 portfolios in the training data with the package PerformanceAnalytics
# compute returns of all B&H portfolios
ret_BnH <- xts(X_lin %*% w_BnH, index(X_lin))
ret_BnH_trn <- ret_BnH[1:T_trn, ]
ret_BnH_tst <- ret_BnH[-c(1:T_trn), ]
head(ret_BnH)


# Performance measures

# Table of Annualized Return, Annualized Std Dev, and Annualized Sharpe
t(table.AnnualizedReturns(ret_BnH_trn, scale = 252, Rf = 0.0))

t(table.AnnualizedReturns(ret_BnH_tst, scale = 252, Rf = 0.0))


# Note how the in-sample (ex ante) performance is not maintained out-of-sample (ex post).
# We can compute many other performance measures:

table.DownsideRisk(ret_BnH_trn)


# To compute the wealth or cumulative P&L, we have two options: one assumes the 
# same quantity is repeatedly invested, whereas the other assumes reinvesting (compounding):

# Compute cumulative wealth
# A. same quantity is repeatedly invested
wealth_arith_BnH_trn <- 1 + cumsum(ret_BnH_trn)  # initial budget of 1$

# B. Assume reinvesting (compounding):
wealth_geom_BnH_trn <- cumprod(1 + ret_BnH_trn)  # initial budget of 1$
head(wealth_geom_BnH_trn,3)

# plots
# same as: 
#   plot(wealth_arith_BnH_trn[, 1], main = "Buy & Hold performance (not compounded)", ylab = "wealth")
chart.CumReturns(ret_BnH_trn[, 'GOOG'], 
                 main = paste(Tickers[9], "Buy & Hold performance (not compounded)", sep=": "),
                 geometric = FALSE, col='blue', wealth.index = TRUE)


# same as: 
#   plot(wealth_geom_BnH_trn[, 1], main = "Buy & Hold performance (compounded)", ylab = "wealth")
chart.CumReturns(ret_BnH_trn[, 'NFLX'], 
                 main = paste(Tickers[2], "Buy & Hold performance (not compounded)", sep=": "), 
                 geometric = TRUE, col='magenta', wealth.index = TRUE)


# more plots
chart.CumReturns(ret_BnH, main = "Buy & Hold performance", 
                 wealth.index = TRUE, legend.loc = "topleft", colorset = rich10equal)


# Combined wealth index, period performance, and drawdown chart

# Note: Drawdown: Any time the cumulative returns dips below the maximum cumulative returns, 
#  it's a drawdown. Drawdowns are measured as a percentage of that maximum cumulative return
# , in effect, measured from peak equity.

charts.PerformanceSummary(ret_BnH_trn, main = "Buy & Hold performance", 
                          wealth.index = TRUE, colorset = rich10equal)

chart.Boxplot(ret_BnH_trn)

# Annualized risk and return
chart.RiskReturnScatter(ret_BnH_trn, symbolset = 21, bg = "red")


# ------------------------------------------------------------------------------
# R session: Comparison of 1/N portfolio, quintile portfolio, and GMRP
# ------------------------------------------------------------------------------

w_EWP <- rep(1/N, N)
names(w_EWP) <- colnames(X_lin)
w_EWP

# find indices of sorted stocks
i1 <- sort(mu, decreasing = TRUE, index.return = TRUE)$ix
i2 <- sort(mu/diag(Sigma), decreasing = TRUE, index.return = TRUE)$ix
i3 <- sort(mu/sqrt(diag(Sigma)), decreasing = TRUE, index.return = TRUE)$ix

cbind(i1, i2, i3)
Tickers

# Quintile portfolios 
# Steps: 1) rank the N stocks
#        2) divide them into five parts
#        3) long the top part (and possibly short the bottom part)

# create portfolios
w_QuintP_1 <- w_QuintP_2 <- w_QuintP_3 <- rep(0, N)
w_QuintP_1[i1[1:round(N/5)]] <- 1/round(N/5)
w_QuintP_2[i2[1:round(N/5)]] <- 1/round(N/5)
w_QuintP_3[i3[1:round(N/5)]] <- 1/round(N/5)
w_QuintP <- cbind("QuintP (mu)"        = w_QuintP_1, 
                  "QuintP (mu/sigma2)" = w_QuintP_2, 
                  "QuintP (mu/sigma)"  = w_QuintP_3)
rownames(w_QuintP) <- colnames(X_lin)
w_QuintP


# Global maximum return portfolio (GMRP) 
# GMRP chooses the stock with the highest return during the in-sample period

i_max <- which.max(mu)
w_GMRP <- rep(0, N)
w_GMRP[i_max] <- 1
names(w_GMRP) <- colnames(X_lin)
w_GMRP

# put together all portfolios
w_heuristic <- cbind("EWP" = w_EWP, w_QuintP, "GMRP" = w_GMRP)
round(w_heuristic, digits = 2)

barplot(t(w_heuristic), col = rainbow8equal[1:5], legend = colnames(w_heuristic), beside = TRUE,
        main = "Portfolio allocation of heuristic portfolios", xlab = "stocks", ylab = "dollars")


# Then we can compare the performance (in-sample vs out-of-sample):

# compute returns of all portfolios
ret_heuristic <- xts(X_lin %*% w_heuristic, index(X_lin))
ret_heuristic$`QuintP (mu/sigma2)` <- NULL  # remove since it coincides with "QuintP (mu/sigma)"
ret_heuristic_trn <- ret_heuristic[1:T_trn, ]        # training set
ret_heuristic_tst <- ret_heuristic[-c(1:T_trn), ]    # test set

# Performance metrics
t(table.AnnualizedReturns(ret_heuristic_trn))

t(table.AnnualizedReturns(ret_heuristic_tst))


# Let's plot the wealth evolution (cumulative PnL) over time:
{ chart.CumReturns(ret_heuristic, main = "Cumulative return of heuristic portfolios", 
                   wealth.index = TRUE, legend.loc = "topleft", colorset = rich8equal)
  addEventLines(xts("training", index(X_lin[T_trn])), srt=90, pos=2, lwd = 2, col = "darkblue") }

charts.PerformanceSummary(ret_heuristic, main = "Performance of heuristic portfolios", 
                          wealth.index = TRUE, colorset = rich8equal)

# Finally, we can plot the risk-return scatter plot:
chart.RiskReturnScatter(ret_heuristic_trn, symbolset = 21, bg = "red",
                        main = "Annualized Return and Risk (in-sample)")

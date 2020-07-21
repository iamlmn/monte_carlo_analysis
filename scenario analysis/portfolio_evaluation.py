import yfinance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def _simulate_returns(historical_returns,forecast_days):
  return historical_returns.sample(n = forecast_days, 
                                   replace = True).reset_index(drop = True)


def simulate_modified_returns(
      historical_returns,
      forecast_days,
      correct_mean_by):
  h = historical_returns.copy()
  new_series = h + correct_mean_by
  return new_series.sample(n=forecast_days,  
     replace = True).reset_index(drop=True)


def simulate_portfolio(historical_returns,composition,forecast_days):
  result = 0
  for t in tqdm(composition):
    name,weight = t[0],t[1]
    s = _simulate_returns(historical_returns['return_%s' % (name)], forecast_days)
    result = result + s * weight
  
  return(result)


def simulate_modified_portfolio(
   historical_returns,
   composition,
   forecast_days):
  
    result = 0
  
    for t in composition:
        name,weight,correction = t[0],t[1],t[2]
        s = simulate_modified_returns(
        historical_returns['return_%s' % (name)], 
        forecast_days,correction
        )
    
        result = result + s * weight
    return(result)



def simulation(historical_returns,composition,forecast_days,n_iterations):
  simulated_portfolios = None

  for i in range(n_iterations):
    sim = simulate_modified_portfolio(historical_returns,composition,forecast_days)

    sim_port = pd.DataFrame({'returns_%d' % (i) : sim})

    if simulated_portfolios is None:
      simulated_portfolios = sim_port
    else:
      simulated_portfolios = simulated_portfolios.join(sim_port)
    
  return simulated_portfolios

if __name__ == '__main__':
    portfolio_composition = [('MSFT',0.5),('AAPL',0.2),('GOOG',0.3)]
    returns = pd.DataFrame({})

    # create returns portfolio dataframe

    
    for t in portfolio_composition:
        name = t[0]
        ticker = yfinance.Ticker(name)
        data = ticker.history(interval="1d",start="2010-01-01",end="2019-12-31")
        data['return_%s' % (name)] = data['Close'].pct_change(1)
        returns = returns.join(data[['return_%s' % (name)]],how="outer").dropna()

    # Monte Carlo simulation of a portfolio

    
    # simulate_portfolio(returns,portfolio_composition,10)
    # This may be enough for portfolio simulation, but we want something more, that is the what-if analysis.

    # print("The historical average returns are  : \n", returns.mean(axis=0))
    
    '''
    If we perform portfolio simulation as shown before, 
    we are simply saying that the future returns are a random sample 
    of the past returns. We already know this isn’t completely true. 
    Moreover, maybe we are performing scenario analysis because 
    we want to know what happens if certain conditions will occur. 
    For example, what happens if the average daily return of each stock 
    is lower than its historical value?If we perform portfolio 
    simulation as shown before, we are simply saying that the future returns 
    are a random sample of the past returns. We already know this 
    isn’t completely true. Moreover, maybe we are performing scenario analysis 
    because we want to know what happens if certain conditions will occur. 
    For example, what happens if the average daily return of each 
    stock is lower than its historical value?
    '''

    print('Let’s try to simulate what happens if the average \
    returns drop by -0.0001 for MSFT, -0.001 for AAPL and -0.0005 for GOOG. \
    We must subtract these quantities from each stock and then simulate the  \
    future portfolios with the new, modified data.')



    # We’ll add these corrections directly to the portfolio_composition list (they are the third component of each tuple):

    new_portfolio_composition = [
   ('MSFT', 0.5,-0.0001), 
   ('AAPL', 0.2,-0.001), 
   ('GOOG', 0.3,-0.0005)
]

    # Simulations and results

    forecast_days = 20
    n_iterations = 200

    simulated_portfolios = simulation(returns,
    new_portfolio_composition,forecast_days,n_iterations)



    # Taken the daily returns of a portfolio, we can build the return after N days with the compound interest formula:

    percentile_5th = simulated_portfolios.cumsum().apply(lambda x : np.percentile(x,5),axis=1)
    percentile_95th = simulated_portfolios.cumsum().apply(lambda x : np.percentile(x,95),axis=1)
    average_port = simulated_portfolios.cumsum().apply(lambda x : np.mean(x),axis=1)
    print(percentile_5th.tail(1))
    print(percentile_95th.tail(1))
    print(average_port.tail(1))

    # Confidence interval for future portfolios
    x = range(forecast_days)

    plt.rcParams['figure.figsize'] = [10, 10]

    plt.plot(x,average_port,label="Average portfolio")
    plt.xlabel("Day")
    plt.ylabel("Portfolio return")


    plt.fill_between(x, percentile_5th, percentile_95th,alpha=0.2)
    plt.grid()
    plt.legend()

    plt.show()


    # Probability of beating the portfolio target

    target_return = 0.02
    target_prob_port = simulated_portfolios.cumsum().apply(lambda x : np.mean(x > target_return),axis=1)

    print("Probabilityof beating the portfolio target {} ".format(target_return),target_prob_port.tail(1))


    # The size of the error bars is calculated with the standard error formula:
    err_bars = np.sqrt(
    target_prob_port * (1-target_prob_port) / n_iterations
    )
    x = range(forecast_days)
    plt.rcParams['figure.figsize'] = [10, 10]
    plt.bar(x,target_prob_port,yerr = err_bars)
    plt.xlabel("Day")
    plt.ylabel("Probability of return >= %.2f" % (target_return))
    plt.grid()
    plt.show()



    # Sharpe ratio histogram
    '''
    performance metric of a portfolio
    '''

    sharpe_indices = simulated_portfolios.apply(lambda x : np.mean(x)/np.std(x))
    plt.hist(sharpe_indices,bins="rice")
    plt.xlabel("Sharpe ratio")
    plt.show()
    print("Sharpe ratio mean value",np.mean(sharpe_indices))
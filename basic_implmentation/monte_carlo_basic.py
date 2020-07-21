# Monte carlo simulation on S&P 500 fortunes
import os, shutil
import numpy as np
from pandas import Series, DataFrame
# %matplotlib inline
import matplotlib.pyplot as plt
# locales for currency formatting
import locale
locale.setlocale(locale.LC_ALL, 'en_US')
from tqdm import tqdm


def traditional_prediction(pv, time_horizon, ror, additions):
    # traditional calculation
    for year in tqdm(range(time_horizon)):
        ending = pv * (1 + ror) + additions
        print(locale.currency(ending, grouping=True))
        pv = ending
    return pv

# with probabillity gets more real



# def probabilitic_calcultion(c):
#     market_return = np.random.normal(expected_return, volatility)
#     fv = pv * (1 + market_return) + annual_addition
#     print("\t{}".ljust(10).format(round(market_return, 4)), "\t{}".rjust(10).format(locale.currency(fv, grouping=True)))
#     pv = fv


def simulate_possibilities(pv, expected_return, volatility, time_horizon, annual_addition, iterations = 5000):
    '''
    Returns a simulated dataframe of 
    probablistic calcultion of expected return
    w.r.t given time horizon, present value, expected return
    & Volatiliy.
    '''
    # probabilitic_calcultion & create simulations
    sim = DataFrame()
    for x in tqdm(range(iterations)):
        stream = []
        each_pv = pv
        for year in range(time_horizon):
            market_return = np.random.normal(expected_return, volatility)
            end = each_pv * (1 + market_return) + annual_addition
            #print("\t{}".ljust(10).format(round(market_return, 4)), "\t{}".rjust(10).format(locale.currency(fv, grouping=True)))
            stream.append(end)
            each_pv = end
        sim[x] = stream

    return sim


def plot_first_n_time_series(sim, n = 5):
    plt.close() # clear old plots
    plt.plot(sim[list(range(n))])
    return plt


def summary_stats(sim, n):
    '''
    returns summary of nth or generally n-1th 
    stats summary.
    '''
    ending_values = sim.loc[n]
    return ending_values.describe()


def histogram_plot(ending_values, bins = 100):
    '''
    Histogram plot to understand the distribution.
    '''
    plt.close() # clear old plots
    plt.hist(ending_values, bins = 100)
    return plt
    


def get_probs_my_value(ending_values, sample_expected_amount = 1000000):
    # what is the probability that we have less than given value?
    return len(ending_values[ending_values<sample_expected_amount]) / len(ending_values)
    # print("{} of chances of getting less than a {}".format(probability_of_a_given_profit() * 100, locale.currency(sample_expected_amount)))
    # print("{} of chances of getting more than a {}".format(100 - (probability_of_a_given_profit() * 100), locale.currency(sample_expected_amount)))

def get_probs_my_range(ending_values, sample_expected_amount_bottom = 800000, sample_expected_amount_top = 1200000):
    # point estimate may not be possiblle but ranges yes?
    return (len(ending_values[ (ending_values<sample_expected_amount_top) & (ending_values<sample_expected_amount_bottom)]))/ len(ending_values)
    # print("{} of chances of getting more than a {} and less than {}".format(probability_of_a_given_profit_range() * 100, locale.currency(sample_expected_amount_bottom), locale.currency(sample_expected_amount_top)))


def percentile_table(ptile_list = [5, 10, 15, 20, 25, 50, 75, 80, 90, 95]):
    # calculate the percentile returns
    p_tiles = np.percentile(ending_values, ptile_list)
    for p in range(len(p_tiles)):
        print("{}%-ile - {}% chance that we get ".format( ptile_list[p], 100 - ptile_list[p]).rjust(15),"{}".format(locale.currency(p_tiles[p], grouping = True)))


if __name__ == '__main__':
    output_folder = 'outputs'
    try:
        os.mkdir(output_folder)
    except:
        # clear and creatte again if present
        shutil.rmtree(output_folder)
        os.mkdir(output_folder)
    
    pv = 10000 # present value 
    time_horizon = 30
    ror = 0.7  # expected rate of return
    annual_additions = 10000 # annual additions
    print('Traditional calculation')
    final_tradition_pred = traditional_prediction(pv, time_horizon, ror, annual_additions)
    print('Traditional calculation final prediction  : {} (Impossible, chill bro. This is just to explain why monte carlo)'.format((locale.currency(final_tradition_pred, grouping=True))))
    print("Now lets try Monte carlo simulation analysis")
    # set up expected returns and its volatility.
    expected_return = 0.09
    volatility = 0.18 # nothing but SD.
    iterations = 5000
    sim_df = simulate_possibilities(pv, expected_return, volatility, time_horizon, annual_additions, iterations = iterations)
    sim_df.to_csv('{}/exported_sims.csv'.format(output_folder), index=False)
    plot_first_n_time_series(sim_df, n = 5).savefig('{}/first_{}_time_series_simulations.png'.format(output_folder, 5))
    print(summary_stats(sim_df, time_horizon - 1))
    ending_values = sim_df.loc[time_horizon - 1]
    # get_probs_my_value(ending_values, sample_expected_amount = 1000000)
    # get_probs_my_range(ending_values, sample_expected_amount_bottom = 800000, sample_expected_amount_top = 1200000)
    sample_expected_amount = 1000000 
    sample_expected_amount_bottom = 800000
    sample_expected_amount_top = 1200000
    print("{} of chances of getting less than a {}".format(get_probs_my_value(ending_values, sample_expected_amount = 1000000) * 100, locale.currency(sample_expected_amount)))
    print("{} of chances of getting more than a {}".format(100 - (get_probs_my_value(ending_values, sample_expected_amount = 1000000) * 100), locale.currency(sample_expected_amount)))
    print("{} of chances of getting more than a {} and less than {}".format(get_probs_my_range(ending_values, sample_expected_amount_bottom = 800000, sample_expected_amount_top = 1200000) * 100, locale.currency(sample_expected_amount_bottom), locale.currency(sample_expected_amount_top)))
    histogram_plot(ending_values, bins = 100).savefig('{}/main_histo.png'.format(output_folder))
    percentile_table(ptile_list = [5, 10, 15, 20, 25, 50, 75, 80, 90, 95])
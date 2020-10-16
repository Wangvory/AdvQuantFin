import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.optimize


def compute_portfolio_mean(weights, returns):
    return sum(returns * weights)


def compute_portfolio_var(weights, covariance):
    return np.dot(np.dot(weights, covariance), weights)


def compute_portfolio_mean_var(weights, returns, covariance):
    return compute_portfolio_mean(weights, returns), compute_portfolio_var(weights, covariance)


def solve_frontier(returns, covariance, risk_free_rate):
    def fitness(weights, returns, covariance, risk_free_rate):
        mean, variance = compute_portfolio_mean_var(weights, returns, covariance)
        penalty = 100.0 * np.abs(mean - risk_free_rate)
        return variance + penalty

    frontier_mean, frontier_var = [], []
    number_of_assets = len(returns)
    for r in np.linspace(min(returns), max(returns), num=100):
        weights = np.ones([number_of_assets]) / number_of_assets
        b_ = [(0, 1) for _ in range(number_of_assets)]
        c_ = ({'type': 'eq', 'fun': lambda weights: sum(weights) - 1.0})
        optimized = scipy.optimize.minimize(fitness, weights, (returns, covariance, r),
                                            method='SLSQP', constraints=c_, bounds=b_)
        if not optimized.success:
            raise BaseException(optimized.message)
        frontier_mean.append(r)
        frontier_var.append(compute_portfolio_var(optimized.x, covariance))

    return np.array(frontier_mean), np.array(frontier_var)


def solve_weights(returns, covariance, risk_free_rate):
    def fitness(weights, returns, covariance, risk_free_rate):
        mean, var = compute_portfolio_mean_var(weights, returns, covariance)
        util = (mean - risk_free_rate) / np.sqrt(var)
        return 1.0 / util

    number_of_assets = len(returns)
    weights = np.ones([number_of_assets]) / number_of_assets
    b_ = [(0.0, 1.0) for i in range(number_of_assets)]
    c_ = ({'type': 'eq', 'fun': lambda w: sum(w) - 1.0})
    optimized = scipy.optimize.minimize(fitness, weights, (returns, covariance, risk_free_rate),
                                        method='SLSQP', constraints=c_, bounds=b_)
    if not optimized.success:
        raise BaseException(optimized.message)

    return optimized.x


def create_views_and_link_matrix(names, views):
    r, c = len(views), len(names)
    Q = [views[i][3] for i in range(r)]  # view matrix
    P = np.zeros([r, c])
    nameToIndex = dict()
    for i, n in enumerate(names):
        nameToIndex[n] = i
    for i, v in enumerate(views):
        name1, name2 = views[i][0], views[i][2]
        P[i, nameToIndex[name1]] = +1 if views[i][1] == '>' else -1
        P[i, nameToIndex[name2]] = -1 if views[i][1] == '>' else +1
    return np.array(Q), P


#################################################################################################

def load_data(tickers, market_capitalizations):
    prices, market_caps = [], []
    for ticker in tickers:
        dataframe = pd.read_csv(f'data/{ticker}.csv', index_col=None, parse_dates=['date'])
        p = list(dataframe['close'])[-500:]
        prices.append(p)
        market_caps.append(market_capitalizations[ticker])
    return tickers, prices, market_caps


def assets_historical_returns_and_covariances(prices):
    # create a numpy array
    prices = np.matrix(prices)

    # compute returns
    rows, cols = prices.shape
    returns = np.empty([rows, cols - 1])
    for r in range(rows):
        for c in range(cols - 1):
            p0, p1 = prices[r, c], prices[r, c + 1]
            returns[r, c] = (p1 / p0) - 1

    # compute expected returns
    expected_returns = np.array([])
    for r in range(rows):
        expected_returns = np.append(expected_returns, np.mean(returns[r]))

    # compute covariances
    covars = np.cov(returns)

    # annualize expected returns and covariances
    expreturns = (1.0 + expected_returns) ** 252 - 1.0
    covars = covars * 252.0
    return expreturns, covars


def optimize_frontier(returns, covariances, risk_free_rate):
    weights = solve_weights(returns, covariances, risk_free_rate)
    tan_mean, tan_var = compute_portfolio_mean_var(weights, returns, covariances)
    front_mean, front_var = solve_frontier(returns, covariances, risk_free_rate)
    return Frontier(weights, tan_mean, tan_var, front_mean, front_var)


class Frontier:
    def __init__(self, weights, tan_mean, tan_var, front_mean, front_var):
        self.weights = weights
        self.tan_mean = tan_mean
        self.tan_var = tan_var
        self.front_mean = front_mean
        self.front_var = front_var


def display_frontier(names, returns, covariances, frontiers, title='', color='red'):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 8)

    ax.scatter([covariances[i, i] ** 0.5 for i in range(len(returns))], returns,
               marker='o', color=color, label='Tickers')
    for i in range(len(returns)):
        ax.text(covariances[i, i] ** 0.5, returns[i], f'  {names[i]}',
                verticalalignment='center', color=color)

    ax.plot(frontiers.front_var ** 0.5, frontiers.front_mean, label='Frontier', color=color)
    ax.scatter(frontiers.tan_var ** 0.5, frontiers.tan_mean, marker='*', color=color, s=150, label='Tangent')

    ax.set_xlabel('volatility $\sigma$')
    ax.set_ylabel('return $\mu$')
    ax.grid(True)

    plt.title(title)
    plt.legend()
    plt.show()


def main():
    # set and load data: risk free rate, tickers, market_capitalizations
    # compute historical and returns and covariances
    risk_free_rate = .015
    tickers = ['XOM', 'AAPL', 'MSFT', 'JNJ', 'GE', 'GOOG', 'CVX', 'PG', 'WFC']
    market_capitalizations = {'XOM': 403.02e9, 'AAPL': 392.90e9, 'MSFT': 283.60e9,
                              'JNJ': 243.17e9, 'GE': 236.79e9, 'GOOG': 292.72e9,
                              'CVX': 231.03e9, 'PG': 214.99e9, 'WFC': 218.79e9}
    names, prices, market_caps = load_data(tickers, market_capitalizations)
    weights = np.array(market_caps) / sum(market_caps)

    # compute and print historical returns and covariances
    returns, covariances = assets_historical_returns_and_covariances(prices)
    print(pd.DataFrame({'Return': returns, 'Weight': weights}, index=names).T.to_string())
    print(pd.DataFrame(covariances, columns=names, index=names).to_string())

    # compute, print, and plot mean-variance portfolio optimization
    frontiers = optimize_frontier(returns, covariances, risk_free_rate)
    display_frontier(names, returns, covariances, frontiers, title='Mean-Variance Portfolio', color='red')
    print(pd.DataFrame({'Weight': frontiers.weights}, index=names).T.to_string())

    # Black-Litterman Reverse Optimization
    # Calculate portfolio historical return and variance
    mean, var = compute_portfolio_mean_var(weights, returns, covariances)
    risk_aversion_coefficient = (mean - risk_free_rate) / var
    port_equil_excess_returns = np.dot(np.dot(risk_aversion_coefficient, covariances), weights)

    # Mean-variance Optimization (based on equilibrium returns)
    frontiers_2 = optimize_frontier(port_equil_excess_returns + risk_free_rate, covariances, risk_free_rate)
    display_frontier(names, port_equil_excess_returns + risk_free_rate, covariances, frontiers_2,
                     title='Mean-Variance Portfolio with Equilibrium Returns', color='green')
    print(pd.DataFrame({'Weight': frontiers_2.weights}, index=names).T.to_string())

    # build the views matrices
    views = [('MSFT', '>', 'GE', 0.02),
             ('AAPL', '<', 'JNJ', 0.02)]
    q_matrix, p_matrix = create_views_and_link_matrix(names, views)
    print('Views Matrix')
    print(pd.DataFrame({'Views': q_matrix}).to_string())
    print('Link Matrix')
    print(pd.DataFrame(p_matrix).to_string())

    # calculate omega - uncertainty matrix about views
    tau = .025
    omega = np.dot(np.dot(np.dot(tau, p_matrix), covariances), np.transpose(p_matrix))

    # calculate equilibrium excess returns with views incorporated
    sub_a = np.linalg.inv(np.dot(tau, covariances))
    sub_b = np.dot(np.dot(np.transpose(p_matrix), np.linalg.inv(omega)), p_matrix)
    sub_c = np.dot(np.linalg.inv(np.dot(tau, covariances)), port_equil_excess_returns)
    sub_d = np.dot(np.dot(np.transpose(p_matrix), np.linalg.inv(omega)), q_matrix)
    port_equil_excess_returns = np.dot(np.linalg.inv(sub_a + sub_b), (sub_c + sub_d))

    frontiers_3 = optimize_frontier(port_equil_excess_returns + risk_free_rate, covariances, risk_free_rate)

    display_frontier(names, returns, covariances, frontiers, title='Mean-Variance Portfolio', color='red')
    display_frontier(names, returns, covariances, frontiers_2, title='Implied returns', color='green')
    display_frontier(names, returns, covariances, frontiers_3, title='Implied returns (adjusted views)', color='blue')

    print(pd.DataFrame({'Weight': frontiers_2.weights}, index=names).T.to_string())


if __name__ == '__main__':
    main()

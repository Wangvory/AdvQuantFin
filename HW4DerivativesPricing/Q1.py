import math
import matplotlib as mpl
mpl.rcParams['font.family'] = 'serif'
import numpy as np
import scipy.stats as si

#print('Set the binomial tree with 1000 time periodes')
# input data & index


class BlackScholes(object):
    def __init__(self):
        pass

    # CRR American Option
    @staticmethod
    def CRR_american_option_value(S0, K, T, r, sigma, option_type='C', M=1000):
        # 1. Create Binomial Tree
        dt = T / M  # length of time interval
        df = math.exp(-r * dt)  # discount per interval
        inf = math.exp(r * dt)  # discount per interval
        # calculate up&down prob
        u = math.exp(sigma * math.sqrt(dt))  # up movement
        d = 1 / u  # down movement
        q = (math.exp(r * dt) - d) / (u - d)  # martingale branch probability
        # initiate the matrix
        mu = np.arange(M + 1)
        mu = np.resize(mu, (M + 1, M + 1))
        md = np.transpose(mu)
        # calculated the stock price movement for single time period
        mus = u ** (mu - md)
        mds = d ** md
        S = S0 * mus * mds

        # 2. Calculate stock price  with discount
        mes = S0 * inf ** mu

        # 3. calculate option value for every time node
        if option_type == 'C':
            V = np.maximum(S - K, 0)
            #Calculate the value of early excute
            oreturn = mes - K
        elif option_type == 'P':
            V = np.maximum(K - S, 0)
            #Calculate the value of early excute
            oreturn = K - mes

        # discount the value by weight and probability step by step
        for z in range(0, M):  # backwards iteration
            # Calculate the after-discount value
            ovalue = (q * V[0:M - z, M - z] +
                      (1 - q) * V[1:M - z + 1, M - z]) * df
            # Updating the option value column by column,
            # equivalent to layer-by-layer forward conversion in a binary tree
            # The maximum value of the option price is obtained
            # by discounting later and exercising in advance
            V[0:M - z, M - z - 1] = np.maximum(ovalue, oreturn[0:M - z, M - z - 1])
        return V[0, 0]


    @staticmethod
    def compute_delta(s, k, t, r, sigma, option_type='C'):
        d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        if option_type == 'C':
            return si.norm.cdf(d1, 0.0, 1.0)
        elif option_type == 'P':
            return -si.norm.cdf(-d1, 0.0, 1.0)
        raise Exception('Option type is not valid')

    @staticmethod
    def compute_theta(s, k, t, r, sigma, option_type='C'):
        d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        prob_density = 1 / np.sqrt(2 * np.pi) * np.exp(-d1 ** 2 * 0.5)
        if option_type == 'C':
            return (-sigma * s * prob_density) / (2 * np.sqrt(t)) - r * k * np.exp(-r * t) * si.norm.cdf(d2, 0.0, 1.0)
        elif option_type == 'P':
            return (-sigma * s * prob_density) / (2 * np.sqrt(t)) + r * k * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0)
        raise Exception('Option type is not valid')

    @staticmethod
    def compute_gamma(s, k, t, r, sigma, option_type='C'):
        d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        prob_density = 1 / np.sqrt(2 * np.pi) * np.exp(-d1 ** 2 * 0.5)
        if option_type == 'C' or option_type == 'P':
            return prob_density / (s * sigma * np.sqrt(t))
        raise Exception('Option type is not valid')

def main():
    print("Calculate the option price using 1000 node of time period")
    call_price = BlackScholes.CRR_american_option_value(100.0, 100.0, 1.0, 0.05, 0.25, 'C')
    print(f'Call price: {call_price:10.4e}')
    put_price = BlackScholes.CRR_american_option_value(110.0, 100.0, 1.0, 0.05, 0.25, 'P')
    print(f'Put price: {put_price:10.4e}')

    BS_call_delta = BlackScholes.compute_delta(110.0, 100.0, 1.0, 0.05, 0.25, 'C')
    print(f'BS formula Call delta: {BS_call_delta:10.4e}')
    BS_put_delta = BlackScholes.compute_delta(110.0, 100.0, 1.0, 0.05, 0.25, 'P')
    print(f'BS formula Put delta: {BS_put_delta:10.4e}')
    call_price_delta1 = BlackScholes.CRR_american_option_value(109.5, 100.0, 1.0, 0.05, 0.25, 'C')
    call_price_delta2 = BlackScholes.CRR_american_option_value(110.5, 100.0, 1.0, 0.05, 0.25, 'C')
    call_price_delta3 = BlackScholes.CRR_american_option_value(111.5, 100.0, 1.0, 0.05, 0.25, 'C')
    put_price_delta1 = BlackScholes.CRR_american_option_value(109.5, 100.0, 1.0, 0.05, 0.25, 'P')
    put_price_delta2 = BlackScholes.CRR_american_option_value(110.5, 100.0, 1.0, 0.05, 0.25, 'P')
    print(f'Binomial Tree Call delta: {call_price_delta2 - call_price_delta1:10.4e}')
    print(f'Binomial Tree Put delta: {put_price_delta2 - put_price_delta1:10.4e}')

    call_theta = BlackScholes.compute_theta(110.0, 100.0, 1.0, 0.05, 0.25, 'C')
    print(f'BS formula Call theta: {call_theta:10.4e}')
    put_theta = BlackScholes.compute_theta(110.0, 100.0, 1.0, 0.05, 0.25, 'P')
    print(f'BS formula Put theta: {put_theta:10.4e}')
    call_price_theta1 = BlackScholes.CRR_american_option_value(110.0, 100.0, 1, 0.05, 0.25, 'C')
    call_price_theta2 = BlackScholes.CRR_american_option_value(110.0, 100.0, 2.0, 0.05, 0.25, 'C', 2000)
    put_price_theta1 = BlackScholes.CRR_american_option_value(110.0, 100.0, 1, 0.05, 0.25, 'P')
    put_price_theta2 = BlackScholes.CRR_american_option_value(110.0, 100.0, 2.0, 0.05, 0.25, 'P', 2000)
    print(f'Binomial Tree Call theta: {call_price_theta1 - call_price_theta2:10.4e}')
    print(f'Binomial Tree Put theta: {put_price_theta1 - put_price_theta2:10.4e}')

    gamma = BlackScholes.compute_gamma(110, 100, 1, 0.05, 0.25)
    print(f'BS Formula Call/Put gamma: {gamma:10.4e}')
    CallPutDelta1 = call_price_delta1 - call_price_delta2
    CallPutDelta2 = call_price_delta2 - call_price_delta3
    print(f'Binomial Tree Call/Put gamma: {CallPutDelta2-CallPutDelta1:10.4e}')

if __name__ == '__main__':
    main()


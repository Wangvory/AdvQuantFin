import numpy as np
import scipy.stats as si


class BlackScholes(object):

    def __init__(self):
        pass

    @staticmethod
    def compute_price(s, k, t, r, sigma, option_type='C'):
        d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        if option_type == 'C':
            return s * si.norm.cdf(d1, 0.0, 1.0) - k * np.exp(-r * t) * si.norm.cdf(d2, 0.0, 1.0)
        elif option_type == 'P':
            return k * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0) - s * si.norm.cdf(-d1, 0.0, 1.0)
        raise Exception('Option type is not valid')

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

    @staticmethod
    def compute_vega(s, k, t, r, sigma, option_type='C'):
        d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        prob_density = 1 / np.sqrt(2 * np.pi) * np.exp(-d1 ** 2 * 0.5)
        if option_type == 'C' or option_type == 'P':
            return s * prob_density * np.sqrt(t)
        raise Exception('Option type is not valid')

    @staticmethod
    def compute_rho(s, k, t, r, sigma, option_type='C'):
        d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        if option_type == 'C':
            return t * k * np.exp(-r * t) * si.norm.cdf(d2, 0.0, 1.0)
        elif option_type == 'P':
            return -t * k * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0)
        raise Exception('Option type is not valid')

    @staticmethod
    def compute_implied_vol(s, k, t, quote, r, sigma, option_type='C'):
        if option_type == 'C':
            d1 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
            d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
            fx = s * si.norm.cdf(d1, 0.0, 1.0) - k * np.exp(-r * t) * si.norm.cdf(d2, 0.0, 1.0) - quote
            vega = (1 / np.sqrt(2 * np.pi)) * s * np.sqrt(t) * np.exp(-(si.norm.cdf(d1, 0.0, 1.0) ** 2) * 0.5)

            tolerance = 0.000001
            x0 = sigma
            xnew = x0
            xold = x0 - 1
            while abs(xnew - xold) > tolerance:
                xold = xnew
                xnew = (xnew - fx - quote) / vega
            return abs(xnew)
        elif option_type == 'P':
            d1 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
            d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
            fx = k * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0) - s * si.norm.cdf(-d1, 0.0, 1.0) - quote
            vega = (1 / np.sqrt(2 * np.pi)) * s * np.sqrt(t) * np.exp(-(si.norm.cdf(d1, 0.0, 1.0) ** 2) * 0.5)

            tolerance = 0.000001
            x0 = sigma
            xnew = x0
            xold = x0 - 1
            while abs(xnew - xold) > tolerance:
                xold = xnew
                xnew = (xnew - fx - quote) / vega
            return abs(xnew)
        raise Exception('Option type is not valid')


def main():
    call_price = BlackScholes.compute_price(110, 100, 1, 0.05, 0.25, 'C')
    print(f'Call price: {call_price:10.4e}')
    put_price = BlackScholes.compute_price(110, 100, 1, 0.05, 0.25, 'P')
    print(f'Put price: {put_price:10.4e}')

    call_delta = BlackScholes.compute_delta(110, 100, 1, 0.05, 0.25, 'C')
    print(f'Call delta: {call_delta:10.4e}')
    put_delta = BlackScholes.compute_delta(110, 100, 1, 0.05, 0.25, 'P')
    print(f'Put put: {put_delta:10.4e}')

    call_theta = BlackScholes.compute_theta(110, 100, 1, 0.05, 0.25, 'C')
    print(f'Call theta: {call_theta:10.4e}')
    put_theta = BlackScholes.compute_theta(110, 100, 1, 0.05, 0.25, 'P')
    print(f'Put theta: {put_theta:10.4e}')

    gamma = BlackScholes.compute_gamma(110, 100, 1, 0.05, 0.25)
    print(f'Call/Put gamma: {gamma:10.4e}')

    vega = BlackScholes.compute_vega(110, 100, 1, 0.05, 0.25)
    print(f'Call/Put vega: {vega:10.4e}')

    call_rho = BlackScholes.compute_rho(110, 100, 1, 0.05, 0.25, 'C')
    print(f'Call rho: {call_rho:10.4e}')
    put_rho = BlackScholes.compute_rho(110, 100, 1, 0.05, 0.25, 'P')
    print(f'Put rho: {put_rho:10.4e}')

    call_implied_vol = BlackScholes.compute_implied_vol(110, 100, 19.3, 1, 0.05, 0.25, 'C')
    print(f'Call implied vol: {call_implied_vol:10.4e}')
    put_implied_vol = BlackScholes.compute_implied_vol(110, 100, 4.428, 1, 0.05, 0.25, 'P')
    print(f'Put implied vol: {put_implied_vol:10.4e}')

if __name__ == '__main__':
    main()

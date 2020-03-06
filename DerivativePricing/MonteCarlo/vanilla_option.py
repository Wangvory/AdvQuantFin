import math
from random import gauss


def generate_terminal_price(s, sigma, r, t):
    return s * math.exp((r - 0.5 * sigma ** 2) * t + sigma * math.sqrt(t) * gauss(0, 1.0))


def call_payoff(s_t, k):
    return max(0.0, s_t - k)


def put_payoff(s_t, k):
    return max(0.0, k - s_t)


def main():
    s = 110.0
    k = 100.0
    t = 1.0
    r = 0.05
    sigma = 0.25

    simulations = 500
    call_payoffs = []
    put_payoffs = []

    for i in range(simulations):
        s_t = generate_terminal_price(s, sigma, r, t)
        call_payoffs.append(call_payoff(s_t, k))
        put_payoffs.append(put_payoff(s_t, k))

    call_price = math.exp(-r * t) * (sum(call_payoffs) / float(simulations))
    print(f'Call price = {call_price:.4f}')

    put_price = math.exp(-r * t) * (sum(put_payoffs) / float(simulations))
    print(f'Put price = {put_price:.4f}')


if __name__ == '__main__':
    main()

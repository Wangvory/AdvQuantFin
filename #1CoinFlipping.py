""" Simulation of the Kelly Criterion using Coin Flipping """
import math
import matplotlib.pyplot as plt
import numpy as np


def flip_coin(number_of_flips=1, probabilty_of_heads=0.5):
    return np.random.binomial(size=number_of_flips, n=1, p=probabilty_of_heads)


trials = 10000
flips_per_trial = 200
start_kelly_criterion = 0.10
end_kelly_criterion = 0.90
step_kelly_criterion = 0.05
probability_heads = 0.50
odds = 2.0

theoretical_kelly = probability_heads - (1.0 - probability_heads)/odds

kelly_criterions = np.arange(start_kelly_criterion, end_kelly_criterion + step_kelly_criterion, step_kelly_criterion)
growth_rates = []
start_bankroll = 1.0e6
for kelly_criterion in kelly_criterions:
    sum_growth_rates = 0.0
    for trial in range(trials):
        bankroll = start_bankroll
        flips = flip_coin(flips_per_trial, probability_heads)
        for flip in flips:
            if flip == 1:
                bankroll += odds * kelly_criterion * bankroll
            else:
                bankroll -= 1.0 * kelly_criterion * bankroll
        total_return = math.log(bankroll / start_bankroll)
        growth_rate = total_return / flips_per_trial
        sum_growth_rates += growth_rate
    growth_rate = sum_growth_rates / trials
    growth_rates.append(growth_rate)

max_growth_rate, min_growth_rate = max(growth_rates), min(growth_rates)
optimal_kelly_criterion = kelly_criterions[growth_rates.index(max_growth_rate)]
print(optimal_kelly_criterion, max_growth_rate)

fig, ax = plt.subplots()
ax.plot(kelly_criterions, growth_rates)
ax.set(xlabel='Kelly Criterion', ylabel='Growth Rate',
       title='Coin Flipping Simulation of Kelly Criterion')
ax.grid()

text = f'Kelly: {optimal_kelly_criterion:6.4f} \n Growth: {max_growth_rate:6.4f} \n Theoretical: {theoretical_kelly:6.4f} '
ax.annotate(text,
            xy=(optimal_kelly_criterion, max_growth_rate),
            xytext=((start_kelly_criterion+end_kelly_criterion)/2.0, (max_growth_rate + min_growth_rate)/2.0),
            va="center", ha="right",
            bbox=dict(boxstyle='round4', fc='cyan', ec='blue', lw=2, alpha=0.5),
            arrowprops=dict(fc='crimson', arrowstyle='->'),
            )
plt.show()

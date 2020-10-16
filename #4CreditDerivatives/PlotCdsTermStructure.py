import math

import matplotlib.pyplot as plt


def plot_cds_term_structure(cds_tenors, cds_deal_spreads, cds_upfronts,
                            running_spreads, hazard_rates,
                            times, marginal_defaults, cummulative_defaults):
    fig, axs = plt.subplots(3, sharex=True)

    # running and deal spreads
    #
    axs[0].plot(cds_tenors, 10000.0 * running_spreads, 'b-', label='Running')
    axs[0].plot(cds_tenors, 10000.0 * cds_deal_spreads, 'y--', label='Deal')
    axs[0].set_ylabel('Spread (bps)')
    axs[0].set_title('Running and Deal Spreads with Upfront Percentages')
    _, y_lim_higher = compute_limits([10000.0 * running_spreads, 10000.0 * cds_deal_spreads], 0, 2.00)
    axs[0].set_ylim(0, y_lim_higher)
    axs[0].grid(True, alpha=0.25)

    # upfronts
    #
    color = 'g'
    ax1 = axs[0].twinx()
    ax1.set_ylabel('Upfront (%)', color=color)
    ax1.bar(x=cds_tenors, height=100.0 * cds_upfronts, align='center', width=0.25, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    y_lim_lower, y_lim_higher = compute_limits(100.0 * cds_upfronts, 0, 0.0)
    ax1.set_ylim(ymin=3.0 * y_lim_lower, ymax=4.0 * y_lim_higher)
    ax1.axhline(0, dashes=(1, 1), color=color)

    axs[0].legend(fontsize='x-small')

    # hazard rates
    #
    axs[1].step(cds_tenors, 100.0 * hazard_rates, 'r-')
    axs[1].set_ylabel('Rate (%)')
    axs[1].set_title('Hazard Rates')
    _, y_lim_higher = compute_limits(100.0 * hazard_rates, 0, 1.0)
    axs[1].set_ylim(0.0, y_lim_higher)
    axs[1].grid(True, alpha=0.25)

    # cummulative and marginal default probabilities
    #
    color = 'r'
    axs[2].plot(times, cummulative_defaults, color=color)
    axs[2].set_xlabel('Tenor (yrs)')
    axs[2].set_ylabel('Cummulative', color=color)
    axs[2].tick_params(axis='y', labelcolor=color)
    axs[2].set_title('Cummulative and Marginal Default Probability')
    _, y_lim_higher = compute_limits(cummulative_defaults, 0, 0.5)
    axs[2].set_ylim(0.0, y_lim_higher)
    axs[2].grid(True, alpha=0.25)

    color = 'g'
    ax2 = axs[2].twinx()
    ax2.set_ylabel('Marginal (10E-3)', color=color)
    ax2.step(times[1:], 1000.0 * marginal_defaults[1:], color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    _, y_lim_higher = compute_limits(1000.0 * marginal_defaults[1:], 0, 0.5)
    ax2.set_ylim(0.0, y_lim_higher)

    plt.show()


def compute_limits(values, lower_pad_percent=0, higher_pad_percent=0):
    value_min, value_max = math.inf, -math.inf
    if type(values) is list:
        for value in values:
            value_min = min(value) if min(value) < value_min else value_min
            value_max = max(value) if max(value) > value_max else value_max
    else:
        value_min, value_max = min(values), max(values)

    left_lim = value_min if lower_pad_percent == 0.0 else (value_max - value_min) * lower_pad_percent - value_min
    right_lim = value_max if higher_pad_percent == 0.0 else (value_max - value_min) * higher_pad_percent + value_max
    return left_lim, right_lim

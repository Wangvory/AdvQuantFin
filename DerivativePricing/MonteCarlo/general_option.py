import matplotlib.pyplot as plt
import numpy as np


class Configuration:
    def __init__(self, number_of_scenarios, number_of_timesteps):
        self.number_of_scenarios = number_of_scenarios
        self.number_of_timesteps = number_of_timesteps


class OptionTrade:
    def __init__(self, underlying, strike, risk_free_rate, volatility, time_to_maturity):
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.time_to_maturity = time_to_maturity


class GBMModel:
    def __init__(self, configuration):
        self.configuration = configuration

    def simulate(self, trade):
        prices = []
        timestep = 1
        for scenarioNumber in range(self.configuration.number_of_scenarios):
            drift = (trade.risk_free_rate - 0.5 * (trade.volatility ** 2)) * timestep
            uncertainty = trade.volatility * np.sqrt(timestep) * np.random.normal(0, 1)
            price = trade.underlying * np.exp(drift + uncertainty)
            prices.append(price)
        return prices


class OptionTradePayoffPricer:

    def calculate_call_price(self, trade, prices_per_scenario):
        pay_offs = 0
        total_scenarios = len(prices_per_scenario)
        for i in range(total_scenarios):
            price = prices_per_scenario[i]
            pay_off = max(price - trade.strike, 0)
            pay_offs = pay_offs + pay_off

        discount_rate = np.exp(-1.0 * trade.risk_free_rate * trade.time_to_maturity)
        return discount_rate * pay_offs / total_scenarios


class MonteCarloEngineSimulator:

    def __init__(self, configuration, model):
        self.configuration = configuration
        self.model = model

    def simulate(self, trade, trade_pricer):
        prices_per_scenario = self.model.simulate(trade)
        MonteCarloEngineSimulator.plot_scenario_paths(prices_per_scenario, trade)
        return trade_pricer.calculate_call_price(trade, prices_per_scenario)

    @staticmethod
    def plot_scenario_paths(prices_per_scenario, trade):
        x, y = [], []
        for i in prices_per_scenario:
            y.append(i)
            y.append(trade.underlying)
            x.append(1)
            x.append(0)
            plt.plot(x, y)

        plt.ylabel('Underlying')
        plt.xlabel('Timestep')
        plt.show()


def main():
    configuration = Configuration(500, 10)
    trade = OptionTrade(110, 100, 0.05, 0.25, 1)
    model = GBMModel(configuration)
    trade_pricer = OptionTradePayoffPricer()
    simulator = MonteCarloEngineSimulator(configuration, model)

    price = simulator.simulate(trade, trade_pricer)
    print(price)


if __name__ == '__main__':
    main()

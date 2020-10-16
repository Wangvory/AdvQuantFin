import matplotlib.pyplot as plt
import numpy as np


class Configuration:
    def __init__(self, number_of_simulations, number_of_timesteps):
        self.number_of_simulations = number_of_simulations
        self.number_of_timesteps = number_of_timesteps


class OptionTrade:
    def __init__(self, underlying, strike, risk_free_rate, volatility, time_to_maturity, option_type='C'):
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.time_to_maturity = time_to_maturity
        self.option_type = option_type


class GbmModel:
    def __init__(self, configuration):
        self.configuration = configuration

    def simulate(self, trade):
        prices = [(0.0, trade.underlying)]
        timestep = trade.time_to_maturity / self.configuration.number_of_timesteps
        times = np.linspace(timestep, trade.time_to_maturity, self.configuration.number_of_timesteps)
        for time in times:
            drift = (trade.risk_free_rate - 0.5 * (trade.volatility ** 2.0)) * timestep
            diffusion = trade.volatility * np.sqrt(timestep) * np.random.normal(0, 1)
            price = prices[-1][1] * np.exp(drift + diffusion)
            prices.append((time, price))
        return prices


class OptionTradePayoffPricer:
    def __init__(self):
        pass

    def calculate_price(self, trade, payoff_prices_per_simulation):
        if trade.option_type == 'C':
            return self.__calculate_call_price(trade, payoff_prices_per_simulation)
        elif trade.option_type == 'P':
            return self.__calculate_put_price(trade, payoff_prices_per_simulation)

    def __calculate_call_price(self, trade, payoff_prices_per_simulation):
        payoffs = []
        for payoff_price in payoff_prices_per_simulation:
            payoffs.append(max(payoff_price - trade.strike, 0))

        discount_rate = np.exp(-1.0 * trade.risk_free_rate * trade.time_to_maturity)
        return discount_rate * sum(payoffs) / len(payoffs)

    def __calculate_put_price(self, trade, payoff_prices_per_simulation):
        payoffs = []
        for payoff_price in payoff_prices_per_simulation:
            payoffs.append(max(trade.strike - payoff_price, 0))

        discount_rate = np.exp(-1.0 * trade.risk_free_rate * trade.time_to_maturity)
        return discount_rate * sum(payoffs) / len(payoffs)


class MonteCarloEngineSimulator:
    # class level attributes
    times, paths = [], []

    def __init__(self, configuration, model):
        self.configuration = configuration
        self.model = model

    def simulate(self, trade, trade_pricer):
        self.payoff_prices_per_simulation = []
        for simulation_index in range(self.configuration.number_of_simulations):
            self.prices_per_simulation = self.model.simulate(trade)
            self.payoff_prices_per_simulation.append(self.prices_per_simulation[-1][1])
            MonteCarloEngineSimulator.add_simulation_path(prices_per_simulation, trade)
        MonteCarloEngineSimulator.plot_simulation_paths(trade)
        return trade_pricer.calculate_price(trade, payoff_prices_per_simulation)

    @staticmethod
    def add_simulation_path(prices_per_simulation, trade):
        x, y = [], []
        for price_per_simulation in prices_per_simulation:
            x.append(price_per_simulation[0])
            y.append(price_per_simulation[1])

        MonteCarloEngineSimulator.times.append(x)
        MonteCarloEngineSimulator.paths.append(y)

    @staticmethod
    def plot_simulation_paths(trade):
        for index in range(len(MonteCarloEngineSimulator.times)):
            plt.plot(MonteCarloEngineSimulator.times[index], MonteCarloEngineSimulator.paths[index])
        strike_line_x = [0.0, trade.time_to_maturity]
        strike_line_y = [trade.strike, trade.strike]
        plt.plot(strike_line_x, strike_line_y, 'k-' )
        plt.ylabel('Underlying')
        plt.xlabel('Timestep')
        plt.show()


def main():
    configuration = Configuration(1000, 252)
    trade = OptionTrade(110, 100, 0.05, 0.25, 1, 'C')
    model = GbmModel(configuration)
    trade_pricer = OptionTradePayoffPricer()
    simulator = MonteCarloEngineSimulator(configuration, model)
    price = simulator.simulate(trade, trade_pricer)
    print(f'Call Price: {price:10.4e}')

    trade = OptionTrade(110, 100, 0.05, 0.25, 1, 'P')
    model = GbmModel(configuration)
    trade_pricer = OptionTradePayoffPricer()
    simulator = MonteCarloEngineSimulator(configuration, model)
    price = simulator.simulate(trade, trade_pricer)
    print(f'Put Price: {price:10.4e}')


if __name__ == '__main__':
    main()

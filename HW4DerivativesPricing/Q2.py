import matplotlib.pyplot as plt
import numpy as np

class Configuration:
    def __init__(self, number_of_simulations, number_of_timesteps):
        self.number_of_simulations = number_of_simulations
        self.number_of_timesteps = number_of_timesteps

class OptionTrade:
    def __init__(self, underlying, strike, risk_free_rate, volatility,
                 time_to_maturity, option_type='C'):
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.time_to_maturity = time_to_maturity
        self.option_type = option_type

class BarrierOptionTrade(OptionTrade):
    def __init__(self, underlying, strike, risk_free_rate, volatility,
                 time_to_maturity, option_type, direction, barrier_price):
        super(BarrierOptionTrade, self).__init__\
            (underlying, strike, risk_free_rate, volatility, time_to_maturity,option_type)
        self.direction = direction
        self.barrier_price = barrier_price

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
        payoff_prices_per_simulation = []
        for simulation_index in range(self.configuration.number_of_simulations):
            prices_per_simulation = self.model.simulate(trade)
            payoff_prices_per_simulation.append(prices_per_simulation[-1][1])
            MonteCarloEngineSimulator.add_simulation_path(prices_per_simulation)
        MonteCarloEngineSimulator.plot_simulation_paths(trade)
        MonteCarloEngineSimulator.times,MonteCarloEngineSimulator.paths=[],[]
        return trade_pricer.calculate_price(trade, payoff_prices_per_simulation)

    def BarrierSimulate(self, trade, trade_pricer):
        payoff_prices_per_simulation = []
        for simulation_index in range(self.configuration.number_of_simulations):
            prices_per_simulation = self.model.simulate(trade)
            if trade.direction =='Up' and max([p[1] for p in prices_per_simulation])>= trade.barrier_price:
                payoff_prices_per_simulation.append(prices_per_simulation[-1][1])
            elif trade.direction=='Down' and min([p[1] for p in prices_per_simulation])<= trade.barrier_price:
                payoff_prices_per_simulation.append(prices_per_simulation[-1][1])
            else:
                payoff_prices_per_simulation.append(0)
            MonteCarloEngineSimulator.add_simulation_path(prices_per_simulation)
        MonteCarloEngineSimulator.plot_simulation_paths(trade)
        MonteCarloEngineSimulator.times, MonteCarloEngineSimulator.paths = [], []
        return trade_pricer.calculate_price(trade, payoff_prices_per_simulation)

    def AsiaSimulate(self, trade, trade_pricer):
        payoff_prices_per_simulation = []
        for simulation_index in range(self.configuration.number_of_simulations):
            prices_per_simulation = self.model.simulate(trade)
            payoff_prices_per_simulation.append(np.mean([p[1] for p in prices_per_simulation]))
            MonteCarloEngineSimulator.add_simulation_path(prices_per_simulation)
        MonteCarloEngineSimulator.plot_simulation_paths(trade)
        MonteCarloEngineSimulator.times, MonteCarloEngineSimulator.paths = [], []
        return trade_pricer.calculate_price(trade, payoff_prices_per_simulation)


    @staticmethod
    def add_simulation_path(prices_per_simulation):
        x, y = [], []
        for price_per_simulation in prices_per_simulation:
            x.append(price_per_simulation[0])
            y.append(price_per_simulation[1])

        MonteCarloEngineSimulator.times.append(x)
        MonteCarloEngineSimulator.paths.append(y)

    @staticmethod
    def plot_simulation_paths(trade):
        plt.figure()
        for index in range(len(MonteCarloEngineSimulator.times)):
            plt.plot(MonteCarloEngineSimulator.times[index], MonteCarloEngineSimulator.paths[index])
        strike_line_x = [0.0, trade.time_to_maturity]
        strike_line_y = [trade.strike, trade.strike]
        plt.plot(strike_line_x, strike_line_y, 'k-' )
        plt.ylabel('Underlying')
        plt.xlabel('Timestep')
        plt.show()

def main():
    configuration = Configuration(100, 100)
    CallTrade = OptionTrade(110, 100, 0.05, 0.25, 1, 'C')
    PutTrade = OptionTrade(110, 100, 0.05, 0.25, 1, 'P')
    CallBarrierUpTrade = BarrierOptionTrade(110, 100, 0.05, 0.25, 1, 'C','Up', 105)
    CallBarrierDownTrade = BarrierOptionTrade(110, 100, 0.05, 0.25, 1, 'C','Down', 95)
    PutBarrierUpTrade = BarrierOptionTrade(110, 100, 0.05, 0.25, 1, 'P','Up', 105)
    PutBarrierDownTrade = BarrierOptionTrade(110, 100, 0.05, 0.25, 1, 'P','Down', 95)

    model = GbmModel(configuration)
    trade_pricer = OptionTradePayoffPricer()
    GeneralSimulator = MonteCarloEngineSimulator(configuration, model)

    GeneralCallPrice = GeneralSimulator.simulate(CallTrade, trade_pricer)
    print(f'General Option Call Price: {GeneralCallPrice:10.4e}')
    GeneralPutPrice = GeneralSimulator.simulate(PutTrade, trade_pricer)
    print(f'General Option Put Price: {GeneralPutPrice:10.4e}')

    AsiaCallPrice = GeneralSimulator.AsiaSimulate(CallTrade, trade_pricer)
    print(f'Asia Option Call Price: {AsiaCallPrice:10.4e}')
    AsiaPutPrice = GeneralSimulator.AsiaSimulate(PutTrade, trade_pricer)
    print(f'Asia Option Put Price: {AsiaPutPrice:10.4e}')

    BarrierUpInPrice = GeneralSimulator.BarrierSimulate(CallBarrierUpTrade, trade_pricer)
    BarrierDownInPrice = GeneralSimulator.BarrierSimulate(CallBarrierDownTrade, trade_pricer)
    print(f'Barrier Call Price with up and in at barrier price {CallBarrierUpTrade.barrier_price}'
          f':{BarrierUpInPrice:10.4e}')
    print(f'Barrier Call Price with down and in at barrier price {CallBarrierDownTrade.barrier_price}'
          f':{BarrierDownInPrice:10.4e}')
    BarrierUpOutPrice = GeneralSimulator.BarrierSimulate(PutBarrierUpTrade, trade_pricer)
    BarrierDownOutPrice = GeneralSimulator.BarrierSimulate(PutBarrierDownTrade, trade_pricer)
    print(f'Barrier Call Price with up and out at barrier price {PutBarrierUpTrade.barrier_price} '
          f':{BarrierUpOutPrice:10.4e}')
    print(f'Barrier Call Price with down and out at barrier price {PutBarrierDownTrade.barrier_price}'
          f': {BarrierDownOutPrice:10.4e}')
    return


if __name__ == '__main__':
    main()

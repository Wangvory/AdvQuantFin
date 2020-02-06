import math


class TermStructure(object):

    def __init__(self):
        self.bonds = []
        self.spot_rates = []
        self.forward_6m_rates = []
        self.discount_factors = []
        for _ in range(60):
            self.spot_rates.append(0.0)
            self.forward_6m_rates.append(0.0)
            self.discount_factors.append(0.0)

    def set_bonds(self, bonds):
        self.bonds = bonds

    def get_spot_rate(self, index):
        return self.spot_rates[index]

    def get_forward_6m_rate(self, index):
        return self.forward_6m_rates[index]

    def get_discount_factor(self, index):
        return self.discount_factors[index]

    def compute_spot_rates(self):
        for bond in self.bonds:
            if bond.get_name() == "6m":
                self.spot_rates[0] = bond.compute_ytm()
            elif bond.get_name() == "1y":
                bond.bootstrap_spot_rate(self.spot_rates, 0, 1)
            elif bond.get_name() == "2y":
                bond.bootstrap_spot_rate(self.spot_rates, 1, 3)
            elif bond.get_name() == "3y":
                bond.bootstrap_spot_rate(self.spot_rates, 3, 5)
            elif bond.get_name() == "5y":
                bond.bootstrap_spot_rate(self.spot_rates, 5, 9)
            elif bond.get_name() == "7y":
                bond.bootstrap_spot_rate(self.spot_rates, 9, 13)
            elif bond.get_name() == "10y":
                bond.bootstrap_spot_rate(self.spot_rates, 13, 19)
            elif bond.get_name() == "20y":
                bond.bootstrap_spot_rate(self.spot_rates, 19, 39)
            elif bond.get_name() == "30y":
                bond.bootstrap_spot_rate(self.spot_rates, 39, 59)

    def compute_discount_factors(self):
        """ Compute discount factors from spot rates assuming compounding frequency is twice per year.
        """
        for i in range(len(self.spot_rates)):
            self.discount_factors[i] = 1.0 / math.pow(1.0 + (self.spot_rates[i] / 100.0 / 2.0), (i + 1))

    def compute_forward_6m_rates(self):
        for i in range(len(self.spot_rates) - 1):
            self.forward_6m_rates[i] = (math.pow(1.0 + self.spot_rates[i + 1] / 100.0 / 2.0, i + 2) /
                                        math.pow(1.0 + self.spot_rates[i] / 100.0 / 2.0, i + 1) - 1.0) * 100.0

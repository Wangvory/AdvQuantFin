import math


class TermStructure(object):

    def __init__(self):
        self.bonds = []
        self.spot_rates = []
        self.forward_6m_rates = []
        self.forward_3m_rates = []
        self.discount_factors = []
        for _ in range(4):
            self.forward_6m_rates.append(0.0)
            self.forward_3m_rates.append(0.0)
            self.discount_factors.append(0.0)

    def set_bonds(self, bonds):
        self.bonds = bonds

    def get_spot_rate(self, index):
        return self.spot_rates[index]

    def get_forward_6m_rate(self, index):
        return self.forward_6m_rates[index]

    def get_forward_3m_rate(self, index):
        return self.forward_3m_rates[index]

    def get_discount_factor(self, index):
        return self.discount_factors[index]

    def compute_spot_rates(self):
        for bond in self.bonds:
            if bond.get_name() == '1m':
                spots=0
            else:
                spots=bond.get_spotrate()
            self.spot_rates.append(spots)

    def compute_discount_factors(self):
        for i in range(len(self.spot_rates)):
            self.discount_factors[i] = 1.0 / math.pow(1.0 + (self.spot_rates[i] / 100.0), (i + 1))

    def compute_forward_6m_rates(self):
        for i in range(len(self.spot_rates) - 2):
            self.forward_6m_rates[i] = ((1.0 + self.spot_rates[i + 2] / 100.0 ) /
                                        (1.0 + self.spot_rates[i] / 100.0) - 1.0) * 100.0
    def compute_forward_3m_rates(self):
        for i in range(len(self.spot_rates) - 1):
            self.forward_3m_rates[i] = ((1.0 + self.spot_rates[i + 1] / 100.0) /
                                        (1.0 + self.spot_rates[i] / 100.0) - 1.0) * 100.0

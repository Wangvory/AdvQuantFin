import math
from Bond import *

class TermStructure(object):

    def __init__(self):
        self.bonds = []
        self.spot_rates = []
        self.forward_6m_rates = []
        self.discount_factors = []
        for _ in range(20):
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

    def compute_discount_factors(self):
        for i in range(len(self.spot_rates)):
            self.discount_factors[i] = math.pow(1.0 + self.spot_rates[i] / 100.0 / 2.0, -(i + 1) / 2.0)

    def compute_forward_6m_rates(self):
        for i in range(len(self.spot_rates) - 1):
            self.forward_6m_rates[i] = (math.pow(
                (math.pow(1.0 + self.spot_rates[i + 1] / 100.0 / 2.0, (i + 2) / 2.0) /
                 math.pow(1.0 + self.spot_rates[i] / 100.0 / 2.0, (i + 1) / 2.0)),
                1.0 / 0.5) - 1.0) * 100.0 * 2.0


if __name__ == "__main__":
    bonds = []

    name = "6m"
    coupon = 4.0
    issue_date = 20130301
    maturity_date = 20130901
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    name = "1y"
    coupon = 5.0
    issue_date = 20130301
    maturity_date = 20140301
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    name = "2y"
    coupon = 7.0
    issue_date = 20130301
    maturity_date = 20150301
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    name = "3y"
    coupon = 9.0
    issue_date = 20130301
    maturity_date = 20160301
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    name = "5y"
    coupon = 9.25
    issue_date = 20130301
    maturity_date = 20180301
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    name = "7y"
    coupon = 9.50
    issue_date = 20130301
    maturity_date = 20200301
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    name = "10y"
    coupon = 10.0
    issue_date = 20130301
    maturity_date = 20230301
    compounding_frequency_per_annum = 2
    price = 100.0
    bond = Bond(name, coupon, issue_date, maturity_date, compounding_frequency_per_annum)
    bond.set_price(price)
    bonds.append(bond)

    print(f'Name\tCoupon\tIssueDate\tMaturityDate\tPrice\t\tYTM')
    for bond in bonds:
        print(
            f'{bond.get_name()}\t{bond.get_coupon():10.4f}\t{bond.get_issue_date()}\t{bond.get_maturity_date()}\t{bond.get_price():10.4f}\t{bond.compute_ytm():10.4f}')

    term_structure = TermStructure()
    term_structure.set_bonds(bonds)
    term_structure.compute_spot_rates()
    term_structure.compute_discount_factors()
    term_structure.compute_forward_6m_rates()

    tenors = ["6m", "1y", "18m", "2y", "2.5y", "3y", "3.5y", "4y", "4.5y", "5y", "5.5y", "6y", "6.5y", "7y", "7.5y", "8y", "8.5y", "9y", "9.5y", "10y"]

    print(f'Tenor\tSpot Rate\tDiscount Factor\tForward 6m Rate')
    for i in range(20):
        print(f'{tenors[i]}\t{term_structure.get_spot_rate(i):10.4f}\t{term_structure.get_discount_factor(i):10.4f}\t{term_structure.get_forward_6m_rate(i):10.4f}')

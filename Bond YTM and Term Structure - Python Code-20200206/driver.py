import csv
import matplotlib.pylab as plt
import seaborn as sns

from Treasury.bond import Bond
from Treasury.term_structure import TermStructure


def read_bonds_from_file(file_name):
    rows = []
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for reader_row in reader:
            reader_row[0] = reader_row[0].strip().lower()
            reader_row[1] = float(reader_row[1])
            reader_row[2] = int(reader_row[2])
            reader_row[3] = int(reader_row[3])
            reader_row[4] = int(reader_row[4])
            rows.append(reader_row)
    return rows


def main():
    # read bonds from a file and instantiate bond objects
    bond_instruments = read_bonds_from_file("bonds.txt")
    bonds = []
    for bond_instrument in bond_instruments:
        bond = Bond(bond_instrument[0], bond_instrument[1], bond_instrument[2], bond_instrument[3], bond_instrument[4])
        bond.set_price(float(bond_instrument[5]))
        bonds.append(bond)

    # compute yield-to-maturities for bonds
    tenors_from_bonds, ytm_from_bonds = [], []
    for bond in bonds:
        tenors_from_bonds.append(bond.get_tenor_in_years())
        ytm_from_bonds.append(bond.compute_ytm())

    # compute term structure (spot and forward rates) and discount factors
    term_structure = TermStructure()
    term_structure.set_bonds(bonds)
    term_structure.compute_spot_rates()
    term_structure.compute_discount_factors()
    term_structure.compute_forward_6m_rates()

    tenor_count = 60
    ts_tenors = [(i + 1) * 0.5 for i in range(tenor_count)]
    ts_spot_rates, ts_forward_6m_rates, ts_discount_factors = [], [], []
    for i in range(tenor_count):
        ts_spot_rates.append(term_structure.get_spot_rate(i))
        ts_forward_6m_rates.append(term_structure.get_forward_6m_rate(i))
        ts_discount_factors.append(term_structure.get_discount_factor(i))

    print(f'Name\tCoupon\tIssueDate\tMaturityDate\tPrice\t\tYTM')
    for bond in bonds:
        print(f'{bond.get_name()}\t{bond.get_coupon():10.4f}' +
              f'\t{bond.get_issue_date()}\t{bond.get_maturity_date()}' +
              f'\t{bond.get_price():10.4f}\t{bond.compute_ytm():10.4f}')
    print(f'Tenor\tSpot Rate\tDiscount Factor\tForward 6m Rate')
    for i in range(60):
        tenor = (i + 1) * 0.5
        print(f'{tenor:4.1f}y\t{term_structure.get_spot_rate(i):10.4f}' +
              f'\t{term_structure.get_discount_factor(i):10.4f}\t{term_structure.get_forward_6m_rate(i):10.4f}')

    # plot term structure of spot and forward rates
    sns.set()
    fig, ax = plt.subplots()
    ax.plot(ts_tenors, ts_spot_rates, linewidth=2, label='Spot', color='blue')
    ax.plot(ts_tenors[:-1], ts_forward_6m_rates[:-1], linewidth=2, label='6m Forward', color='orange')
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.set_xlabel('Tenor (yrs)')
    ax.set_ylabel('Rate')
    ax.set_title(f'Spot and Forward 6m Rates')
    ax.legend(loc='best', fontsize='x-small')
    plt.show()

    # plot term structure of discount factors
    fig, ax = plt.subplots()
    ax.plot(ts_tenors, ts_discount_factors, linewidth=2, label='Discount Factor', color='blue')
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.set_xlabel('Tenor (yrs)')
    ax.set_ylabel('Discount Factor')
    ax.set_title(f'Discount Factors')
    ax.legend(loc='best', fontsize='x-small')
    plt.show()


if __name__ == '__main__':
    main()

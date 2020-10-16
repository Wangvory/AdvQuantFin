import math
import numpy as np
import PlotCdsTermStructure

class CdsTermStructure(object):

    def __init__(self, cds_tenors, interest_rate, recovery_rate, cds_deal_spreads, cds_upfronts):
        self.cds_tenors = np.array(cds_tenors)
        self.interest_rate = interest_rate
        self.recovery_rate = recovery_rate
        self.cds_deal_spreads = np.array(cds_deal_spreads)
        self.cds_upfronts = np.array(cds_upfronts)

        self.time_increment = 0.05
        self.times = np.arange(0.0, 10.001, self.time_increment)
        self.discount_factors = np.exp(-self.interest_rate * self.times)
        self.cumulative_survival_probabilities = np.ones(len(self.times))
        self.cumulative_default_probabilities = np.zeros(len(self.times))
        self.marginal_default_probabilities = np.zeros(len(self.times))
        self.premiums = np.zeros(len(self.times))
        self.defaults = np.zeros(len(self.times))
        self.accrual_times = np.zeros(len(self.times))

        self.running_spreads = np.zeros(len(self.cds_tenors))
        self.hazard_rates = np.zeros(len(self.cds_tenors))
        self.risky_annuity = np.zeros(len(self.cds_tenors))
        self.default_legs = np.zeros(len(self.cds_tenors))
        self.mtm = np.zeros(len(self.cds_tenors))

    def compute_schedule(self, tenor_index):
        self.discount_factors = np.exp(-self.interest_rate * self.times)
        self.cumulative_survival_probabilities = np.ones(len(self.times))
        self.cumulative_default_probabilities = np.zeros(len(self.times))
        self.marginal_default_probabilities = np.zeros(len(self.times))
        self.premiums = np.zeros(len(self.times))
        self.defaults = np.zeros(len(self.times))
        self.accrual_times = np.zeros(len(self.times))

        for index in range(1, len(self.times)):
            # determine to which cds does this index belong to
            hazard_rate = self.hazard_rates[0]
            for cds_index in range(len(self.cds_tenors)):
                if index <= int(self.cds_tenors[cds_index] / self.time_increment):
                    hazard_rate = self.hazard_rates[cds_index]
                    break
            #这里是？？？？
            self.cumulative_survival_probabilities[index] = self.cumulative_survival_probabilities[index - 1] * \
                                                            math.exp(-self.time_increment * hazard_rate)
            self.cumulative_default_probabilities[index] = 1.0 - self.cumulative_survival_probabilities[index]
            self.marginal_default_probabilities[index] = \
                self.cumulative_survival_probabilities[index - 1] - self.cumulative_survival_probabilities[index]
            self.defaults[index] = self.discount_factors[index] * self.marginal_default_probabilities[index] * \
                                   (1.0 - self.recovery_rate)
            if self.times[index] * 100 % 25 == 0:
                self.accrual_times[index] = 0.0
                self.premiums[index] = self.discount_factors[index] * self.cumulative_survival_probabilities[
                    index] * 1.0 / 4.0
            else:
                self.accrual_times[index] = self.times[index] - self.times[index - 1]

        self.last_index = int(self.cds_tenors[tenor_index] / self.time_increment)

        self.risky_annuity[tenor_index] = sum(self.premiums[0:self.last_index + 1])
        self.default_legs[tenor_index] = sum(self.defaults[0:self.last_index + 1])
        self.mtm[tenor_index] = self.default_legs[tenor_index] - self.risky_annuity[tenor_index] * \
                                self.cds_deal_spreads[tenor_index] - self.cds_upfronts[tenor_index]
        self.running_spreads[tenor_index] = self.default_legs[tenor_index] / self.risky_annuity[tenor_index]

    def FiveTenSpread(self):
        self.FiveTenAnnuity = sum(self.premiums[100:201])
        self.FiveTenDeftLeg = sum(self.defaults[100:201])
        self.FiveTenSpreadPrice = self.FiveTenDeftLeg/self.FiveTenAnnuity * 10000
        return self.FiveTenSpreadPrice

    def compute(self):
        """ compute the term structure of default probabilities
        """
        self.hazard_rates = np.zeros(len(self.cds_tenors))
        self.risky_annuity = np.zeros(len(self.cds_tenors))
        self.default_legs = np.zeros(len(self.cds_tenors))
        self.mtm = np.zeros(len(self.cds_tenors))

        count_iterations, tolerance = 50, 0.0000000001
        x1, x2 = 0.01, 0.02
        for tenor_index in range(len(self.cds_tenors)):
            self.hazard_rates[tenor_index] = x1
            self.compute_schedule(tenor_index)
            f1 = self.mtm[tenor_index]

            self.hazard_rates[tenor_index] = x2
            self.compute_schedule(tenor_index)
            f2 = self.mtm[tenor_index]

            if math.fabs(f1) < math.fabs(f2):
                root = x1
                x1 = x2
                f1, f2 = f2, f1
            else:
                x1 = x1
                root = x2

            # apply the secant method to find root
            for _ in range(count_iterations):
                dx = (x1 - root) * f2 / (f2 - f1)
                x1 = root
                f1 = f2
                root += dx

                self.hazard_rates[tenor_index] = root
                self.compute_schedule(tenor_index)
                f2 = self.mtm[tenor_index]

                if math.fabs(dx) < tolerance or math.fabs(f2) < tolerance:
                    break

        return


def main():
    """ mainline driver to compute term structure of default probabilities from term structure of CDS spreads
    """
    # input parameters
    #
    # interest rate, assumed constant throughout
    # recovery rate, the same for all cds' within the term structure
    # term structure of tenors in years, deal spreads in bps, and upfront as a percentage
    interest_rate = 1.0 / 100.0
    recovery_rate = 40.0 / 100.0
    cds_tenors = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]
    cds_deal_spreads1 = [500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0]
    cds_deal_spreads2 = [501.0, 501.0, 501.0, 501.0, 501.0, 501.0, 501.0, 501.0]
    cds_upfronts = [-1.0, -0.5, -0.4, -0.3, -0.2, 0.0, 1.0, 7.0]

    for index in range(len(cds_deal_spreads1)):
        cds_deal_spreads1[index] /= 10000.0
    for index in range(len(cds_deal_spreads2)):
        cds_deal_spreads2[index] /= 10000.0
    for index in range(len(cds_upfronts)):
        cds_upfronts[index] /= 100.0

    # instantiate a cds term structure and compute
    cds_term_structure1 = CdsTermStructure(cds_tenors, interest_rate, recovery_rate, cds_deal_spreads1, cds_upfronts)
    cds_term_structure2 = CdsTermStructure(cds_tenors, interest_rate, recovery_rate, cds_deal_spreads2, cds_upfronts)
    cds_term_structure1.compute()
    cds_term_structure2.compute()
    cds_term_structure1.FiveTenSpread()
    cds_term_structure2.FiveTenSpread()

    # print all results to the console
    print(f'Tenor\tDealSpread\tUpfront\tRunningSpread\tHazardRate\tRiskyAnnuity\t\tDefaultLeg\t\tMTM')
    for index in range(len(cds_tenors)):
        print(f'{cds_tenors[index]:5.1f}'
              f'\t{10000.0 * cds_deal_spreads1[index]:10.1f}'
              f'\t{100.0 * cds_upfronts[index]:10.1f}%'
              f'\t{10000.0 * cds_term_structure1.running_spreads[index]:10.1f}'
              f'\t{100 * cds_term_structure1.hazard_rates[index]:10.4f}%'
              f'\t{cds_term_structure1.risky_annuity[index]:12.6f}'
              f'\t{cds_term_structure1.default_legs[index]:12.6f}'
              f'\t{100.0 * cds_term_structure1.mtm[index]:10.2f}%')

    print("Given the DealSpread and Upfront Lists, a 5y-10y spread trade value =",
          "%.5f" % cds_term_structure1.FiveTenSpreadPrice)
    print("DV01: the dollar value change for a 1 bp move on the 5y-10y spread trade=",
           round(cds_term_structure2.FiveTenSpreadPrice-cds_term_structure1.FiveTenSpreadPrice,5))
    print("Skip the plot")
'''
    # plot of running spreads with cummulative and marginal default probabilities
    PlotCdsTermStructure.plot_cds_term_structure(cds_term_structure.cds_tenors,
                                                 cds_term_structure.cds_deal_spreads,
                                                 cds_term_structure.cds_upfronts,
                                                 cds_term_structure.running_spreads,
                                                 cds_term_structure.hazard_rates,
                                                 cds_term_structure.times,
                                                 cds_term_structure.marginal_default_probabilities,
                                                 cds_term_structure.cumulative_default_probabilities)
'''


if __name__ == '__main__':
    main()

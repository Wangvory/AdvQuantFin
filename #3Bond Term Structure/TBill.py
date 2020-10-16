import math


class TBills(object):

    def __init__(self, name, issue_date, maturity_date):
        self._name = name
        self._issue_date = issue_date
        self._maturity_date = maturity_date
        self._tenor_in_days = int(self._maturity_date - self._issue_date) / 100.0 * 30
        self._price = 0.0
        self._face_value = 100.0

    @property
    def get_tenor_in_days(self):
        return self._tenor_in_days

    def get_name(self):
        return self._name

    def get_issue_date(self):
        return self._issue_date

    def get_maturity_date(self):
        return self._maturity_date

    def get_price(self):
        return self._price

    def get_spotrate(self):
        return (self._face_value-self._price)/self._price*100

    def set_price(self, price, face_value=100.0):
        self._price = price
        self._face_value = face_value

    @staticmethod
    def compute_price(face_value,tenor,ytm):
        price = face_value / (1 + ytm * tenor/360)
        return price

    def compute_ytm(self):
        """ Computes the bond yield-to-maturity via bisection method
        :return: yield to maturity
        """
        ytm, tolerance = 0.0, 0.0001
        a, b, c = 0.0, 100.0, 0.0

        while True:
            fa = self.compute_price(self._face_value, self._tenor_in_days, a / 100.0) \
                 - self._price / 100.0 * self._face_value
            fb = self.compute_price(self._face_value, self._tenor_in_days, b / 100.0) \
                 - self._price / 100.0 * self._face_value

            if math.fabs(fa) <= tolerance:
                ytm = a
                break
            elif math.fabs(fb) <= tolerance:
                ytm = b
                break
            elif fa * fb < 0.0:
                c = (a + b) / 2.0
                fc = self.compute_price(self._face_value,self._tenor_in_days, c / 100.0,) \
                     - self._price / 100.0 * self._face_value
                if math.fabs(fc) <= tolerance:
                    ytm = c
                    break
                if fa * fc < 0.0:
                    b = c
                else:
                    a = c
            else:
                print("Problem:  Lower and upper bounds of the starting range does not have a root.")
                return -1.0
        return ytm

    def bootstrap_spot_rate(self, spot_rates, index_tenor_start, index_tenor_end):
        ytm, tolerance = 0.0, 0.0001
        a, b, c = 0.0, 100.0, 0.0

        # setup working spot rates
        spot_rates_a, spot_rates_b, spot_rates_c = [], [], []
        for i in range(index_tenor_end + 1):
            spot_rates_a.append(0.0)
            spot_rates_b.append(0.0)
            spot_rates_c.append(0.0)

        while True:
            # copy known spot rates to working spot rates
            for i in range(index_tenor_start + 1):
                spot_rates_a[i] = spot_rates[i]
                spot_rates_b[i] = spot_rates[i]

            # set starting spot rates
            for i in range(index_tenor_start + 1, index_tenor_end + 1):
                spot_rates_a[i] = spot_rates[index_tenor_start] + \
                                  (a - spot_rates[index_tenor_start]) * (i - index_tenor_start) / \
                                  (index_tenor_end - index_tenor_start)
                spot_rates_b[i] = spot_rates[index_tenor_start] + \
                                  (b - spot_rates[index_tenor_start]) * (i - index_tenor_start) / \
                                  (index_tenor_end - index_tenor_start)

            for i in range(index_tenor_end + 1):
                spot_rates_a[i] = spot_rates_a[i] / 100.0
                spot_rates_b[i] = spot_rates_b[i] / 100.0

            fa = self.compute_price_from_spot(self._face_value,
                                              self._coupon / 100.0 / self._compounding_frequency,
                                              spot_rates_a,
                                              self._count_coupon_payments) - self._price / 100.0 * self._face_value
            fb = self.compute_price_from_spot(self._face_value,
                                              self._coupon / 100.0 / self._compounding_frequency,
                                              spot_rates_b,
                                              self._count_coupon_payments) - self._price / 100.0 * self._face_value

            if math.fabs(fa) <= tolerance:
                for i in range(index_tenor_start + 1, index_tenor_end + 1):
                    spot_rates[i] = spot_rates[index_tenor_start] + (a - spot_rates[index_tenor_start]) * \
                                    (i - index_tenor_start) / (index_tenor_end - index_tenor_start)
                break

            elif math.fabs(fb) <= tolerance:
                for i in range(index_tenor_start + 1, index_tenor_end + 1):
                    spot_rates[i] = spot_rates[index_tenor_start] + (b - spot_rates[index_tenor_start]) * \
                                    (i - index_tenor_start) / (index_tenor_end - index_tenor_start)
                break

            elif fa * fb < 0.0:
                c = (a + b) / 2.0

                for i in range(index_tenor_start + 1):
                    spot_rates_c[i] = spot_rates[i]

                for i in range(index_tenor_start + 1, index_tenor_end + 1):
                    spot_rates_c[i] = spot_rates[index_tenor_start] + (
                            c - spot_rates[index_tenor_start]) * \
                                      (i - index_tenor_start) / (
                                              index_tenor_end - index_tenor_start)

                for i in range(index_tenor_end + 1):
                    spot_rates_c[i] = spot_rates_c[i] / 100.0 / self._compounding_frequency

                fc = self.compute_price_from_spot(self._face_value,
                                                  self._coupon / 100.0 / self._compounding_frequency,
                                                  spot_rates_c,
                                                  self._count_coupon_payments) \
                     - self._price / 100.0 * self._face_value

                if math.fabs(fc) <= tolerance:
                    for i in range(index_tenor_start + 1, index_tenor_end + 1):
                        spot_rates[i] = spot_rates[index_tenor_start] + \
                                        (c - spot_rates[index_tenor_start]) * (i - index_tenor_start) / \
                                        (index_tenor_end - index_tenor_start)
                    break

                if fa * fc < 0.0:
                    b = c
                else:
                    a = c

            else:
                print("Problem:  Lower and upper bounds of the starting range does not have a root.")
                return -1.0

        return ytm

    @staticmethod
    def compute_price_from_spot(face_value, coupon , spot_rates, count_coupon_payments):
        price = 0.0
        for i in range(count_coupon_payments):
            price += coupon * face_value / math.pow(1.0 + spot_rates[i], i + 1)
        price += face_value / math.pow(1.0 + spot_rates[count_coupon_payments - 1], count_coupon_payments)
        return price

import math


class Bond(object):

    def __init__(self, name, coupon, issue_date, maturity_date, compounding_frequency_per_annum):
        self._name = name
        self._coupon = coupon
        self._issue_date = issue_date
        self._maturity_date = maturity_date
        self._compounding_frequency_per_annum = compounding_frequency_per_annum
        self._number_of_coupon_payments = 1 if (name == "6m") \
            else int((maturity_date - issue_date) / 10000 * compounding_frequency_per_annum)
        self._price = 0.0
        self._face_value = 1000.0

    def get_name(self):
        return self._name

    def get_coupon(self):
        return self._coupon

    def get_issue_date(self):
        return self._issue_date

    def get_maturity_date(self):
        return self._maturity_date

    def get_compounding_frequency_per_annum(self):
        return self._compounding_frequency_per_annum

    def get_price(self):
        return self._price

    def set_price(self, price, face_value=1000.0):
        self._price = price
        self._face_value = face_value

    @staticmethod
    def compute_price(face_value, coupon, ytm, number_of_coupon_payments):
        price = 0.0
        for i in range(number_of_coupon_payments):
            price += coupon * face_value / math.pow(1.0 + ytm, i + 1)
        price += face_value / math.pow(1.0 + ytm, number_of_coupon_payments)
        return price

    def compute_ytm(self):
        ytm, tolerance = 0.0, 0.0001
        a, b, c = 0.0, 100.0, 0.0

        while True:
            fa = self.compute_price(self._face_value, self._coupon / 100.0 / self._compounding_frequency_per_annum,
                                    a / 100.0 / self._compounding_frequency_per_annum, self._number_of_coupon_payments) \
                 - self._price / 100.0 * self._face_value
            fb = self.compute_price(self._face_value, self._coupon / 100.0 / self._compounding_frequency_per_annum,
                                    b / 100.0 / self._compounding_frequency_per_annum, self._number_of_coupon_payments) \
                 - self._price / 100.0 * self._face_value
            if math.fabs(fa) <= tolerance:
                ytm = a
                break
            elif math.fabs(fb) <= tolerance:
                ytm = b
                break
            elif fa * fb < 0.0:
                c = (a + b) / 2.0
                fc = self.compute_price(self._face_value, self._coupon / 100.0 / self._compounding_frequency_per_annum,
                                        c / 100.0 / self._compounding_frequency_per_annum,
                                        self._number_of_coupon_payments) \
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

    def bootstrap_spot_rate(self, spot_rates, interpolatedTenorStart, interpolatedTenorEnd):
        ytm, tolerance = 0.0, 0.0001
        a, b, c = 0.0, 100.0, 0.0

        spot_rates_a, spot_rates_b, spot_rates_c = [], [], []
        for i in range(20):
            spot_rates_a.append(0.0)
            spot_rates_b.append(0.0)
            spot_rates_c.append(0.0)

        while True:
            for i in range(interpolatedTenorStart + 1):
                spot_rates_a[i] = spot_rates[i]
                spot_rates_b[i] = spot_rates[i]

            for i in range(interpolatedTenorStart + 1, interpolatedTenorEnd + 1):
                spot_rates_a[i] = spot_rates[interpolatedTenorStart] + (
                        a - spot_rates[interpolatedTenorStart]) * (i - interpolatedTenorStart) / (
                                          interpolatedTenorEnd - interpolatedTenorStart)
                spot_rates_b[i] = spot_rates[interpolatedTenorStart] + (
                        b - spot_rates[interpolatedTenorStart]) * (i - interpolatedTenorStart) / (
                                          interpolatedTenorEnd - interpolatedTenorStart)

            for i in range(len(spot_rates)):
                spot_rates_a[i] = spot_rates_a[i] / 100.0 / self._compounding_frequency_per_annum
                spot_rates_b[i] = spot_rates_b[i] / 100.0 / self._compounding_frequency_per_annum

            fa = self.compute_price_from_spot(self._face_value,
                                              self._coupon / 100.0 / self._compounding_frequency_per_annum,
                                              spot_rates_a,
                                              self._number_of_coupon_payments) - self._price / 100.0 * self._face_value
            fb = self.compute_price_from_spot(self._face_value,
                                              self._coupon / 100.0 / self._compounding_frequency_per_annum,
                                              spot_rates_b,
                                              self._number_of_coupon_payments) - self._price / 100.0 * self._face_value

            if math.fabs(fa) <= tolerance:
                for i in range(interpolatedTenorStart + 1, interpolatedTenorEnd + 1):
                    spot_rates[i] = spot_rates[interpolatedTenorStart] + (a - spot_rates[interpolatedTenorStart]) * (
                            i - interpolatedTenorStart) / (interpolatedTenorEnd - interpolatedTenorStart)
                break

            elif math.fabs(fb) <= tolerance:
                for i in range(interpolatedTenorStart + 1, interpolatedTenorEnd + 1):
                    spot_rates[i] = spot_rates[interpolatedTenorStart] + (b - spot_rates[interpolatedTenorStart]) * (
                            i - interpolatedTenorStart) / (interpolatedTenorEnd - interpolatedTenorStart)
                break

            elif fa * fb < 0.0:
                c = (a + b) / 2.0

                for i in range(interpolatedTenorStart + 1):
                    spot_rates_c[i] = spot_rates[i]

                for i in range(interpolatedTenorStart + 1, interpolatedTenorEnd + 1):
                    spot_rates_c[i] = spot_rates[interpolatedTenorStart] + (c - spot_rates[interpolatedTenorStart]) * (
                            i - interpolatedTenorStart) / (interpolatedTenorEnd - interpolatedTenorStart)

                for i in range(len(spot_rates)):
                    spot_rates_c[i] = spot_rates_c[i] / 100.0 / self._compounding_frequency_per_annum

                fc = self.compute_price_from_spot(self._face_value,
                                                  self._coupon / 100.0 / self._compounding_frequency_per_annum,
                                                  spot_rates_c,
                                                  self._number_of_coupon_payments) - self._price / 100.0 * self._face_value

                if math.fabs(fc) <= tolerance:
                    for i in range(interpolatedTenorStart + 1, interpolatedTenorEnd + 1):
                        spot_rates[i] = spot_rates[interpolatedTenorStart] + (
                                c - spot_rates[interpolatedTenorStart]) * (i - interpolatedTenorStart) / (
                                                interpolatedTenorEnd - interpolatedTenorStart)
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
    def compute_price_from_spot(face_value, coupon, spot_rates, number_of_coupon_payments):
        price = 0.0
        for i in range(number_of_coupon_payments):
            price += coupon * face_value / math.pow(1.0 + spot_rates[i], i + 1)
        price += face_value / math.pow(1.0 + spot_rates[number_of_coupon_payments - 1], number_of_coupon_payments)
        return price

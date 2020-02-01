import math


def compute_future_value(notional, interest_rate, compounding_frequency, tenor):
    if compounding_frequency == math.inf:
        return notional * math.exp(interest_rate * tenor)
    else:
        return notional * math.pow(1.0 + interest_rate / compounding_frequency, compounding_frequency * tenor)


def main():
    notional = 100.0
    interest_rate = 5.0
    compounding_frequencys = [1, 2, 4, 6, 12, 24, 48, 96, 128, 256, 365, math.inf]
    tenor = 2.0

    for compounding_frequency in compounding_frequencys:
        future_value = compute_future_value(notional, interest_rate / 100.0, compounding_frequency, tenor)
        print(compounding_frequency, round(future_value, 8))


if __name__ == '__main__':
    main()

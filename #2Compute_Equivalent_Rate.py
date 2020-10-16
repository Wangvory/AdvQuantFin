import math


def compute_equivalent_rate(interest_rate, compounding_frequency):
    if compounding_frequency == math.inf:
        return interest_rate
    else:
        return compounding_frequency * (math.exp(interest_rate / compounding_frequency) - 1.0)


def main():
    interest_rate = 4.879  # continuous compounding
    compounding_frequencys = [1, 2, 4, 6, 12, 24, 48, 96, 128, 256, 365, math.inf]

    for compounding_frequency in compounding_frequencys:
        interest_rate_compounded = compute_equivalent_rate(interest_rate / 100.0, compounding_frequency)
        print(compounding_frequency, round(100 * interest_rate_compounded, 4))


if __name__ == '__main__':
    main()

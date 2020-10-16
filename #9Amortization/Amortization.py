from prettytable import PrettyTable


def print_to_table(schedule):
    x = PrettyTable()
    x.field_names = ['Payment Number', 'Begin Principal', 'Payment', 'Extra Payment',
                     'Applied Principal', 'Applied Interest', 'End Principal']
    for field_name in x.field_names:
        x.align[field_name] = "r"
    for _ in schedule.values():
        x.add_row([round(_[0], 2), round(_[1], 2), round(_[2], 2),
                   round(_[3], 2), round(_[4], 2), round(_[5], 2), round(_[6], 2)])
    print(x)


def compute_schedule(principal, rate, min_payment, extra_payment):
    begin_principal = principal
    payment = min_payment
    payment_number = 0
    schedule = {}
    while begin_principal > 0.0:
        payment_number += 1
        applied_interest = begin_principal * rate / 12.0 / 100.0
        applied_principal = payment - applied_interest + extra_payment
        if applied_principal > begin_principal:
            payment = begin_principal + applied_interest
            extra_payment = 0.0
            applied_principal = payment - applied_interest + extra_payment
        end_principal = begin_principal - applied_principal
        schedule[payment_number] = (payment_number, begin_principal, payment,
                                    extra_payment, applied_principal, applied_interest, end_principal)
        begin_principal = end_principal
    return schedule


def main():
    print('Please enter the following items:')
    principal = float(input('Principal? '))
    rate = float(input('Rate? '))
    min_payment = float(input('Expected Minimum Payment? '))
    extra_payment = float(input('Extra Payment? '))

    schedule = compute_schedule(principal, rate, min_payment, extra_payment)
    print_to_table(schedule)


if __name__ == '__main__':
    main()

# Copyright (c) 2023 SPMontreal

# Imports:

import numpy_financial as npf

# Functions:

def mortgage_payment(r, l, a):
    """
    r: float, annual interest rate, in percent
    l: float, total loan amount, in dollars
    a: int, amortization in years
    returns: p (float), the monthly mortgage payment in dollars
    """
    biann_r = 1 + r/200
    month_r = biann_r**(1/6)
    p = -npf.pmt(month_r - 1, a*12, l)
    return p

def princ_calc(y, l, r, p):
    """
    y: int, the term period in years
    l: float, loan amount, in dollars
    r: float, annual interest rate, in percent
    p: float, the monthly mortgage payment in dollars
    returns: princ_paid (float), the amount of principal paid off over the
        life of the contract, in dollars
    """
    biann_r = 1 + r/200
    month_r = biann_r**(1/6)
    months_remaining = y*12
    l_remaining = l
    princ_paid = 0
    while months_remaining > 0:
        princ_paid_month = p - l_remaining*(month_r - 1)
        princ_paid += princ_paid_month
        l_remaining -= princ_paid_month
        months_remaining -= 1
    return princ_paid

def cmhc_insurance(l, d, prov):
    """
    l: float, loan amount, in dollars
    d: float, down payment amount, in dollars
    prov: string, province of purchase
    returns:
        - ins (float), the CMHC mortgage insurance cost over the initial term,
            in dollars
        - ins_tax (float), the tax paid on the CMHC mortgage insurance, in
            dollars
    """
    ltv = l/(l + d)
    if ltv <= 0.65:
        ins = 0.006*l
    elif ltv <= 0.75:
        ins = 0.017*l
    else:
        ins = 0.024*l
    ins_tax = 0
    prov_l = prov.lower()
    if prov_l == 'quebec':
        ins_tax = ins*0.09975
    elif prov_l == 'ontario':
        ins_tax = ins*0.13
    elif prov_l == 'saskatchewan':
        ins_tax = ins*0.06
    return ins, ins_tax

def cost_over_term(y, l, tot, insured, a, is_init):
    """
    y: int, the term period in years
    l: float, loan amount, in dollars
    tot: float, purchase price, in dollars
    ins_purchased: Boolean, True if mortgage insurance is being purchased with
        this loan contract
    insured: Boolean, True if the mortgage loan is insured
    a: int, amortization in years
    is_init: Boolean, True if this is the initial term
    returns:
        - term_cost (float), the total mortgage cost over the life of the
            contract, in dollars
        - princ_paid (float), the amount of principal paid off over the life
            of the contract, in dollars
    """
    if insured:
        if is_init:
            r = r_ins_init
        else:
            r = r_ins
    else:
        if is_init:
            r = r_un_init
        else:
            ltv = l/tot
            if ltv <= 0.65:
                r = r_un_65
            elif ltv <= 0.70:
                r = r_un_70
            elif ltv <= 0.75:
                r = r_un_75
            else:
                r = r_un_80
    p = mortgage_payment(r, l, a)
    term_cost = y*12*p
    princ_paid = princ_calc(y, l, r, p)
    return term_cost, princ_paid

def cost_over_mortgage(y, l, tot, insured, a):
    """
    y: int, the term period in years
    l: float, loan amount, in dollars
    tot: float, purchase price, in dollars
    insured: Boolean, True if mortgage insurance is purchased when the loan is
        first taken
    a: int, amortization in years
    returns: tot_cost (float), the total mortgage cost over all terms, in
        dollars
    """
    a_remaining = a
    l_remaining = l
    tot_cost = 0
    if insured:
        ins, ins_tax = cmhc_insurance(l, (tot - l), prov)
        l_remaining += ins
        tot_cost += ins_tax
    term_cost, princ_paid = cost_over_term(y, l_remaining, tot, insured,
                                           a_remaining, True)
    tot_cost += term_cost
    a_remaining -= y
    l_remaining -= princ_paid
    while a_remaining >= y:
        term_cost, princ_paid = cost_over_term(y, l_remaining, tot, insured,
                                               a_remaining, False)
        tot_cost += term_cost
        a_remaining -= y
        l_remaining -= princ_paid
    tot_cost += l_remaining
    return tot_cost

# Main:
    
tot = float(input("Please enter the purchase price ($): "))
d = float(input("\nPlease enter the down payment ($): "))
a = int(input("\nPlease enter the initial amortization period, in years: "))
if tot >= 1000000:
    print("\nThe house is not eligible for mortgage insurance since it costs",
          "$1 million or more.")
elif d/tot < 0.2:
    print("\nSince your down payment is less than 20%, you will need to get",
          "mortgage insurance.")
elif a > 25:
    print("\nInsured mortgages cannot have amortizations longer than 25",
          "years.")
else:
    l = tot - d
    prov = input("\nProvince where property is located (omit accents): ")
    r_ins_init = float(input("\nInitial interest rate if insured (%): "))
    r_un_init = float(input("\nInitial interest rate if uninsured (%): "))
    r_ins = float(input("\nEstimated future interest rate if insured (%): "))
    print("\nEstimated future interest rate if uninsured...")
    r_un_80 = float(input("...75-80% LTV (%): "))
    r_un_75 = float(input("...70-75% LTV (%): "))
    r_un_70 = float(input("...65-70% LTV (%): "))
    r_un_65 = float(input("...0-65% LTV (%): "))
    y = int(input("\nPlease enter the term period, in years: "))
    tot_cost_ins = cost_over_mortgage(y, l, tot, True, a)
    print("\nThe total cost of the insured mortgage is: $"
          + str(round(tot_cost_ins, 2)))
    tot_cost_un = cost_over_mortgage(y, l, tot, False, a)
    print("\nThe total cost of the uninsured mortgage is: $"
          + str(round(tot_cost_un, 2)))
    if tot_cost_ins < tot_cost_un:
        print("\nThe insured mortgage is less expensive.")
    elif tot_cost_un < tot_cost_ins:
        print("\nThe uninsured mortgage is less expensive.")
    else:
        print("\nBoth options have the same overall cost.")
    diff = str(round(abs(tot_cost_un - tot_cost_ins), 2))
    print("\nThe cost difference over the life of the loan is: $" + diff)

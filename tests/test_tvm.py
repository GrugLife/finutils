import math

from finutils.tvm import present_value, future_value, payment, rate


def test_present_value_lump_sum():
    # Excel: =PV(0.05, 10, 0, 1000) -> -613.91
    pv = present_value(0.05, 10, payment=0, future_value=1000)
    assert round(pv, 2) == -613.91


def test_future_value_lump_sum():
    # Excel: =FV(0.05, 10, 0, -1000) -> 1628.89
    fv = future_value(0.05, 10, payment=0, present_value=-1000)
    assert round(fv, 2) == 1628.89


def test_payment_standard_loan():
    # Excel: =PMT(0.05, 10, 1000, 0) -> -129.50
    pmt = payment(0.05, 10, present_value=1000, future_value=0)
    assert round(pmt, 2) == -129.5


def test_rate_simple_case():
    # For a loan with PV=1000, n=10, payments ~ -129.5, rate ~ 5%
    r = rate(10, payment=-129.5, present_value=1000, future_value=0, guess=0.05)
    assert math.isclose(r, 0.05, rel_tol=1e-4)
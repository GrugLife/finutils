import math
from datetime import date

from finutils import present_value, future_value, payment, rate, npv, npv, irr, xnpv, xirr


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


def test_npv_simple():
    # Excel: =NPV(0.10, 300,400,500) - 1000 = -37.22
    assert npv(0.10, [300,400,500], 1000) == -37.22


def test_npv_zero_rate():
    assert npv(0.0, [100,100,100], 250) == 50.00


def test_npv_simple():
    # Cashflows: -1000 now, then +300, +420, +680
    # Excel: =IRR({-1000,300,420,680}) ≈ 0.2489
    cfs = [-1000, 300, 420, 680]
    r = 0.10
    v = npv(r, cfs)

    # Just a sanity check: NPV at 10% should be positive
    assert v > 0


def test_irr_example():
    # Example: -1000 now, then +300, +420, +680
    cfs = [-1000, 300, 420, 680]
    r = irr(cfs)
    # Excel IRR for this series ≈ 0.2489 (24.89%)
    assert math.isclose(r, 0.2489, rel_tol=1e-3)


def test_xnpv_and_xirr():
    # Simple date-based cashflow example
    cashflows = [-1000, 300, 400, 500]
    dates = [
        date(2020, 1, 1),
        date(2020, 6, 30),
        date(2021, 1, 1),
        date(2021, 12, 31),
    ]

    r = 0.10
    v = xnpv(r, cashflows, dates)
    # Just sanity check: NPV should be finite
    assert isinstance(v, float)

    xr = xirr(cashflows, dates)
    # IRR should be reasonable (0 < r < 1)
    assert 0.0 < xr < 1.0
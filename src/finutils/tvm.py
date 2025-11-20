"""
tvm.py — Time Value of Money & Cashflow Utilities (Excel-ish)

Implements:
- present_value  -> PV
- future_value   -> FV
- payment        -> PMT
- rate           -> RATE
- npv            -> NPV (standard, includes CF0)
- xnpv           -> XNPV (date-based)
- irr            -> IRR
- xirr           -> XIRR (date-based)
"""

from __future__ import annotations

from datetime import date
from typing import Literal, Sequence


When = Literal[0, 1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_when(when: int) -> None:
    if when not in (0, 1):
        raise ValueError("`when` must be 0 (end of period) or 1 (beginning of period).")


# ---------------------------------------------------------------------------
# Classic TVM functions: PV, FV, PMT, RATE
# ---------------------------------------------------------------------------

def present_value(
    rate: float,
    n_periods: int,
    payment: float = 0.0,
    future_value: float = 0.0,
    when: When = 0,
) -> float:
    """
    Compute the present value of a series of cash flows or lump sum.

    Mirrors Excel's: PV(rate, nper, pmt, fv, type)
    """
    _validate_when(when)

    if n_periods < 0:
        raise ValueError("n_periods must be non-negative.")

    if rate == 0:
        return round(-(payment * n_periods + future_value), 2)

    pv_factor = (1 - (1 + rate) ** (-n_periods)) / rate

    pv = -(
        payment * (1 + rate * when) * pv_factor
        + future_value * (1 + rate) ** (-n_periods)
    )

    return round(pv, 2)


def future_value(
    rate: float,
    n_periods: int,
    payment: float = 0.0,
    present_value: float = 0.0,
    when: When = 0,
) -> float:
    """
    Compute the future value of a series of cash flows or lump sum.

    Mirrors Excel's: FV(rate, nper, pmt, pv, type)
    """
    _validate_when(when)

    if n_periods < 0:
        raise ValueError("n_periods must be non-negative.")

    if rate == 0:
        return round(-(present_value + payment * n_periods), 2)

    fv_factor = ((1 + rate) ** n_periods - 1) / rate

    fv = -(
        present_value * (1 + rate) ** n_periods
        + payment * (1 + rate * when) * fv_factor
    )

    return round(fv, 2)


def payment(
    rate: float,
    n_periods: int,
    present_value: float = 0.0,
    future_value: float = 0.0,
    when: When = 0,
) -> float:
    """
    Compute the constant payment per period.

    Mirrors Excel's: PMT(rate, nper, pv, fv, type)
    """
    _validate_when(when)

    if n_periods <= 0:
        raise ValueError("n_periods must be positive.")

    if rate == 0:
        return round(-(present_value + future_value) / n_periods, 2)

    r1 = 1 + rate
    r1n = r1 ** n_periods

    numerator = rate * (present_value * r1n + future_value)
    denominator = (1 + rate * when) * (r1n - 1)

    pmt = -numerator / denominator

    return round(pmt, 2)


def rate(
    n_periods: int,
    payment: float = 0.0,
    present_value: float = 0.0,
    future_value: float = 0.0,
    when: When = 0,
    guess: float = 0.1,
    tol: float = 1e-7,
    max_iter: int = 100,
) -> float:
    """
    Solve for the interest rate per period that satisfies the TVM equation.

    Roughly mirrors Excel's: RATE(nper, pmt, pv, fv, type, guess)
    """
    _validate_when(when)

    if n_periods <= 0:
        raise ValueError("n_periods must be positive.")

    def f(r: float) -> float:
        if r == 0:
            return present_value + payment * n_periods + future_value

        r1 = 1 + r
        r1n = r1 ** n_periods
        return (
            present_value * r1n
            + payment * (1 + r * when) * (r1n - 1) / r
            + future_value
        )

    r = guess
    for _ in range(max_iter):
        y = f(r)
        if abs(y) < tol:
            return r

        h = 1e-6
        y_h = f(r + h)
        dy = (y_h - y) / h
        if dy == 0:
            break

        r -= y / dy

    raise ValueError("Failed to converge to a solution for rate.")


# ---------------------------------------------------------------------------
# Cashflow-based functions: NPV, XNPV, IRR, XIRR
# ---------------------------------------------------------------------------

def npv(rate: float, cashflows: Sequence[float]) -> float:
    """
    Net Present Value of a series of cash flows including time 0.

    NPV(rate, [CF0, CF1, ..., CFn]) = Σ CF_t / (1 + rate)^t, t = 0..n
    """
    if rate == -1:
        raise ValueError("rate = -1 would cause division by zero")

    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def xnpv(rate: float, cashflows: Sequence[float], dates: Sequence[date]) -> float:
    """
    Date-based NPV (Excel-style XNPV).

    Discounts each cash flow based on its exact day difference
    from the first cash flow.
    """
    if len(cashflows) != len(dates):
        raise ValueError("cashflows and dates must have the same length")

    if len(cashflows) == 0:
        return 0.0

    t0 = dates[0]

    return sum(
        cf / (1 + rate) ** ((d - t0).days / 365.0)
        for cf, d in zip(cashflows, dates)
    )


def irr(
    cashflows: Sequence[float],
    guess: float = 0.1,
    tol: float = 1e-7,
    max_iter: int = 100,
) -> float:
    """
    Internal Rate of Return (IRR) for a series of cash flows.

    Solves for r such that:
        0 = Σ CF_t / (1 + r)^t,  t = 0..n
    """
    def f(r: float) -> float:
        return npv(r, cashflows)

    r = guess
    for _ in range(max_iter):
        y = f(r)
        if abs(y) < tol:
            return r

        h = 1e-6
        y_h = f(r + h)
        dy = (y_h - y) / h
        if dy == 0:
            break

        r -= y / dy

    raise ValueError("IRR did not converge")


def xirr(
    cashflows: Sequence[float],
    dates: Sequence[date],
    guess: float = 0.1,
    tol: float = 1e-7,
    max_iter: int = 100,
) -> float:
    """
    Date-based IRR (Excel-style XIRR).

    Solves for r such that:
        0 = Σ CF_i / (1 + r)^((t_i - t0)/365)
    """
    if len(cashflows) != len(dates):
        raise ValueError("cashflows and dates must have the same length")

    if len(cashflows) == 0:
        raise ValueError("cashflows must not be empty")

    def f(r: float) -> float:
        return xnpv(r, cashflows, dates)

    r = guess
    for _ in range(max_iter):
        y = f(r)
        if abs(y) < tol:
            return r

        h = 1e-6
        y_h = f(r + h)
        dy = (y_h - y) / h
        if dy == 0:
            break

        r -= y / dy

    raise ValueError("XIRR did not converge")
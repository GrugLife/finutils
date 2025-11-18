"""
tvm.py — Time Value of Money utilities (Excel-compatible)

Implements:
- present_value  -> PV
- future_value   -> FV
- payment        -> PMT
- rate           -> RATE
"""

from __future__ import annotations

from typing import Literal


When = Literal[0, 1]


def _validate_when(when: int) -> None:
    if when not in (0, 1):
        raise ValueError("`when` must be 0 (end of period) or 1 (beginning of period).")


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

    Parameters
    ----------
    rate : float
        Discount rate per period as a decimal (e.g., 0.05 for 5%).
    n_periods : int
        Number of periods.
    payment : float, default 0.0
        Payment made each period (PMT). Use negative for outflows,
        positive for inflows.
    future_value : float, default 0.0
        Future lump sum (FV).
    when : {0, 1}, default 0
        0 = end of period (ordinary annuity)
        1 = beginning of period (annuity due)

    Returns
    -------
    float
        Present value (PV). By convention, will usually be the opposite sign
        of payment / future_value.
    """
    _validate_when(when)

    if n_periods < 0:
        raise ValueError("n_periods must be non-negative.")

    if rate == 0:
        # PV is just the negative sum of all cash flows
        return round(-(payment * n_periods + future_value), 2)

    # PV factor for an annuity
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

    Parameters
    ----------
    rate : float
        Interest rate per period as a decimal (e.g., 0.05 for 5%).
    n_periods : int
        Number of periods.
    payment : float, default 0.0
        Payment made each period (PMT). Negative for deposits, positive for withdrawals.
    present_value : float, default 0.0
        Present value (PV). Negative for an amount you invest today.
    when : {0, 1}, default 0
        0 = end of period (ordinary annuity)
        1 = beginning of period (annuity due)

    Returns
    -------
    float
        Future value (FV).
    """
    _validate_when(when)

    if n_periods < 0:
        raise ValueError("n_periods must be non-negative.")

    if rate == 0:
        # FV is just negative of total cashflow sum
        return round(-(present_value + payment * n_periods), 2)

    # FV factor for an annuity
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

    Parameters
    ----------
    rate : float
        Interest rate per period as a decimal.
    n_periods : int
        Number of periods.
    present_value : float, default 0.0
        Present value (PV). Positive if you receive money today.
    future_value : float, default 0.0
        Future value (FV). Positive if you want to have that amount at the end.
    when : {0, 1}, default 0
        0 = end of period (ordinary annuity)
        1 = beginning of period (annuity due)

    Returns
    -------
    float
        Payment per period (PMT). Usually negative if PV is positive
        (e.g., loan repayment).
    """
    _validate_when(when)

    if n_periods <= 0:
        raise ValueError("n_periods must be positive.")

    if rate == 0:
        # Simple straight-line repayment
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

    Uses a simple Newton-Raphson method with a finite-difference derivative.

    Parameters
    ----------
    n_periods : int
        Number of periods (nper).
    payment : float, default 0.0
        Payment made each period (PMT).
    present_value : float, default 0.0
        Present value (PV).
    future_value : float, default 0.0
        Future value (FV).
    when : {0, 1}, default 0
        0 = end of period, 1 = beginning of period.
    guess : float, default 0.1
        Initial guess for the rate (as a decimal).
    tol : float, default 1e-7
        Convergence tolerance for the solution.
    max_iter : int, default 100
        Maximum number of iterations.

    Returns
    -------
    float
        Solved interest rate per period as a decimal.

    Raises
    ------
    ValueError
        If it fails to converge.
    """
    _validate_when(when)

    if n_periods <= 0:
        raise ValueError("n_periods must be positive.")

    def f(r: float) -> float:
        # TVM equation set to zero:
        # pv*(1+r)^n + pmt*(1+r*when)*((1+r)^n - 1)/r + fv = 0
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

        # Finite difference derivative
        h = 1e-6
        y_h = f(r + h)
        dy = (y_h - y) / h
        if dy == 0:
            break

        r -= y / dy

    raise ValueError("Failed to converge to a solution for rate.")
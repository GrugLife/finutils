import pandas as pd
import numpy as np

def present_value(rate, n_periods, payment=0, future_value=0, when=0):
    """
    Computes the present value of an annuity or lump sum

    Parameters
    ----------
    rate : float
        Discount rate per period (e.g., 0.05 for 5%)

    n_periods : int
        Number of periods

    payment : float
        Payment made each period (PMT)

    future_value : float
        Future lump sum (FV)

    when : {0, 1}
        0 = end of period (ordinary annuity)
        1 = beginning of period (annuity due)

    Returns
    -------
    present_value : float
        Present value of investment
    """
    if rate == 0:
        return -(payment * n_periods + future_value)
    
    pv_factor = (1 - (1 + rate) ** (-n_periods)) / rate
    present_value = -(payment * (1 + rate * when) * pv_factor + future_value * (1+ rate) ** (-n_periods))
    return round(present_value, 2)

print(present_value(rate=0.08, n_periods=5, future_value=1000))
print(present_value(rate=0.06, n_periods=10, payment=100, when=1))
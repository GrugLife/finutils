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


def future_value(rate, n_periods, payment=0, present_value=0, when=0):
    """ 
    Computes the future value of an annuity or lump sum

    Parameters
    ----------
    rate : float
        Discount rate per period (e.g., 0.05 for 5%)

    n_periods : int
        Number of periods

    payment : float
        Payment made each period (PMT)

    present_value : float
        Present lump sum (PV)

    when : {0, 1}
        0 = end of period (ordinary annuity)
        1 = beginning of period (annuity due)

    Returns
    -------
    future_value : float
        Future value of investment
    """

    if rate == 0:
        return present_value + n_periods * payment
    
    fv_factor = ((1 + rate) ** n_periods -1) / rate
    future_value = (-(present_value * (1 + rate) ** n_periods) - payment * (1 + rate * when) * fv_factor)
    return round(future_value, 2)
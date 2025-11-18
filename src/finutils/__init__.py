"""
finutils

A small collection of finance utilities:
 - Time Value of Money (tvm)
 - (future: npv/xirr, amortization, etc.)
"""

from .tvm import present_value, future_value, payment, rate

__all__ = ["present_value", "future_value", "payment", "rate"]
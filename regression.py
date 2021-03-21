"""Holds all regression methods

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
from typing import List, Tuple

import python_ta


class Regression:
    """Stores all regression methods"""

    @staticmethod
    def linear_regression(x_values: List[float], y_values: List[float]) -> Tuple[float, float]:
        """Return the line of best fit

        preconditions:
            - len(x_values) == len(y_values)
            - len(x_values) != 0
            - len(y_values) != 0
        """
        n = len(x_values)

        x_mean = Regression.mean(x_values)
        y_mean = Regression.mean(y_values)
        numerator = 0
        denominator = 0
        for i in range(n):
            numerator += (x_values[i] - x_mean) * (y_values[i] - y_mean)
            denominator += (x_values[i] - x_mean) ** 2

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        return (slope, intercept)

    @staticmethod
    def strength_of_correlation(slope: float, intercept: float,
                                x_values: List[float], y_values: List[float]) -> float:
        """Finds the strength of correlation, R^2, of a linear model

        preconditions:
            - len(x_values) == len(y_values)
            - len(x_values) != 0
            - len(y_values) != 0
        """
        y_mean = Regression.mean(y_values)
        s_tot = 0
        s_res = 0
        for i in range(len(y_values)):
            s_tot += (y_values[i] - y_mean) ** 2
            s_res += (y_values[i] - (intercept + slope * x_values[i])) ** 2

        return 1 - s_res / s_tot

    @staticmethod
    def mean(values: List[float]) -> float:
        """Returns the mean of a list of values

        preconditions:
            - len(values) != 0
        """
        return sum(values) / len(values)


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()

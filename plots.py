"""Holds all methods needed to display correlations for the correlation displayer menu

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
from typing import Dict, List, Tuple

import python_ta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from regions import Region
from regression import Regression


class Plots:
    """Holds methods for plotting the correlations between variables"""
    @staticmethod
    def in_region_over_time(region: Region, y_var: str) -> None:
        """Create a plot looking at a variable over time within a region"""
        x_values = {year: year for year in range(1951, 2017)}
        y_values = getattr(region, y_var)

        cleaned_x_values, cleaned_y_values = Plots.clean_time_data(x_values, y_values)

        # will not display anything if there is no data to display
        if len(cleaned_x_values) != 0 and len(cleaned_y_values) != 0:
            Plots.linear_plot(cleaned_x_values, cleaned_y_values,
                              "year", y_var, region_name=region.name)

    @staticmethod
    def in_region(region: Region, x_var: str, y_var: str) -> None:
        """Create a plot comparing two variables within a region every year"""
        x_values = getattr(region, x_var)
        y_values = getattr(region, y_var)

        cleaned_x_values, cleaned_y_values = Plots.clean_time_data(x_values, y_values)

        # will not display anything if there is no data to display
        if len(cleaned_x_values) != 0 and len(cleaned_y_values) != 0:
            Plots.linear_plot(cleaned_x_values, cleaned_y_values,
                              x_var, y_var, region_name=region.name)

    @staticmethod
    def all_regions_over_time(regions: Dict[str, Region], y_var: str) -> None:
        """Create a plot looking at a variable over time over all regions"""
        x_values = {year: year for year in range(1951, 2017)}
        y_values = Plots.average_all_regions_over_time(regions, y_var)

        cleaned_x_values, cleaned_y_values = Plots.clean_time_data(x_values, y_values)

        # will not display anything if there is no data to display
        if len(cleaned_x_values) != 0 and len(cleaned_y_values) != 0:
            Plots.linear_plot(cleaned_x_values, cleaned_y_values, "year", y_var)

    @staticmethod
    def all_regions(regions: Dict[str, Region], x_var: str, y_var: str) -> None:
        """Create a plot comparing two variables within all region

        Takes the most recent data point in the data set."""
        x_values, y_values = Plots.final_over_all_regions(regions, x_var, y_var)

        Plots.linear_plot(x_values, y_values, x_var, y_var)

    @staticmethod
    def average_all_regions_over_time(regions: Dict[str, Region], var: str) \
            -> Dict[int, float]:
        """Average a result over all regions"""
        values = {key: None for key in range(1951, 2017)}

        for year in range(1951, 2017):
            total = 0
            amount = 0

            for region in regions:
                val = getattr(regions[region], var)[year]
                if val is not None:
                    total += val
                    amount += 1

            if amount == 0:
                values[year] = None
            else:
                values[year] = total / amount

        return values

    @staticmethod
    def final_over_all_regions(regions: Dict[str, Region], x_var: str, y_var: str) \
            -> Tuple[List[float], List[float]]:
        """Takes the most recent pair of values from all regions"""
        x_values = []
        y_values = []
        for region in regions:
            x_val = getattr(regions[region], x_var)[2016]
            y_val = getattr(regions[region], y_var)[2016]
            if x_val is not None and y_val is not None:
                x_values.append(x_val)
                y_values.append(y_val)
        return x_values, y_values

    @staticmethod
    def clean_time_data(x_values: Dict[int, float], y_values: Dict[int, float]) \
            -> Tuple[List[float], List[float]]:
        """Remove all None values from a dict of data over time and
        turn it into a list
        """
        cleaned_x_values = []
        cleaned_y_values = []
        for year in range(1951, 2017):
            if x_values[year] is not None and y_values[year] is not None:
                cleaned_x_values.append(x_values[year])
                cleaned_y_values.append(y_values[year])
        return cleaned_x_values, cleaned_y_values

    @staticmethod
    def linear_plot(x_values: List[float], y_values: List[float], x_var: str,
                    y_var: str, region_name: str = "Global") -> None:
        """Plot two list of values, uses a linear regression
        """
        slope, intercept = Regression.linear_regression(x_values, y_values)
        r_squared = Regression.strength_of_correlation(slope, intercept, x_values, y_values)

        t = np.linspace(min(x_values), max(x_values), 100)

        title = region_name + ": slope = " + str(round(slope, 2)) + \
            ", intercept = " + str(round(intercept, 2)) + ", R^2 = " + str(round(r_squared, 2))

        fig = px.line(x=t, y=slope * t + intercept, labels={'x': x_var, 'y': y_var}, title=title)
        fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='markers'))
        fig.show()


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()

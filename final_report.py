"""Creates the interesting correlations to be displayed in the final report

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
from typing import Dict, List

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import python_ta

from dataset import DataSet
from twitter import TweetAnalyser
from regions import Region
from regression import Regression


class FinalReport:
    """Holds all the methods for analysing the data set in more detail, and in more interesting ways

    Instance Attributes:
        - data_set: holds the DataSet used
        - tweets: holds the tweets gathered
        - regions: holds the list of regions in data_set
    """

    data_set: DataSet
    tweets: List[dict]
    regions: Dict[str, Region]

    def __init__(self, data_set: DataSet) -> None:
        self.data_set = data_set
        self.tweets = data_set.tweets
        self.regions = self.data_set.regions

    # menu 0
    def most_common_days(self) -> str:
        """Return a string listing the most common days for climate change related tweets"""
        common_days = TweetAnalyser.common_times(self.tweets)
        return ', '.join([str(day[0]) for day in common_days])

    def average_score_of_state(self, state_name: str, state_abbreviation: str) -> float:
        """Return the average tweet denial in the state

        preconditions:
            - state_name.is_lower()
            - state_abbreviation.is_upper()
        """
        score0, total0 = TweetAnalyser.location_score(self.tweets, state_name, False)
        score1, total1 = TweetAnalyser.location_score(self.tweets, state_abbreviation, True)
        return (score0 + score1) / (total0 + total1)

    def compare_selected_locations(self) -> None:
        """Compares the tweet score of the top 10 highest population US states"""
        states = [("california", "CA"),
                  ("texas", "TX"),
                  ("florida", "FL"),
                  ("new york", "NY"),
                  ("pennsylvania", "PA"),
                  ("illinois", "IL"),
                  ("ohio", "OH"),
                  ("georgia", "GA"),
                  ("north carolina", "NC"),
                  ("michigan", "MI")]

        states_score = []
        for state in states:
            states_score.append(self.average_score_of_state(state[0], state[1]))

        # Fix states to display in table
        states = [state[0].title() for state in states]

        title0 = "State"
        title1 = "Average Amount of Climate Change Denial in Tweets"
        fig = go.Figure(data=[go.Table(header=dict(values=[title0, title1]),
                                       cells=dict(values=[states, states_score]))
                              ])
        fig.show()

    def denial_and_emissions(self) -> None:
        """Display plots showing the relationship between denial and emissions"""
        x0_values = []
        x1_values = []
        y0_values = []
        y1_values = []
        for region in self.regions:
            concerned = self.regions[region].percentage_concerned
            if concerned is not None:
                emissions = self.regions[region].co2_emissions[2016]
                emissions_per_capita = self.regions[region].co2_emissions_per_capita[2016]
                if emissions is not None:
                    x0_values.append(concerned)
                    y0_values.append(emissions)
                if emissions_per_capita is not None:
                    x1_values.append(concerned)
                    y1_values.append(emissions_per_capita)

        slope0, intercept0 = Regression.linear_regression(x0_values, y0_values)
        slope1, intercept1 = Regression.linear_regression(x1_values, y1_values)

        r_squared0 = Regression.strength_of_correlation(slope0, intercept0, x0_values, y0_values)
        r_squared1 = Regression.strength_of_correlation(slope1, intercept1, x1_values, y1_values)

        t = np.linspace(0, 100, 100)

        title0 = "slope = " + str(round(slope0, 2)) + \
                 ", intercept = " + str(round(intercept0, 2)) + \
                 ", R^2 = " + str(round(r_squared0, 2))
        title1 = "slope = " + str(round(slope1, 2)) + \
                 ", intercept = " + str(round(intercept1, 2)) + \
                 ", R^2 = " + str(round(r_squared1, 2))

        fig0 = px.line(x=t, y=slope0 * t + intercept0,
                       labels={'x': 'Percent Concerened', 'y': 'CO_2 Emissions'}, title=title0)
        fig0.add_trace(go.Scatter(x=x0_values, y=y0_values, mode='markers'), row=1, col=1)

        fig1 = px.line(x=t, y=slope1 * t + intercept1,
                       labels={'x': 'Percent Concerened',
                               'y': 'CO_2 Emissions per Capita'}, title=title1)
        fig1.add_trace(go.Scatter(x=x1_values, y=y1_values, mode='markers'), row=1, col=1)

        fig0.show()
        fig1.show()

    def denial_and_energy_production(self) -> None:
        """Display plots showing the relationship between denial and energy production"""
        x_values = []
        y_values = []
        for region in self.regions:
            concerned = self.regions[region].percentage_concerned
            if concerned is not None:
                renewable_energy = self.regions[region].renewable_energy[2016]
                if renewable_energy is not None:
                    x_values.append(concerned)
                    y_values.append(renewable_energy)

        slope, intercept = Regression.linear_regression(x_values, y_values)

        r_squared = Regression.strength_of_correlation(slope, intercept, x_values, y_values)

        t = np.linspace(0, 100, 100)

        title = "slope = " + str(round(slope, 2)) + \
                ", intercept = " + str(round(intercept, 2)) + ", R^2 = " + str(round(r_squared, 2))

        fig = px.line(x=t, y=slope * t + intercept,
                      labels={'x': 'Percent Concerened',
                              'y': 'Renewable Energy Production'}, title=title)
        fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='markers'), row=1, col=1)

        fig.show()

    def denial_and_carbon_tax(self) -> None:
        """Display plots showing the relationship between denial
        and the implementation of a carbon tax
        """
        x_values = []
        y_values = []
        for region in self.regions:
            concerned = self.regions[region].percentage_concerned
            if concerned is not None:
                carbon_tax = self.regions[region].has_carbon_tax
                if carbon_tax:
                    x_values.append(concerned)
                    y_values.append(1)
                elif not carbon_tax:
                    x_values.append(concerned)
                    y_values.append(0)

        slope, intercept = Regression.linear_regression(x_values, y_values)

        r_squared = Regression.strength_of_correlation(slope, intercept, x_values, y_values)

        t = np.linspace(0, 100, 100)

        title = "slope = " + str(round(slope, 2)) + \
                ", intercept = " + str(round(intercept, 2)) + ", R^2 = " + str(round(r_squared, 2))

        fig = px.line(x=t, y=slope * t + intercept,
                      labels={'x': 'Percent Concerened', 'y': 'Has Carbon Tax'}, title=title)
        fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='markers'), row=1, col=1)

        fig.show()

    # menu 1
    def gdp_per_capita_and_emissions(self) -> None:
        """Display plots showing the relationship between GDP per capita and CO2 emissions per capita"""
        x0_values = []
        x1_values = []
        y0_values = []
        y1_values = []
        for region in self.regions:
            concerned = self.regions[region].gdp_per_capita[2016]
            if concerned is not None:
                emissions = self.regions[region].co2_emissions[2016]
                emissions_per_capita = self.regions[region].co2_emissions_per_capita[2016]
                if emissions is not None:
                    x0_values.append(concerned)
                    y0_values.append(emissions)
                if emissions_per_capita is not None:
                    x1_values.append(concerned)
                    y1_values.append(emissions_per_capita)

        slope0, intercept0 = Regression.linear_regression(x0_values, y0_values)
        slope1, intercept1 = Regression.linear_regression(x1_values, y1_values)

        r_squared0 = Regression.strength_of_correlation(slope0, intercept0, x0_values, y0_values)
        r_squared1 = Regression.strength_of_correlation(slope1, intercept1, x1_values, y1_values)

        t = np.linspace(0, max(max(x0_values), max(x1_values)), 100)

        title0 = "slope = " + str(round(slope0, 2)) + \
                 ", intercept = " + str(round(intercept0, 2)) + ", R^2 = " + str(round(r_squared0, 2))
        title1 = "slope = " + str(round(slope1, 2)) + \
                 ", intercept = " + str(round(intercept1, 2)) + ", R^2 = " + str(round(r_squared1, 2))

        fig0 = px.line(x=t, y=slope0 * t + intercept0,
                       labels={'x': 'GDP per Capita', 'y': 'CO_2 Emissions'}, title=title0)
        fig0.add_trace(go.Scatter(x=x0_values, y=y0_values, mode='markers'), row=1, col=1)

        fig1 = px.line(x=t, y=slope1 * t + intercept1,
                       labels={'x': 'GDP per Capita', 'y': 'CO_2 Emissions per Capita'}, title=title1)
        fig1.add_trace(go.Scatter(x=x1_values, y=y1_values, mode='markers'), row=1, col=1)

        fig0.show()
        fig1.show()

    def gdp_per_capita_and_carbon_taxes(self) -> None:
        """Display plots showing the relationship between GDP per capita and carbon tax implementation"""
        x_values = []
        y_values = []
        for region in self.regions:
            gdp_per_capita = self.regions[region].gdp_per_capita[2016]
            if gdp_per_capita is not None:
                carbon_tax = self.regions[region].has_carbon_tax
                if carbon_tax:
                    x_values.append(gdp_per_capita)
                    y_values.append(1)
                elif not carbon_tax:
                    x_values.append(gdp_per_capita)
                    y_values.append(0)

        slope, intercept = Regression.linear_regression(x_values, y_values)

        r_squared = Regression.strength_of_correlation(slope, intercept, x_values, y_values)

        t = np.linspace(0, max(x_values), 100)

        title = "slope = " + str(round(slope, 2)) + \
                ", intercept = " + str(round(intercept, 2)) + ", R^2 = " + str(round(r_squared, 2))

        fig = px.line(x=t, y=slope * t + intercept,
                      labels={'x': 'GDP per Capita', 'y': 'Has Carbon Tax'}, title=title)
        fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='markers'), row=1, col=1)

        fig.show()

    def largest_co2(self) -> List[str]:
        """Return the names of the top 10 CO2 emitting regions"""
        top10 = [(None, 0) for _ in range(10)]
        for region in self.regions:
            emissions = self.regions[region].co2_emissions[2016]
            if emissions is None:
                continue
            for i in range(10):
                if top10[i][1] < emissions:
                    top10.insert(i, (region, emissions))
                    top10 = top10[:10]
                    break
        return [region[0] for region in top10]

    def most_contributing_regions(self) -> str:
        """Return a string listing the ten regions emitting the most CO2 in 2016"""
        return ", ".join(self.largest_co2())

    def average_gdp_contributing_regions(self) -> str:
        """Return the average GDP of regions contributing the most to climate change as a string"""
        total = 0
        for region in self.largest_co2():
            total += self.regions[region].gdp[2016]
        return str(round(total / 10))

    # menu 2
    def location_and_emissions(self) -> None:
        """Display a table showing the average emissions per continent"""
        continents_emissions = {"North America": 0,
                                "South America": 0,
                                "Africa": 0,
                                "Asia": 0,
                                "Oceania": 0,
                                "Europe": 0,
                                "Antarctica": 0}
        continents_total = {"North America": 0,
                            "South America": 0,
                            "Africa": 0,
                            "Asia": 0,
                            "Oceania": 0,
                            "Europe": 0,
                            "Antarctica": 0}

        for region_name in self.regions:
            region = self.regions[region_name]
            continent = region.continent
            if region.co2_emissions[2016] is not None:
                continents_total[continent] += 1
                continents_emissions[continent] += region.co2_emissions[2016]

        data_points = [[], []]
        for continent in continents_emissions:
            if continents_total[continent] != 0:
                data_points[0].append(continent)
                data_points[1].append(continents_emissions[continent] / continents_total[continent])

        fig = go.Figure(data=[go.Table(header=dict(values=['Continent', 'CO_2 Emissions on average']),
                                       cells=dict(values=[data_points[0], data_points[1]]))
                              ])
        fig.show()

    def damage_and_emissions(self) -> None:
        """Display plots showing the relationship between projected change to GDP and emissions"""
        x0_values = []
        x1_values = []
        y0_values = []
        y1_values = []
        for region in self.regions:
            concerned = self.regions[region].projected_damage
            if concerned is not None:
                emissions = self.regions[region].co2_emissions[2016]
                emissions_per_capita = self.regions[region].co2_emissions_per_capita[2016]
                if emissions is not None:
                    x0_values.append(concerned)
                    y0_values.append(emissions)
                if emissions_per_capita is not None:
                    x1_values.append(concerned)
                    y1_values.append(emissions_per_capita)

        slope0, intercept0 = Regression.linear_regression(x0_values, y0_values)
        slope1, intercept1 = Regression.linear_regression(x1_values, y1_values)

        r_squared0 = Regression.strength_of_correlation(slope0, intercept0, x0_values, y0_values)
        r_squared1 = Regression.strength_of_correlation(slope1, intercept1, x1_values, y1_values)

        t = np.linspace(min(min(x0_values), min(x1_values)), max(max(x0_values), max(x1_values)), 100)

        title0 = "slope = " + str(round(slope0, 2)) + \
                 ", intercept = " + str(round(intercept0, 2)) + ", R^2 = " + str(round(r_squared0, 2))
        title1 = "slope = " + str(round(slope1, 2)) + \
                 ", intercept = " + str(round(intercept1, 2)) + ", R^2 = " + str(round(r_squared1, 2))

        fig0 = px.line(x=t, y=slope0 * t + intercept0,
                       labels={'x': 'Projected Damage', 'y': 'CO_2 Emissions'}, title=title0)
        fig0.add_trace(go.Scatter(x=x0_values, y=y0_values, mode='markers'), row=1, col=1)

        fig1 = px.line(x=t, y=slope1 * t + intercept1,
                       labels={'x': 'Projected Damage', 'y': 'CO_2 Emissions per Capita'}, title=title1)
        fig1.add_trace(go.Scatter(x=x1_values, y=y1_values, mode='markers'), row=1, col=1)

        fig0.show()
        fig1.show()

    def greatest_help(self) -> List[str]:
        """Returns a list of regions doing the most to help climate change"""
        top10 = [(None, 0) for _ in range(10)]
        for region in self.regions:
            score = self.regions[region].region_score
            if score is None:
                continue
            for i in range(10):
                if top10[i][1] < score:
                    top10.insert(i, (region, score))
                    top10 = top10[:10]
                    break
        return [region[0] for region in top10]

    def most_helpful_regions(self) -> str:
        """Return a string showing the regions which do the most to fight climate change"""
        return ", ".join(self.greatest_help())

    def average_damage_helping_regions(self) -> str:
        """Return the projected damage to regions doing the most to fight climate change as a string"""
        total = 0
        for region in self.greatest_help():
            projected_damage = self.regions[region].projected_damage
            if projected_damage is not None:
                total += projected_damage
        return str(round(total / 10, 3))


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()

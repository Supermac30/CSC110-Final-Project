"""Stores all methods for gathering data from the data sets, and analysing them

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
from typing import List, Dict, Tuple
from random import randint
from datetime import datetime
import json
import logging

import python_ta

from regions import Region
from twitter import Tweet


# Taken from the International Monetary Fund
COUNTRIES_WITH_CARBON_TAX = [
    'Argentina', 'Canada', 'Chile', 'Colombia',
    'Denmark', 'Estonia', 'Finland',
    'France', 'Iceland', 'Ireland',
    'Japan', 'Latvia', 'Liechtenstein',
    'Mexico', 'Norway', 'Poland', 'Portugal',
    'Singapore', 'Slovenia', 'South Africa',
    'Spain', 'Sweden', 'Switzerland', 'United Kingdom', 'Ukraine'
]


class DataSet:
    """Stores all region data and methods for getting data out of the data set files

    Instance Attributes:
        - regions: All the Region objects storing all the required data
        - tweets: All the Tweet object gathered
    """
    regions: Dict[str, Region]
    tweets: List[Tweet]

    def __init__(self) -> None:
        self.regions = {}
        self.tweets = []

        logging.info("Initialising data set\n")
        logging.info("Initialising regions")
        self.initialise_regions()
        logging.info("Initialised regions\n")

        logging.info("Initialising CO2 emissions")
        self.initialise_co2_emissions()
        logging.info("Initialised CO2 emissions\n")

        logging.info("Initialising GDP emissions")
        self.initialise_gdp()
        logging.info("Initialised GDP emissions\n")

        logging.info("Initialising energy production")
        self.energy_production()
        logging.info("Initialised energy production\n")

        logging.info("Initialising population")
        self.initialise_population()
        logging.info("Initialised population\n")

        logging.info("Initialising gdp per capita")
        self.initialise_gdp_per_capita()
        logging.info("Initialised gdp per capita\n")

        logging.info("Initialising CO2 emissions per capita")
        self.initialise_co2_emissions_per_capita()
        logging.info("Initialised CO2 emissions per capita")

        logging.info("Initialising renewables per capita")
        self.initialise_renewables_per_capita()
        logging.info("Initialised renewables per capita")

        logging.info("Initialising Carbon Tax")
        self.initialise_carbon_tax()
        logging.info("Done Initialising Carbon Tax\n")

        logging.info("Initialising projected damage")
        self.initialise_projected_damage()
        logging.info("Initialised projected damage\n")

        logging.info("Initialising climate change opinion")
        self.initialise_climate_opinion()
        logging.info("Initialised climate change opinion\n")

        logging.info("Initialising region score")
        self.initialise_region_score()
        logging.info("Initialised region score\n")

        logging.info("Initialising tweets")
        self.get_tweet_data()
        logging.info("Initialised tweets\n")

        logging.info("Initialised data set\n")

    def get_tweet_data(self) -> None:
        """Gathers all tweets from the data set"""
        f = open("data/Climate_Tweets.txt", encoding="utf-8")
        for tweet_json in f.readlines():
            tweet_json = eval(tweet_json)  # turns the dict text into a dict

            hashtags = {hashtag['text'].lower() for hashtag in tweet_json['entities']['hashtags']}

            tweet = Tweet(
                text=tweet_json['full_text'],
                hashtags=hashtags,
                date=self.parse_date(tweet_json['created_at']),
                location=tweet_json['user']['location'],
                user=tweet_json['user']['name']
            )

            # annoyingly, retweets have truncated text
            # if a tweet is a retweet, take the text from the original
            if "retweeted_status" in tweet_json:
                tweet.text = tweet_json['retweeted_status']['full_text']

            self.tweets.append(tweet)

    def get_random_tweet(self) -> Tweet:
        """Returns a random tweet from the tweet data set

        Used in the Sampled Tweet menu
        """
        return self.tweets[randint(0, len(self.tweets) - 1)]

    def initialise_regions(self) -> None:
        """Create all the region data classes"""
        f = open("data/country_names.csv")
        data = f.readlines()

        for line in data[1:]:
            name, continent = DataSet.parse_csv_line(line)
            region = Region(
                name=name,
                continent=continent
            )
            self.regions[name] = region

        f.close()

        # To ensure consistency between different data sets,
        # some names will be changed
        uk = self.regions["United Kingdom of Great Britain & Northern Ireland"]
        del self.regions["United Kingdom of Great Britain & Northern Ireland"]
        self.regions["United Kingdom"] = uk

        us = self.regions["United States of America"]
        del self.regions["United States of America"]
        self.regions["United States"] = us

    def initialise_co2_emissions(self) -> None:
        """Gathers the CO2 emissions from 1951-2016

        Collects data from the earliest start year if the earliest start year is greater than 1951
        """
        f = open("data/CO2_emissions.json")
        data_set = json.load(f)
        for region in self.regions:
            if region not in data_set:
                continue
            data = data_set[region]['data']

            for line in data:
                if 1951 <= line['year'] <= 2016 and 'co2' in line:
                    self.regions[region].co2_emissions[line['year']] = line['co2']

    def initialise_gdp(self) -> None:
        """Gathers GDP from 1951-2016

        Collects data from the earliest start year if the earliest start year is greater than 1951
        """
        f = open("data/CO2_emissions.json")
        data_set = json.load(f)
        for region in self.regions:
            if region not in data_set:
                continue
            data = data_set[region]['data']

            for line in data:
                if 1951 <= line['year'] <= 2016 and 'gdp' in line:
                    self.regions[region].gdp[line['year']] = line['gdp']

    def initialise_population(self) -> None:
        """Gathers population from 1951-2016

        Collects data from the earliest start year if the earliest start year is greater than 1951
        """
        f = open("data/CO2_emissions.json")
        data_set = json.load(f)
        for region in self.regions:
            if region not in data_set:
                continue
            data = data_set[region]['data']

            for line in data:
                if 1951 <= line['year'] <= 2016 and 'population' in line:
                    self.regions[region].population[line['year']] = line['population']

    def initialise_gdp_per_capita(self) -> None:
        """Calculates the gdp per capita of each region
        using the population and gdp gathered before"""
        for region in self.regions:
            population = self.regions[region].population
            gdp = self.regions[region].gdp

            if population == {} or gdp == {}:
                continue

            start_year = max(
                min(population),
                min(gdp)
            )

            for year in range(start_year, 2017):
                if gdp[year] is not None and population[year] is not None:
                    self.regions[region].gdp_per_capita[year] = gdp[year] / population[year]

    def initialise_co2_emissions_per_capita(self) -> None:
        """Calculates the gdp per capita of each region
        using the population and gdp gathered before"""
        for region in self.regions:
            population = self.regions[region].population
            co2_emissions = self.regions[region].co2_emissions

            if population == {} or co2_emissions == {}:
                continue

            start_year = max(
                min(population),
                min(co2_emissions)
            )

            for year in range(start_year, 2017):
                if co2_emissions[year] is not None and population[year] is not None:
                    self.regions[region].co2_emissions_per_capita[year] = \
                        co2_emissions[year] / population[year]

    def initialise_renewables_per_capita(self) -> None:
        """Calculates the gdp per capita of each region
        using the population and gdp gathered before"""
        for region in self.regions:
            population = self.regions[region].population
            renewable_energy = self.regions[region].renewable_energy

            if population == {} or renewable_energy == {}:
                continue

            start_year = max(
                min(population),
                min(renewable_energy)
            )

            for year in range(start_year, 2017):
                if renewable_energy[year] is not None and population[year] is not None:
                    self.regions[region].renewable_energy_per_capita[year] = \
                        renewable_energy[year] / population[year]

    def energy_production(self) -> None:
        """Gathers the percentage of energy gathered from renewables"""
        f = open("data/IRENA_RE_electricity_statistics_-_Query_tool.csv")
        data = f.readlines()
        for line in data[9:]:
            line = line.split(",")
            region = line[1]

            # Handles different naming between different data sets
            if region == "USA":
                region = "United States"
            elif region == "UK":
                region = "United Kingdom"

            if region not in self.regions:
                continue

            for i in range(3, 20):
                amount = line[i].replace(" ", "")
                if amount != "":
                    self.regions[region].renewable_energy[1997 + i] = float(amount)

        f.close()

    def initialise_carbon_tax(self) -> None:
        """Find whether or not a country has a carbon tax

        This is added manually, with data taken from the data set
        """
        for country in COUNTRIES_WITH_CARBON_TAX:
            region = self.regions[country]
            region.has_carbon_tax = True

    def initialise_projected_damage(self) -> None:
        """Find the projected damage as a percentage to GDP due to climate change"""
        f = open("data/projected_GDP_change.txt", encoding='utf-8')
        data = f.readlines()
        for line in data[1:]:
            line = line.split("\t")
            if line[0] in self.regions:
                line[-1] = line[-1].replace("−", "-")  # changes the dash to an ascii hyphen
                self.regions[line[0]].projected_damage = float(line[-1])

            elif line[0] == "United States of America":
                line[-1] = line[-1].replace("−", "-")  # changes the dash to an ascii hyphen
                self.regions["United States"].projected_damage = float(line[-1])

    def initialise_climate_opinion(self) -> None:
        """Find the percentage of population who are concerned about climate change
        in certain regions
        """
        f = open("data/climate_change_opinion_by_country.txt")
        data = f.readlines()
        for line in data:
            line = line.split("\t")
            if line[0] in self.regions:
                self.regions[line[0]].percentage_concerned = int(line[1][:-2])

            # Handles different names for regions
            elif line[0] == "U.S.":
                self.regions["United States"].percentage_concerned = int(line[1][:-2])
            elif line[0] == "UK":
                self.regions["United Kingdom"].percentage_concerned = int(line[1][:-2])

    def initialise_region_score(self) -> None:
        """Give an Ad Hoc score to each region that is larger when regions do more to
        fight climate change

        Used to compare different regions
        """
        for region_name in self.regions:
            region = self.regions[region_name]
            renewable = region.renewable_energy[2016]
            emission = region.co2_emissions[2016]
            if renewable is None or emission is None:
                continue
            score = renewable / emission
            if region.has_carbon_tax:
                score *= 10
            region.region_score = score

    @staticmethod
    def parse_csv_line(line: str) -> Tuple[str, str]:
        """A helper function, parses a line of data from country_names.csv

        Takes a line of the form
        <Continent>,<Continent Code>,<Name>,<etc.>
        where <Name> may be surrounded in quotation marks if it contains a comma
        and returns the name and continent

        >>> DataSet.parse_csv_line('Europe,EU,"Albania, Republic of",AL,ALB,8')
        ('Albania', 'Europe')
        """
        line = line.replace("\"", "").split(",")

        return (line[2], line[0])

    @staticmethod
    def parse_date(date_text: str) -> datetime:
        """Takes date as formated in the tweet status and turns it into a datetime object

        preconditions:
            - len(date_text.split()) == 6
            - date_text.split()[1] in
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Nov', 'Dec']
            - date_text.split()[2].isnumeric()
            - 1 <= int(date_text.split()[2]) <= 31
            - date_text.split()[5].isnumeric()

        >>> DataSet.parse_date("Tue Dec 21 20:50:12 +0000 2010")
        datetime.datetime(2010, 12, 21, 20, 50, 12)
        """
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        months_dict = {months[i]: i + 1 for i in range(len(months))}
        date = date_text.split()
        year = int(date[5])
        month = months_dict[date[1]]
        day = int(date[2])

        time = date[3].split(':')
        hour = int(time[0])
        minute = int(time[1])
        second = int(time[2])

        return datetime(year, month, day, hour, minute, second)


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()

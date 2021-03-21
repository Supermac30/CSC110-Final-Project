"""Holds the MenuManager class, which is responsible for the user interface

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
from typing import List, Tuple, Optional
import logging

import pygame
import python_ta
from pygame_menu import Menu, widgets, font, themes

from dataset import DataSet
from plots import Plots
from final_report import FinalReport

HEIGHT = 500
WIDTH = 1000


class MenuManager:
    """Handles the creation of the GUI

    Instance Attributes:
        - surface: The pygame surface the GUI is displayed on
        - theme: The pygame-menu theme used
        - final_menu_theme: The pygame-menu theme used in the final report
        - data_set: The DataSet used

        - main_menu: The pygame-menu storing the main menu
        - regions_menu: The pygame-menu storing the regions profiles
        - region_menu: The pygame-menu storing the region menu generated when clicked on a region
        - tweet_menu: The pygame-menu storing the tweet displayer menu
        - correlation_menu: The pygame-menu storing the correlation displayer
        - final_menu0: The pygame-menu storing the first page of the final report
        - final_menu1: The pygame-menu storing the second page of the final report
        - final_menu2: The pygame-menu storing the third page of the final report

        - is_at_region_menu: Stores whether the region menu generated should currently be displayed
        - chosen_x_values: Stores the x variable chosen in the correlation displayer
        - chosen_y_values: Stores the y variable chosen in the correlation displayer
        - chose_local: Stores whether the user chose to investigate variables within a region

        - tweet_info: The pygame-menu label used to display and update the tweet metadata displayed
        - tweet_display: The list of pygame-menu labels used to
            display and update the tweet displayed
    """
    surface: pygame.display
    theme: themes.Theme
    final_menu_theme: themes.Theme

    data_set: DataSet

    main_menu: Menu
    regions_menu: Menu
    region_menu: Menu
    tweet_menu: Menu
    correlation_menu: Menu
    final_menu0: Menu
    final_menu1: Menu
    final_menu2: Menu

    is_at_region_menu: bool
    chosen_x_values: str
    chosen_y_values: str
    chose_local: Tuple[bool, str]

    tweet_info: widgets.Label
    tweet_display: List[widgets.Label]

    def __init__(self, data_set: DataSet) -> None:
        self.data_set = data_set

        pygame.init()
        pygame.font.init()

        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('CSC110 Final Project: '
                                   'Climate Change Denial, Contribution, and Prevention')

        self.theme = themes.Theme(
            background_color=(36, 227, 71),
            title_shadow=True,
            title_background_color=(255, 0, 0),
            title_bar_style=widgets.MENUBAR_STYLE_SIMPLE,
            title_font=font.FONT_OPEN_SANS_BOLD,
            title_font_size=35,
            widget_font=font.FONT_OPEN_SANS,
            widget_font_size=40
        )

        self.final_menu_theme = themes.Theme(
            background_color=(36, 227, 71),
            title_shadow=True,
            title_background_color=(255, 0, 0),
            title_bar_style=widgets.MENUBAR_STYLE_SIMPLE,
            title_font=font.FONT_OPEN_SANS_BOLD,
            title_font_size=35,
            widget_font=font.FONT_OPEN_SANS,
            widget_font_size=20
        )

        # Set default values for correlation finder
        self.is_at_region_menu = False
        self.chosen_x_values = "time"
        self.chosen_y_values = "co2_emissions"
        self.chose_local = (False, "Canada")

        self.initialise_menus()

    def initialise_menus(self) -> None:
        """Initialises all GUI elements in all menus"""
        logging.info("creating menus\n")
        logging.info("creating final menu")
        self.initialise_final_menus()
        logging.info("created final menu\n")
        logging.info("creating correlation menu")
        self.initialise_correlation_menu()
        logging.info("created correlation menu\n")
        logging.info("creating tweet menu")
        self.initialise_tweet_menu()
        logging.info("created tweet menu\n")
        logging.info("creating regions menu")
        self.initialise_regions_menu()
        logging.info("created regions menu\n")
        logging.info("creating main menu")
        self.initialise_main_menu()
        logging.info("created main menu\n")
        logging.info("created menus\n")

    def loop(self) -> Optional[bool]:
        """Handles user events

        Returns True when the user exits
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return True

            # As a quirk of pygame-menu, becuase region_menu is generated
            # a new during runtime, it has to be handled separately
            if self.is_at_region_menu:
                self.region_menu.update(events)
                self.region_menu.draw(self.surface)
            else:
                self.main_menu.update(events)
                self.main_menu.draw(self.surface)

            pygame.display.update()

        return None

    def create_plot(self) -> None:
        """Creates a plotly graph based on the chosen x and y values

        uses the values chosen for x, y, and the location by the user"""
        regions = self.data_set.regions

        if self.chose_local[0]:
            if self.chosen_x_values == "time":
                Plots.in_region_over_time(regions[self.chose_local[1]],
                                          self.chosen_y_values)
            else:
                Plots.in_region(regions[self.chose_local[1]], self.chosen_x_values, self.chosen_y_values)
        else:
            if self.chosen_x_values == "time":
                Plots.all_regions_over_time(regions, self.chosen_y_values)
            else:
                Plots.all_regions(regions, self.chosen_x_values, self.chosen_y_values)

    def initialise_final_menus(self) -> None:
        """Creates all GUI elements in the final report"""
        self.final_menu0 = Menu(HEIGHT, WIDTH, "Final Report: Public Perception and Response",
                                theme=self.final_menu_theme)
        self.final_menu1 = Menu(HEIGHT, WIDTH, "Final Report: GDP and Response",
                                theme=self.final_menu_theme)
        self.final_menu2 = Menu(HEIGHT, WIDTH, "Final Report: Projected Damage and Response",
                                theme=self.final_menu_theme)

        final_report = FinalReport(self.data_set)

        # Initialises final_menu0
        self.final_menu0.add_label("The Most Common Days For Climate Change "
                                   "Tweets in this data set are: "
                                   + final_report.most_common_days(), max_char=-1)
        self.final_menu0.add_button("Look at climate change denying tweets in selected regions",
                                    final_report.compare_selected_locations)
        self.final_menu0.add_button("Correlation between denial and CO_2 Emissions",
                                    final_report.denial_and_emissions)
        self.final_menu0.add_button("Correlation between denial and Renewable Energy Production",
                                    final_report.denial_and_energy_production)
        self.final_menu0.add_button("Correlation between denial and carbon taxes",
                                    final_report.denial_and_carbon_tax)
        self.final_menu0.add_button("Next", self.final_menu1)

        # Initialises final_menu1
        self.final_menu1.add_button("Correlation between GDP per capita "
                                    "and CO_2 Emissions per capita",
                                    final_report.gdp_per_capita_and_emissions)
        self.final_menu1.add_button("Correlation between GDP per capita and carbon taxes",
                                    final_report.gdp_per_capita_and_carbon_taxes)
        self.final_menu1.add_label("The Ten Regions contributing the most to climate change per capita are: "
                                   + final_report.most_contributing_regions(), max_char=-1)
        self.final_menu1.add_label("The average GDP of these regions is: "
                                   + final_report.average_gdp_contributing_regions(), max_char=-1)
        self.final_menu1.add_button("Next", self.final_menu2)

        # Initialises final_menu2
        self.final_menu2.add_button("Correlation between geographic location and CO_2 Emissions per capita",
                                    final_report.location_and_emissions)
        self.final_menu2.add_button("Correlation between projected damage and CO_2 Emissions per capita",
                                    final_report.damage_and_emissions)
        self.final_menu2.add_label("The Ten Regions doing the most to stop climate change are: "
                                   + final_report.most_helpful_regions(), max_char=-1)
        self.final_menu2.add_label("The average projected damage of these regions is: "
                                   + final_report.average_damage_helping_regions(), max_char=-1)

    def initialise_correlation_menu(self) -> None:
        """Creates all GUI elements in the correlation finder"""
        self.correlation_menu = Menu(HEIGHT, WIDTH, "Correlation Finder", theme=self.theme)
        options_y = [
            ('co2_emissions',),
            ('co2_emissions_per_capita',),
            ('gdp',),
            ('gdp_per_capita',),
            ('population',),
            ('renewable_energy',),
            ('renewable_energy_per_capita',),
        ]
        options_x = [('time', )] + options_y
        self.correlation_menu.add_selector(
            "x-values",
            options_x,
            onchange=self.change_x_values
        )
        self.correlation_menu.add_selector(
            "y_values",
            options_y,
            onchange=self.change_y_values
        )
        self.correlation_menu.add_selector(
            "Location",
            [('global',), ('local',)],
            onchange=self.change_location
        )
        self.correlation_menu.add_button("Create Plot", self.create_plot)

    def initialise_tweet_menu(self) -> None:
        """Creates all GUI elements in the tweet menu"""
        self.tweet_menu = Menu(HEIGHT, WIDTH, "Sampled Tweets", theme=self.theme)

        self.tweet_menu.add_button("Show Another Tweet", self.random_tweet)

        self.tweet_info = self.tweet_menu.add_label("Location:  User: ", font_size=20)

        # the label will be turned into a list to make it easy to manage
        # as, annoyingly, sometimes this function returns a list
        self.tweet_display = [self.tweet_menu.add_label(" ", max_char=-1)]

    def create_region_menu(self, value: str = None) -> None:
        """Create the menu displaying the region's data

        preconditions:
            - value in self.data_set.regions
        """
        region = self.data_set.regions[value]
        self.region_menu = Menu(HEIGHT, WIDTH, value, theme=self.theme, onclose=self.quit_region_menu)
        self.region_menu.add_label("Continent: " + region.continent)
        self.region_menu.add_label("GDP Per Capita: " + str(region.gdp_per_capita[2016]))
        self.region_menu.add_label("Has Carbon Tax: " + str(region.has_carbon_tax))
        self.region_menu.add_label("CO_2 Emissions: " + str(region.co2_emissions[2016]))
        self.region_menu.add_label("Renewable Energy: " + str(region.renewable_energy[2016]))
        self.region_menu.add_label("Expected Damage as a percentage of GDP: " + str(region.projected_damage))
        self.region_menu.add_label("Percentage of people concerned: " + str(region.percentage_concerned))
        self.region_menu.add_label("Region Score: " + str(region.region_score))
        self.region_menu.add_button("Choose Region", self.choose_region, value)

        self.is_at_region_menu = True

    def choose_region(self, value: str) -> None:
        """Changes the location of self.chose_local.
        Created to be called by the pygame-menu Button

        The correlation menu will now find local correlations of this region"""
        self.chose_local = (self.chose_local[0], value)

    def quit_region_menu(self) -> None:
        """closes the new region menu generated.
        Created to be called by the pygame-menu Button"""
        self.is_at_region_menu = False

    def initialise_regions_menu(self) -> None:
        """Creates all GUI elements in the region profiles selector"""
        self.regions_menu = Menu(HEIGHT, WIDTH, "Region Profiles", theme=self.theme)

        for region in self.data_set.regions:
            self.regions_menu.add_button(region, self.create_region_menu, region)

    def initialise_main_menu(self) -> None:
        """Creates all GUI elements in the main menu"""
        self.main_menu = Menu(HEIGHT, WIDTH, "Climate Change Denial, Contribution, and Prevention", theme=self.theme)
        self.main_menu.add_button("Region Profiles", self.regions_menu)
        self.main_menu.add_button("Sampled Tweets", self.tweet_menu)
        self.main_menu.add_button("Correlation Finder", self.correlation_menu)
        self.main_menu.add_button("Final Report", self.final_menu0)

    def random_tweet(self) -> None:
        """Places a random tweet in the display of the tweets menu"""
        tweet = self.data_set.get_random_tweet()
        text = self.clean_text(tweet.text)
        location = self.clean_text(tweet.location)
        user = self.clean_text(tweet.user)

        self.tweet_info.set_title("User: \"" + user + "\", Location: \"" + location + "\"")

        # Annoyingly, the label has to be deleted and re-added,
        # or the text will not wrap
        for line in self.tweet_display:
            self.tweet_menu.remove_widget(line)
        labels = self.tweet_menu.add_label(text, max_char=-1, font_size=20)

        # The function above returns a list if an overflow occurs,
        # and a single widget object otherwise
        # the label will be turned into a list to make it easy to manage if it already is not
        if isinstance(labels, list):
            self.tweet_display = labels
        else:
            self.tweet_display = [labels]

    def change_x_values(self, value: Tuple[str]) -> None:
        """Change the value of the variable self.chosen_x_value
        Called when x value is changed in correlation menu"""
        self.chosen_x_values = value[0]

    def change_y_values(self, value: Tuple[str]) -> None:
        """Change the value of the variable self.chosen_y_value
        Called when y value is changed in correlation menu"""
        self.chosen_y_values = value[0]

    def change_location(self, value: Tuple[str]) -> None:
        """Change whether correlations are found locally or globally.
        Called by the pygame-menu Button"""
        if value[0] == 'local':
            self.chose_local = (True, self.chose_local[1])
        else:
            self.chose_local = (False, self.chose_local[1])

    @staticmethod
    def clean_text(text: str) -> str:
        """A helper function that Removes all characters with
        character code above 0xFFFF so that pygame can display it"""
        cleaned_text = ""
        for char in text:
            if ord(char) <= 0xFFFF:
                cleaned_text += char
        return cleaned_text


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()

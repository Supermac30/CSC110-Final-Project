"""The dataclass to store information about a region

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
from typing import Dict
from dataclasses import dataclass, field

import python_ta


def defualt_dict() -> Dict[int, None]:
    """Returns the defualt value for the parameters in the Region Dataclass"""
    return {year: None for year in range(1951, 2017)}


@dataclass
class Region:
    """A region data class for storing region data

    Instance Attributes:
        - name: The name of the region
        - continent: The continent the region is in
        - population: The population of the region
        - has_carbon_tax: Whether or not a carbon tax is implemented
        - co2_emissions: The amount of CO2 Emissions in tonnes
        - co2_emissions_per_capita: The amount of CO2 Emissions in tonnes per person
        - gdp: The gdp of the region
        - gdp_per_capita: The gdp per capita of the region
        - renewable_energy: The amount of renewable energy produced in the region in GWh
        - projected_damage: The projected damage to a region as a percent of GDP
        - percent_concerned: The percentage of the population concerned about climate change
        - region_score: The amount a region does to fight climate change
    """
    name: str
    continent: str = None
    population: Dict[int, float] = field(default_factory=defualt_dict)

    has_carbon_tax: bool = False

    co2_emissions: Dict[int, float] = field(default_factory=defualt_dict)
    co2_emissions_per_capita: Dict[int, float] = field(default_factory=defualt_dict)

    gdp: Dict[int, float] = field(default_factory=defualt_dict)
    gdp_per_capita: Dict[int, float] = field(default_factory=defualt_dict)

    renewable_energy: Dict[int, float] = field(default_factory=defualt_dict)
    renewable_energy_per_capita: Dict[int, float] = field(default_factory=defualt_dict)

    projected_damage: float = None
    percentage_concerned: float = None

    region_score: float = None


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()

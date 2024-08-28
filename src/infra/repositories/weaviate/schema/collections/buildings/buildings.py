""" This module is responsible for Buildings collection filter handling
"""
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from weaviate.classes.query import Filter

def append_housing_price_filters(buildings_filter: BuildingsFilter, filter_array: list) -> list:
    if(isinstance(buildings_filter.less_than_price, float) and \
            isinstance(buildings_filter.greater_than_price, float)):
        filter_array.append(Filter.by_ref(link_on="hasBuilding").by_property("housingPrice").greater_or_equal(buildings_filter.greater_than_price))
        filter_array.append(Filter.by_ref(link_on="hasBuilding").by_property("housingPrice").less_or_equal(buildings_filter.less_than_price))
    elif(isinstance(buildings_filter.greater_than_price, float)):
        filter_array.append(Filter.by_ref(link_on="hasBuilding").by_property("housingPrice").greater_or_equal(buildings_filter.greater_than_price))
    elif(isinstance(buildings_filter.less_than_price, float)):
        filter_array.append(Filter.by_ref(link_on="hasBuilding").by_property("housingPrice").less_or_equal(buildings_filter.less_than_price))
        
    return filter_array

def append_building_facility_filters(buildings_filter: BuildingsFilter, filter_array: list) -> list:
    if isinstance(buildings_filter.building_facility, str):
        result_list = [item.strip() for item in buildings_filter.building_facility.split(',')]
        if all(isinstance(item, str) for item in result_list):
            for k in result_list:
                filter_array.append(Filter.by_property("chunk").like(f"*{k}*"))
    
    return filter_array
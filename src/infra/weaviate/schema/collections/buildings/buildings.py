""" This module is responsible for Buildings collection filter handling
"""
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from weaviate.classes.query import Filter

def append_housing_price_filters(buildings_filter: BuildingsFilter, filter_array: list) -> list:
    if(isinstance(buildings_filter.greater_than_price, float)):
        filter_array.append(Filter.by_property("housing_price").greater_than(buildings_filter.greater_than_price))
    elif(isinstance(buildings_filter.less_than_price, float)):
        filter_array.append(Filter.by_property("housing_price").less_than(buildings_filter.less_than_price))
    elif(isinstance(buildings_filter.less_than_price, float) and \
            isinstance(buildings_filter.greater_than_price, float)):
        filter_array.append(Filter.by_property("housing_price").greater_than(buildings_filter.greater_than_price))
        filter_array.append(Filter.by_property("housing_price").less_than(buildings_filter.less_than_price))
        
    return filter_array
    
def append_property_address_filters(buildings_filter: BuildingsFilter, filter_array: list) -> list:
    if(buildings_filter.building_address is not None):
        filter_array.append(Filter.by_property("property_address").like(f"*{buildings_filter.building_address}*"))
    return filter_array
    
def append_property_title_filters(buildings_filter: BuildingsFilter, filter_array: list) -> list:
    if(buildings_filter.building_title is not None):
        filter_array.append(Filter.by_property("property_title").like(f"*{buildings_filter.building_title}*"))
    return filter_array
    
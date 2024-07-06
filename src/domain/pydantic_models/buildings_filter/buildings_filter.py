from langchain_core.pydantic_v1 import BaseModel, Field, root_validator

class BuildingsFilter(BaseModel):
    building_title: str | None = Field(description="The title of the building, if applicable")
    building_address: str | None = Field(description="The building location whether its a province, city, district, street, etc. If applicable.")
    building_facility: str | None = Field(description="The facility provided by the building. If applicable.")
    filter_type: str | None = Field(description="Type of price filter (LESS_THAN, GREATER_THAN, AROUND)")
    less_than_price: float | None = Field(description="The maximum rent price, if applicable.")
    greater_than_price: float | None = Field(description="The minimum rent price, if applicable.")
    
    @root_validator(pre=True)
    def convert_prices(cls, values):
        values['less_than_price'] = cls.convert_price(values.get('less_than_price'))
        values['greater_than_price'] = cls.convert_price(values.get('greater_than_price'))
        return values
    
    @staticmethod
    def convert_price(price: float) -> float:
        if price is not None:
            # Assuming that the input is given in millions (e.g., 1.5 means 1,500,000)
            if price < 100:  # If the price is less than 100, it's likely given in millions
                return price * 1_000_000
        
        return price
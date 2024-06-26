from langchain_core.pydantic_v1 import BaseModel, Field

class RentPriceFilter(BaseModel):
    is_asking_for_pricing: bool = Field(description="define whether the prompt is asking for pricing or not")
    filter_type: str = Field(description="Type of price filter (LESS_THAN, GREATER_THAN, AROUND)")
    less_than_price: float = Field(description="The maximum rent price, if applicable.")
    greater_than_price: float = Field(description="The minimum rent price, if applicable.")
    
    def __post_init__(self):
        self.less_than_price = self.convert_price(self.less_than_price)
        self.greater_than_price = self.convert_price(self.greater_than_price)
    
    @staticmethod
    def convert_price(price: float) -> float:
        if price is not None:
            # Assuming that the input is given in millions (e.g., 1.5 means 1,500,000)
            if price < 100:  # If the price is less than 100, it's likely given in millions
                return price * 1_000_000
        return price
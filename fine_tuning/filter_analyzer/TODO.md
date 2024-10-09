# TODO

## What to train

- respond when the user said "bisa lebih murah ga" or "mahalan dikit gapapa min"
  - to understand whether the input is asking for a change of price for slight amount

### Current system message (Please update the TODO file if you change the training data system message)

Understand the context of the conversation and define the extracted data based on the prompt and the conversation context. 1. analyze the context of the incoming input based on the conversation, 2. simulate extracting data from the conversation, 3. If the filter type is to be AROUND, make sure to adjust the price for greater_than_price: xxx - 250000 and less_than_price: xxx + 250000, 4. If the input implies desires for cheap prices, set the price to be LESS_THAN 1500000 and if it implies for high budget set the price to be GREATER_THAN 2000000 this applies only if the input gave no budget, 5. the enum for gender is [Lelaki, Perempuan, Campur, Bebas], provide the following fields in a JSON dict, where applicable: \"building_title\", \"building_address\", \"building_proximity\", \"building_facility\", \"building_note\", \"filter_type\", \"less_than_price\", and \"greater_than_price\"., NOTE: filter price can't be less than or equal 0 if the filter reach 0 or minus, give 0 value

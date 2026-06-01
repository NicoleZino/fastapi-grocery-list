from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
import pytz

VANCOUVER_TZ = pytz.timezone("America/Vancouver")

class GroceryItemDetails(BaseModel):
    weight_grams: float = Field(..., gt = 0, description = "The weight of the item has to be a positive number in grams.")
    organic: bool = Field(..., description = "Is the item organic? (True/False)")
    availability: Optional[str] = Field("In stock", description = "Is this item in stock, out of stock, or seasonal?") 
    expiration_date: Optional[datetime] = Field(None, description = "This is the expiration date of the items in the grocery list.")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"weight_grams": 500, "organic": True, "availability": "In stock"},
                {"weight_grams": 200, "organic": False, "availability": "Out of stock"},
            ]
        }
    }

class GroceryItem(BaseModel):
    id: UUID = Field(default_factory = uuid4, description = "Each item has a unique identifier that shows the item is different from other items")
    name: str = Field(..., min_length = 2, max_length = 20, description = "Name of the item in the grocery list: ")
    category: str = Field(..., description = "Other categories can be selected")
    price_per_gram: float = Field(..., gt = 0, description = "Price per gram has to be a positive number")
    added_at: datetime = Field(default_factory = lambda: datetime.now(VANCOUVER_TZ), description = "the timestamp this item was added to the grocery list")
    details: GroceryItemDetails
    
    # This is for tutorial - Declare Request Example Data
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Carrots",
                    "category": "Veggie",
                    "price_per_gram": 1.50,
                    "details": {
                        "weight_grams": 30.0,
                        "organic": True,
                        "availability": "In stock"
                    }
                },
                {
                    "name": "Strawberries",
                    "category": "Fruit",
                    "price_per_gram": 0.50,
                    "details": {
                        "weight_grams": 15.0,
                        "organic": False,
                        "availability": "Seasonal"
                    }
                }
            ]
        }
    }

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class CategoryEnum(str, Enum):
    FOOD = "food"
    COFFEE = "coffee"
    TRANSPORT = "transport"
    SHOPPING = "shopping"
    OTHER = "other"


class Item(BaseModel):
    name: str = Field(description="Name of the item")
    quantity: Optional[float] = Field(default=None, description="Quantity of the item")
    unit_price: Optional[float] = Field(
        default=None, description="Unit price of the item"
    )
    total_price: Optional[float] = Field(
        default=None, description="Total price of the item"
    )
    vat_percent: Optional[float] = Field(
        default=None, description="VAT percentage for the item"
    )
    final_price: Optional[float] = Field(
        default=None, description="Final price including VAT"
    )
    category: CategoryEnum = Field(description="Category of the item")


class ExtractionResult(BaseModel):
    items: List[Item] = Field(description="List of extracted items from the receipt")
    receipt_date: Optional[str] = Field(
        default=None, description="Receipt date on the receipt. Format: DD/MM/YYYY"
    )


class ItemResponse(Item):
    upload_time: Optional[str] = Field(
        default=None, description="Upload time of the item"
    )
    receipt_date: Optional[str] = Field(
        default=None, description="Receipt date on the receipt"
    )

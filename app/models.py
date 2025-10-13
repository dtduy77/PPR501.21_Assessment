from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Item(BaseModel):
    """Model cho một mặt hàng được trích xuất từ hóa đơn"""

    name: str = Field(description="Tên của mặt hàng")
    quantity: Optional[float] = Field(default=None, description="Số lượng của mặt hàng")
    unit_price: Optional[float] = Field(
        default=None, description="Giá đơn vị của mặt hàng"
    )
    total_price: Optional[float] = Field(
        default=None, description="Tổng giá của mặt hàng"
    )
    vat_percent: Optional[float] = Field(
        default=None, description="Phần trăm VAT cho mặt hàng"
    )
    final_price: Optional[float] = Field(
        default=None, description="Giá cuối cùng bao gồm VAT"
    )
    category: Literal["food", "coffee", "transport", "shopping", "other"] = Field(
        description="Danh mục của mặt hàng: food (đồ ăn), coffee (cà phê/đồ uống), transport (giao thông), shopping (mua sắm), other (khác)"
    )


class ExtractionResult(BaseModel):
    items: List[Item] = Field(
        description="Danh sách các mặt hàng được trích xuất từ hóa đơn"
    )
    receipt_date: Optional[str] = Field(
        default=None, description="Ngày trên hóa đơn. Định dạng: DD/MM/YYYY"
    )


class ItemResponse(Item):
    upload_time: Optional[str] = Field(
        default=None, description="Thời gian tải lên của mặt hàng"
    )
    receipt_date: Optional[str] = Field(default=None, description="Ngày trên hóa đơn")

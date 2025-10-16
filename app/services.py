import os
import base64
from typing import Dict, Any
from datetime import datetime, timedelta
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.Repository.item_repository import create_item, get_items_by_date_range
from .configs import ModelConfig
from .models import ExtractionResult


def get_file_metadata(image_path: str) -> str:
    """Get file metadata including upload time"""
    try:
        # Get current time as upload time
        upload_time = datetime.now().strftime("%H:%M:%S %d-%m-%y")

        # Get file size
        file_size = os.path.getsize(image_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)

        return f"Upload time: {upload_time}, File size: {file_size_mb}MB"
    except Exception as e:
        upload_time = datetime.now().strftime("%H:%M:%S %d-%m-%y")
        return f"Upload time: {upload_time}"


def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for sending to vision models"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def create_vision_chain(provider: str):
    """Create LangChain chain for vision analysis with JSON output parser"""

    # Create JSON output parser using our Pydantic model
    parser = JsonOutputParser(pydantic_object=ExtractionResult)

    # Create prompt template
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                [
                    {
                        "type": "text",
                        "text": """
Phân tích hình ảnh hóa đơn/bill này và trích xuất dữ liệu có cấu trúc chi tiết cho tất cả các mặt hàng được tìm thấy.

Cấu trúc output phải tuân theo mô hình Pydantic sau:
{format_instructions}

Đối với mỗi mặt hàng được tìm thấy trên hóa đơn, hãy trích xuất các thông tin sau:

CÁC TRƯỜNG BẮT BUỘC:
- name: Tên chính xác/mô tả của mặt hàng như được viết trên hóa đơn
- category: Phân loại mỗi mặt hàng thành một trong: food, coffee, transport, shopping, hoặc other

CÁC TRƯỜNG TÙY CHỌN (trích xuất nếu nhìn thấy trên hóa đơn):
- quantity: Số lượng mặt hàng đã mua (nếu có hiển thị, ví dụ: "2x", "3 cái")
- unit_price: Giá cho từng mặt hàng riêng lẻ (đơn vị: VND, trước VAT nếu có)
- total_price: Tổng giá cho mặt hàng này (đơn vị: VND, quantity × unit_price, trước VAT)
- vat_percent: Phần trăm VAT/thuế cho mặt hàng này (ví dụ: 10.0 cho 10%)
- final_price: Giá cuối cùng bao gồm VAT/thuế (đơn vị: VND)

HƯỚNG DẪN XỬ LÝ GIÁ CẢ VND:
1. Trích xuất TẤT CẢ các mặt hàng nhìn thấy trên hóa đơn, ngay cả khi thiếu một số thông tin giá
2. Nếu một trường không nhìn thấy hoặc không rõ ràng, đặt thành null (không phải 0)
3. Đối với giá cả bằng VND:
   - Loại bỏ tất cả ký hiệu tiền tệ (VND, đ, VNĐ, ₫)
   - Loại bỏ dấu phân cách hàng nghìn (dấu chấm hoặc dấu phẩy)
   - Chỉ giữ lại số nguyên (ví dụ: "25.000 VND" → 25000, "15,500đ" → 15500)
   - Nếu giá có đơn vị khác (USD, EUR), convert sang VND nếu có thể, nếu không thì giữ nguyên
4. Đối với phần trăm VAT, sử dụng định dạng thập phân (ví dụ: 10.0 cho 10%)
5. Đặc biệt chú ý các định dạng giá Việt Nam:
   - "25.000" hoặc "25,000" = 25000 VND
   - "1.250.000" = 1250000 VND
   - "50K" = 50000 VND
   - "2tr" hoặc "2 triệu" = 2000000 VND
6. Phân loại mặt hàng một cách phù hợp:
   - food: bữa ăn, đồ ăn nhẹ, thực phẩm, món ăn nhà hàng
   - coffee: cà phê, trà, đồ uống từ quán cafe
   - transport: taxi, xe buýt, tàu hỏa, đỗ xe, xăng dầu
   - shopping: đồ bán lẻ, quần áo, điện tử
   - other: bất cứ thứ gì không phù hợp với các danh mục trên

Return ONLY the JSON data in the exact format specified above. Do not include any additional text, explanations, or formatting.
""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,{image_data}"},
                    },
                ],
            )
        ]
    )

    # Get the appropriate LLM based on provider
    if provider == "openai":
        # Check if using Azure OpenAI or regular OpenAI
        azure_config = ModelConfig.get_azure_openai_config()
        if azure_config["api_key"] and azure_config["endpoint"]:
            # Use Azure OpenAI
            from langchain_openai import AzureChatOpenAI

            llm = AzureChatOpenAI(
                azure_endpoint=azure_config["endpoint"],
                azure_deployment=azure_config["deployment"],
                api_version=azure_config["api_version"],
                api_key=azure_config["api_key"],
                temperature=0.0,
            )
        else:
            # Use regular OpenAI
            from langchain_openai import ChatOpenAI

            config = ModelConfig.get_openai_config()
            llm = ChatOpenAI(
                model=(
                    config["name"]
                    if config["name"] in ["gpt-4o", "gpt-4-vision-preview"]
                    else "gpt-4o"
                ),
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
            )
    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        config = ModelConfig.get_google_config()
        llm = ChatGoogleGenerativeAI(
            model=config["name"],
            temperature=config["temperature"],
            max_output_tokens=config["max_output_tokens"],
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Create the chain
    chain = prompt_template | llm | parser
    return chain, parser


def extract_from_image_with_langchain(image_path: str, provider: str) -> Dict[str, Any]:
    """Extract data from image using LangChain with JsonOutputParser"""
    try:
        # Create the LangChain chain
        chain, parser = create_vision_chain(provider)

        # Encode image and get metadata
        base64_image = encode_image_to_base64(image_path)

        # Run the chain with error handling
        try:
            result = chain.invoke(
                {
                    "image_data": base64_image,
                    "format_instructions": parser.get_format_instructions(),
                }
            )
            print(f"LLM Raw Output: {result}")  # Debug logging

            # Ensure the result is a dictionary
            if isinstance(result, dict):
                # Validate that we have the expected structure
                if "items" in result:
                    # Add upload_time to the result
                    upload_time = datetime.now().strftime("%H:%M:%S %d-%m-%y")
                    result["upload_time"] = upload_time
                    return result
                else:
                    # If missing items, create proper structure
                    upload_time = datetime.now().strftime("%H:%M:%S %d-%m-%y")
                    return {"items": [], "upload_time": upload_time}
            else:
                # If result is not a dict, try to extract items manually
                print(f"Unexpected result type: {type(result)}")
                upload_time = datetime.now().strftime("%H:%M:%S %d-%m-%y")
                return {"items": [], "upload_time": upload_time}

        except Exception as parse_error:
            print(f"JSON parsing failed: {parse_error}")
            # Try to create a basic structure with empty items
            upload_time = datetime.now().strftime("%H:%M:%S %d-%m-%y")
            return {"items": [], "upload_time": upload_time}

    except Exception as e:
        raise RuntimeError(f"LangChain extraction failed for {provider}: {str(e)}")


def extract_from_image(path: str) -> dict:
    """Extract structured data from receipt image using LangChain"""

    try:
        # Get available provider automatically
        provider = ModelConfig.detect_provider()

        # Use LangChain for extraction
        result = extract_from_image_with_langchain(path, provider)

        # Ensure the result has the correct structure
        if "items" not in result:
            result["items"] = []
        if "raw_text" not in result:
            result["raw_text"] = f"Extracted using {provider} via LangChain"

        return result

    except Exception as e:
        # If the configured provider fails, try fallback
        try:
            # Try the other provider as fallback
            if ModelConfig.check_google_available():
                result = extract_from_image_with_langchain(path, "google")
            elif ModelConfig.check_openai_available():
                result = extract_from_image_with_langchain(path, "openai")
            else:
                raise RuntimeError("No working LLM providers available") from e

            # Ensure the result has the correct structure
            if "items" not in result:
                result["items"] = []
            if "raw_text" not in result:
                result["raw_text"] = "Extracted using fallback provider via LangChain"

            return result

        except Exception:
            raise RuntimeError(
                f"All LLM providers failed. Original error: {str(e)}"
            ) from e


def save_items_to_db(result: dict):
    items = result.get("items", [])
    receipt_date = result.get("receipt_date")
    formatted_receipt_date = None
    if receipt_date:
        try:
            # Try full datetime first
            formatted_receipt_date = datetime.strptime(
                receipt_date, "%H:%M:%S %d-%m-%y"
            ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                # Try date only (DD-MM-YY)
                formatted_receipt_date = datetime.strptime(
                    receipt_date, "%d-%m-%y"
                ).strftime("%Y-%m-%d")
            except Exception:
                try:
                    # Try date only (YYYY-MM-DD)
                    formatted_receipt_date = datetime.strptime(
                        receipt_date, "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                except Exception:
                    try:
                        # Try DD/MM/YYYY format (common in receipts)
                        formatted_receipt_date = datetime.strptime(
                            receipt_date, "%d/%m/%Y"
                        ).strftime("%Y-%m-%d")
                    except Exception:
                        try:
                            # Try MM/DD/YYYY format
                            formatted_receipt_date = datetime.strptime(
                                receipt_date, "%m/%d/%Y"
                            ).strftime("%Y-%m-%d")
                        except Exception:
                            print(f"Could not parse receipt_date: {receipt_date}")
                            formatted_receipt_date = (
                                None  # Set to None instead of invalid format
                            )
    else:
        formatted_receipt_date = None
    upload_time = result.get("upload_time")

    # Convert upload_time to PostgreSQL timestamp format if needed
    # Expected input: 'HH:MM:SS DD-MM-YY', output: 'YYYY-MM-DD HH:MM:SS'
    formatted_upload_time = None
    if upload_time:
        try:
            dt = datetime.strptime(upload_time, "%H:%M:%S %d-%m-%y")
            formatted_upload_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            formatted_upload_time = upload_time  # fallback, may error in DB
    else:
        formatted_upload_time = None

    for item in items:
        create_item(
            name=item.get("name"),
            quantity=item.get("quantity"),
            unit_price=item.get("unit_price"),
            total_price=item.get("total_price"),
            vat_percent=item.get("vat_percent"),
            final_price=item.get("final_price"),
            category=item.get("category"),
            upload_time=formatted_upload_time,
            receipt_date=formatted_receipt_date,
        )


def get_expenses_by_type_and_date(type: str, date: str):
    """
    Calculate date range and return items for day, month, or year.
    - type: 'day', 'month', or 'year'
    - date: 'YYYY-MM-DD'
    """
    print(f"Calculating expenses for type: {type}, date: {date}")
    dt = datetime.strptime(date, "%Y-%m-%d")
    if type == "day":
        start_date = dt.strftime("%Y-%m-%d")
        end_date = dt.strftime("%Y-%m-%d")
    elif type == "month":
        start_date = dt.replace(day=1).strftime("%Y-%m-%d")
        # Find last day of month
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)
        end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
    elif type == "year":
        start_date = dt.replace(month=1, day=1).strftime("%Y-%m-%d")
        end_date = dt.replace(month=12, day=31).strftime("%Y-%m-%d")
    else:
        raise ValueError("Invalid type")

    items = get_items_by_date_range(start_date, end_date)
    return {
        "type": type,
        "date": date,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(items),
        "items": [item.dict() for item in items],
    }

# Bill Receipt Extraction (LangChain + Vision Models)

This FastAPI application extracts structured data from receipt/bill images using LangChain with JsonOutputParser. It supports both OpenAI GPT-4o and Google Gemini vision models. The system directly processes images without OCR preprocessing, using vision models to extract item details with proper categorization.

**Key Features:**

- Direct image processing with vision models (no OCR needed)
- LangChain integration with JsonOutputParser for structured output
- Automatic provider fallback (OpenAI ↔ Google)
- Pydantic models for type safety
- FastAPI web service with automatic documentation

**Project Structure:**

```
app/
├── __init__.py
├── main.py          # FastAPI application
├── models.py        # Pydantic models for structured data
├── services.py      # LangChain vision extraction logic
└── configs.py       # Model configurations and provider detection
.env                 # Environment variables
requirements.txt     # Python dependencies
```

## Setup & Installation

### 1. Prerequisites

- Python 3.8+ installed
- Git (optional, for cloning)

### 2. Create and activate Python environment

**Windows (Command Prompt/PowerShell):**

```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Or in PowerShell
.venv\Scripts\Activate.ps1
```

**macOS/Linux (Terminal/Bash/Zsh):**

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 3. Install dependencies

**All platforms:**

```bash
pip install -r requirements.txt
```

If you encounter issues, try upgrading pip first:

```bash
# Windows
python -m pip install --upgrade pip

# macOS/Linux
python3 -m pip install --upgrade pip
```

3. Set environment variables for the provider you want to use.

**Option 1: Create `.env` file (recommended):**

```bash
# For OpenAI GPT-4o
PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o

# OR for Google Gemini
PROVIDER=google
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL=gemini-2.5-flash
```

**Option 2: Export environment variables:**

```bash
# For OpenAI
export PROVIDER=openai
export OPENAI_API_KEY=sk-your-key
export OPENAI_MODEL=gpt-4o

# OR for Google Gemini
export PROVIDER=google
export GOOGLE_API_KEY=your-key
export GOOGLE_MODEL=gemini-2.5-flash
```

4. Run the FastAPI server:

```bash
# Run with uvicorn from project root (make sure you installed the requirements)
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Or run directly with Python
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

5. Use the API:

```bash
# Health check
curl http://127.0.0.1:8000/health

# Extract data from receipt image
curl -X POST "http://127.0.0.1:8000/extract" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/receipt.jpg"
```

### Configuration

You can configure models through environment variables or by modifying `app/configs.py`:

## Supported Models

**OpenAI Vision Models:**

- `gpt-4o` (recommended for vision tasks)
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-4-vision-preview`

**Google Gemini Models:**

- `gemini-2.5-flash` (recommended, fastest)
- `gemini-pro`
- `gemini-1.5-pro`
- `gemini-pro-preview`

## API Usage

The system provides structured JSON output using Pydantic models:

```json
{
  "items": [
    {
      "name": "Coca Cola",
      "quantity": 2.0,
      "unit_price": 1.5,
      "total_price": 3.0,
      "vat_percent": 10.0,
      "final_price": 3.3,
      "category": "coffee"
    },
    {
      "name": "Burger",
      "quantity": 1.0,
      "unit_price": 8.99,
      "total_price": 8.99,
      "vat_percent": 10.0,
      "final_price": 9.89,
      "category": "food"
    }
  ],
  "upload_time": "14:30:25 07-10-25"
}
```

**Categories:** `food`, `coffee`, `transport`, `shopping`, `other`

## Technical Details

**LangChain Integration:**

- Uses `JsonOutputParser` for guaranteed structured output
- Automatic retry with fallback providers
- Type-safe Pydantic models with validation

**Vision Processing:**

- Direct image-to-text extraction using vision models
- No OCR preprocessing required
- Supports common image formats: JPG, PNG, GIF, BMP, TIFF

**Error Handling:**

- Automatic provider fallback (OpenAI ↔ Google)
- Structured error responses
- Input validation and file type checking

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# View API documentation
# Visit http://localhost:8000/docs for Swagger UI
# Visit http://localhost:8000/redoc for ReDoc
```

**Extending the system:**

- Add new categories in `app/models.py` → `CategoryEnum`
- Modify extraction prompt in `app/services.py` → `create_vision_chain()`
- Add new providers in `app/configs.py` → `ModelConfig`

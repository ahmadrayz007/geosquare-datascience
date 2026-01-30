import requests
import json
import base64
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

# Paths (relative to script location)
SCRIPT_DIR = Path(__file__).parent.absolute()

# Load .env file
load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("ERROR: Set OPENROUTER_API_KEY environment variable")
    print("Get your API key from: https://openrouter.ai/keys")
    print("\nUsage:")
    print("  export OPENROUTER_API_KEY='your-key-here'")
    print("  python vision_ocr.py")
    exit(1)

# Read and encode image
image_path = SCRIPT_DIR / "disdukcapil_oku.jpeg"
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

print(f"Processing {image_path}...")
print(f"Image size: {len(image_data)} bytes (base64)")

# Prepare the request
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# Using Google Gemini 2.0 Flash (good vision, cheap)
# Or try: "anthropic/claude-3.5-sonnet" (better quality, more expensive)
model = "z-ai/glm-4.6v"

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Extract the table data from this image and return it as a CSV format.

The table contains population data for Kabupaten Ogan Komering Ulu with these columns:
- NO. (row number)
- KECAMATAN (district name)
- LAKI-LAKI (male population)
- PEREMPUAN (female population)
- JUMLAH (total population)

Return ONLY the CSV data with header: kecamatan,laki_laki,perempuan,jumlah
Do not include the row numbers or the TOTAL row.
Make sure all district names are properly spelled and all numbers are accurate."""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
}

print(f"Calling OpenRouter API with model: {model}")
print("This may take 10-30 seconds...\n")

# Make the API request
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"ERROR: API request failed with status {response.status_code}")
    print(response.text)
    exit(1)

result = response.json()

# Extract the response
if "choices" not in result or len(result["choices"]) == 0:
    print("ERROR: No response from API")
    print(json.dumps(result, indent=2))
    exit(1)

extracted_text = result["choices"][0]["message"]["content"]

print("=== AI VISION RESPONSE ===")
print(extracted_text)
print("\n" + "="*80 + "\n")

# Parse CSV from response
# Sometimes AI wraps it in markdown code blocks
csv_data = extracted_text
if "```" in csv_data:
    # Extract content between code blocks
    import re
    match = re.search(r'```(?:csv)?\n(.*?)\n```', csv_data, re.DOTALL)
    if match:
        csv_data = match.group(1)

# Write to temporary CSV file
with open("temp_vision_ocr.csv", "w") as f:
    f.write(csv_data)

# Read with pandas
try:
    df = pd.read_csv("temp_vision_ocr.csv")

    # Clean column names (remove whitespace)
    df.columns = df.columns.str.strip()

    # Add total row
    total_row = {
        'kecamatan': 'TOTAL',
        'laki_laki': df['laki_laki'].sum(),
        'perempuan': df['perempuan'].sum(),
        'jumlah': df['jumlah'].sum()
    }
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    print("=== EXTRACTED TABLE DATA ===")
    print(df.to_string(index=False))

    # Save to final CSV (output to script directory)
    output_path = SCRIPT_DIR / 'penduduk_oku_vision.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved to {output_path.name} ({len(df)-1} kecamatan)")
    print(f"  Output directory: {SCRIPT_DIR}")

    print(f"\nTotal Penduduk Kabupaten OKU: {total_row['jumlah']:,} jiwa")
    print(f"  Laki-laki: {total_row['laki_laki']:,}")
    print(f"  Perempuan: {total_row['perempuan']:,}")

    # Clean up temp file
    os.remove("temp_vision_ocr.csv")

except Exception as e:
    print(f"ERROR parsing CSV: {e}")
    print("\nRaw CSV data:")
    print(csv_data)
    exit(1)

# Show API usage info
if "usage" in result:
    usage = result["usage"]
    print(f"\nAPI Usage:")
    print(f"  Tokens: {usage.get('total_tokens', 'N/A')}")
    if "native_tokens_prompt" in result:
        print(f"  Cost estimate: ${result.get('native_tokens_prompt', 0) * 0.000001:.6f}")

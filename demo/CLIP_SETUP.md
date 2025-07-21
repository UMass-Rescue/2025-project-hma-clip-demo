# CLIP Text Hash Server

A standalone Flask server that generates CLIP hashes from text strings, compatible with the format used by the HMA CLIP extension.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python clip_text_server.py
   ```

   The server will start on `http://localhost:5001`

## Usage

### Generate CLIP Hash from Text

**Request:**
```bash
curl -X POST http://localhost:5001/clip/text \
     -H "Content-Type: application/json" \
     -d '{"text": "a beautiful sunset over the mountains"}'
```

**Response:**
```json
{
  "success": true,
  "text": "a beautiful sunset over the mountains",
  "hash": "abc123def456789..."
}
```

### Health Check

**Request:**
```bash
curl http://localhost:5001/clip/health
```

**Response:**
```json
{
  "success": true,
  "status": "CLIP text hashing is working",
  "test_hash": "xyz789abc123..."
}
```

### API Info

**Request:**
```bash
curl http://localhost:5001/
```

## Examples

Here are some example curl commands you can try:

```bash
# Simple text
curl -X POST http://localhost:5001/clip/text \
     -H "Content-Type: application/json" \
     -d '{"text": "cat"}'

# Descriptive text
curl -X POST http://localhost:5001/clip/text \
     -H "Content-Type: application/json" \
     -d '{"text": "a fluffy orange cat sitting by the window"}'

# Abstract concept
curl -X POST http://localhost:5001/clip/text \
     -H "Content-Type: application/json" \
     -d '{"text": "happiness and joy"}'
```

## Notes

- The server uses OpenAI's CLIP ViT-B/32 model
- Hashes are generated using SHA256 of the normalized CLIP text embeddings
- The format should be compatible with the HMA CLIP extension
- First run will download the CLIP model (~400MB)
- GPU will be used automatically if available (CUDA)

## Troubleshooting

If you encounter issues:

1. **CUDA out of memory:** The server will automatically fall back to CPU
2. **Model download fails:** Check your internet connection
3. **Import errors:** Make sure all requirements are installed: `pip install -r requirements.txt` 
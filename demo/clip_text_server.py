#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.

"""
Standalone Flask server for generating CLIP hashes from text strings.
This can be run locally without Docker to provide CLIP text hashing functionality.
"""

from flask import Flask, request, jsonify
import hashlib
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def create_clip_text_hash(text: str) -> str:
    """
    Generate a CLIP hash from a text string.
    
    Args:
        text: Input text string
        
    Returns:
        CLIP hash as a hex string
    """
    try:
        import clip
        import torch
        
        # Load CLIP model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        model, _ = clip.load("ViT-B/32", device=device)
        
        # Tokenize and encode text
        text_tokens = clip.tokenize([text]).to(device)
        
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            # Normalize the features (standard practice with CLIP)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy and then to hex string (same format as HMA)
            embedding_array = text_features.cpu().numpy().flatten().astype(np.float32)
            embedding_bytes = embedding_array.tobytes()
            
            # Convert to hex string (same format as HMA uses)
            hash_str = embedding_bytes.hex()
            
            return hash_str
                
    except Exception as e:
        logger.error(f"Error generating CLIP hash for text '{text}': {e}")
        raise

@app.route('/clip/text', methods=['POST'])
def clip_text_hash():
    """
    Generate CLIP hash from text string.
    
    Expected JSON payload:
    {
        "text": "your text string here"
    }
    
    Returns:
    {
        "text": "input text",
        "hash": "generated_clip_hash",
        "success": true
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'text' field in request"
            }), 400
        
        text = data['text']
        if not isinstance(text, str) or not text.strip():
            return jsonify({
                "success": False,
                "error": "Text must be a non-empty string"
            }), 400
        
        # Generate CLIP hash
        logger.info(f"Generating CLIP hash for text: '{text}'")
        hash_value = create_clip_text_hash(text)
        
        response = {
            "success": True,
            "text": text,
            "hash": hash_value
        }
        
        logger.info(f"Generated hash: {hash_value}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in clip_text_hash endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/clip/health', methods=['GET'])
def clip_health():
    """
    Health check endpoint for CLIP functionality.
    """
    try:
        # Test with a simple string
        test_hash = create_clip_text_hash("test")
        return jsonify({
            "success": True,
            "status": "CLIP text hashing is working",
            "test_hash": test_hash
        })
    except Exception as e:
        logger.error(f"CLIP health check failed: {e}")
        return jsonify({
            "success": False,
            "status": "CLIP text hashing is not working",
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with usage information.
    """
    return jsonify({
        "service": "CLIP Text Hash Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /clip/text": "Generate CLIP hash from text",
            "GET /clip/health": "Health check",
            "GET /": "This help message"
        },
        "usage": {
            "curl_example": "curl -X POST http://localhost:5001/clip/text -H 'Content-Type: application/json' -d '{\"text\": \"your text here\"}'"
        }
    })

if __name__ == '__main__':
    print("🚀 Starting CLIP Text Hash Server...")
    print("📝 Usage:")
    print("   curl -X POST http://localhost:5001/clip/text \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"text\": \"your text here\"}'")
    print("")
    print("🔍 Health check:")
    print("   curl http://localhost:5001/clip/health")
    print("")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 
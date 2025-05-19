"""Configuration for CLIP Threat Exchange Extension."""
from tx_extension_clip.hasher import CLIPHasher

# Note that the embeddings must match the model used to generate the hashes.
# This metadata must be included in the database.
CLIP_DISTANCE_THRESHOLD: float = 0.1
CLIP_NORMALIZED: bool = True
OPEN_CLIP_MODEL_NAME: str = "xlm-roberta-base-ViT-B-32"
OPEN_CLIP_PRETRAINED: str = "laion5b_s13b_b90k"
BITS_IN_CLIP: int = 32 * 512

CLIP_HASHER: CLIPHasher = CLIPHasher(
    model_name=OPEN_CLIP_MODEL_NAME,
    pretrained=OPEN_CLIP_PRETRAINED,
    normalized=CLIP_NORMALIZED,
)

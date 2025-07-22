FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone -b manual-hashes https://github.com/UMass-Rescue/ThreatExchange.git

RUN cd ThreatExchange && pip install -e ./python-threatexchange

RUN cd ThreatExchange/hasher-matcher-actioner && pip install -e .

# -----------------------------------------------------------------------------
# Patch: add CLIP text hashing endpoint to OpenMediaMatch hashing blueprint
# -----------------------------------------------------------------------------
# We append a small route to hashing.py that loads the same open_clip model used
# for image hashing and returns a 4096-char hex embedding for a provided text.
# The new endpoint will be available at /h/clip_text?text=Your+query
#
RUN set -eux; \
  PATCH_FILE="ThreatExchange/hasher-matcher-actioner/src/OpenMediaMatch/blueprints/hashing.py"; \
  printf '\n# ---- Patched in Docker build: CLIP text hashing endpoint ----\n' >> "$PATCH_FILE"; \
  printf '\nimport binascii, numpy as _np\nimport open_clip as _oc\nimport torch as _torch\n' >> "$PATCH_FILE"; \
  printf '\n# Lazy-loaded global to avoid reloading the model per request\n_clip_text_model = None\n_clip_text_tokenizer = None\n' >> "$PATCH_FILE"; \
  printf '\n@bp.route("/clip_text", methods=["GET"])\ndef clip_text_hash() -> dict[str, str]:\n    """Return CLIP hex hash for ?text= query param (normalized LAION5B model)."""\n    text = request.args.get("text", "").strip()\n    if not text:\n        abort(400, "Missing required parameter: text")\n    global _clip_text_model, _clip_text_tokenizer\n    if _clip_text_model is None:\n        _clip_text_model, _, _ = _oc.create_model_and_transforms(\n            "xlm-roberta-base-ViT-B-32", "laion5b_s13b_b90k"\n        )\n        _clip_text_model.eval()\n    with _torch.no_grad():\n        tokens = _oc.tokenize([text])\n        feats = _clip_text_model.encode_text(tokens)\n        feats = _torch.nn.functional.normalize(feats, dim=-1)\n    arr = feats.cpu().numpy().flatten().astype(_np.float32)\n    return {"hash": arr.tobytes().hex(), "text": text}\n' >> "$PATCH_FILE"

RUN git clone -b threshold_eval https://github.com/UMass-Rescue/tx-extension-clip.git && \
    pip install -e ./tx-extension-clip

RUN threatexchange config extensions add tx_extension_clip

COPY omm_config.py /build/omm_config.py

WORKDIR /build/ThreatExchange/hasher-matcher-actioner

ENV PYTHONPATH=/build/ThreatExchange/hasher-matcher-actioner/src:$PYTHONPATH

EXPOSE 5000

ENV OMM_CONFIG=/build/omm_config.py

CMD ["python", "-m", "flask", "--app", "OpenMediaMatch.app", "run", "--host=0.0.0.0"]
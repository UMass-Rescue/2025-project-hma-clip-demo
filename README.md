# HMA Demo with CLIP Extension

This project serves as a practical demonstration on how to extend the capabilities of Hasher-Matcher-Actioner (HMA). If you are interested in building upon the foundational HMA tool, you can explore the main [HMA repository](https://github.com/facebook/ThreatExchange/tree/main/hasher-matcher-actioner) for more insights and community collaborations.

This demo showcases a specific implementation using the CLIP python threatexchange extension and work as a guide on how to customize HMA to suit your needs. This demo leverages Docker Compose for easy deployment and orchestration, making it ideal for both development and production environments.

## Introduction

[Hasher-Matcher-Actioner (HMA)](https://github.com/facebook/ThreatExchange/tree/main/hasher-matcher-actioner) is a content moderation tool by Meta that uses hashing technology for copy detection. This technology allows platforms to share digital fingerprints of content, enhancing their ability to detect and moderate harmful material.

This demo extends HMA to incorporate the [CLIP python ThreatExchange extension](https://pypi.org/project/tx-extension-clip/), which provides semantic embeddings that bridge text and image data. Allowing to match content with similar _meaning_ rather than similar visual components.

---

## Creating CLIP Hashes

Once `docker compose up --build` finishes, the Flask app inside the container exposes helper endpoints under the **Hasher** blueprint (`/h`).  You can generate hashes for either images or free-form text.

### 1. Image → CLIP hash

```bash
# photo is the multipart field name expected by the endpoint
curl -X POST http://localhost:5005/h/hash \
     -F photo=@/absolute/path/to/my_image.jpg
```

Response (truncated):

```jsonc
{
  "clip": "c66af73b14dcb43b…",   // 4096-character hex string
  "pdq":  "…",
  "vmd5": "…"
}
```

### 2. Text → CLIP hash

The Dockerfile patches HMA at build time with a *text* helper endpoint:

```bash
curl 'http://localhost:5005/h/clip_text?text=A%20red%20sports%20car'
#                 └───────── URL-encode your prompt ─────────┘
```

Response:

```jsonc
{
  "text": "A red sports car",
  "hash": "58feed…4096 hex chars…"
}
```

> **Note**: the hash value must be **exactly 4096 hex characters** (no quotes, no newline) when you paste or POST it back into HMA.

---

## Adding a Hash to a Bank

You can add the newly generated hash either through the UI or directly via the REST endpoint.

### Via the UI

1. Go to `http://localhost:5005/ui` →  *Banks*  →  *Add Hash to Bank*.
2. Select the bank (create one if needed), choose **clip** as signal type, paste the 4096-character hash, and click *Save*.

If the modal never closes, check your browser console or the container logs – a common cause is an extra newline or missing character in the hash.

### Via cURL

```bash
bank="ROAD"
hash=$(curl -s 'http://localhost:5005/h/clip_text?text=road' | jq -r '.hash')

curl -X POST http://localhost:5005/ui/add_hash_to_bank \
     -F "hash=$hash" \
     -F "signal_type=clip" \
     -F "bank_name=$bank"
```

The response will include the internal content-ID and echo the signals added.

---

## Getting Started

To get this demo up and running, follow these steps:

### Prerequisites

- Docker and Docker Compose installed on your machine.

### Setup and Run

1. **Clone the Repository**

```bash
   git clone [your-repository-url]
   cd [repository-name]
```

2. **Launch the Services**

Use Docker Compose to build and start the services defined in the `docker-compose.yml`:

```bash
    docker compose up --build
```

This command builds the Docker image and starts the services defined, including the application and the database.

## Configuration

The `omm_config.py` file in the build directory is essential for the application's configuration. Adjust this file according to your needs to fit your use case.

### Using the Demo

With the services running, you can interact with the HMA-CLIP extension through the REST API. The application is available at http://localhost:5005/, and API usage details are documented within the HMA repository.

### Contributions and Feedback

We welcome contributions and feedback on this demo. If you have improvements or encounter issues, please submit a pull request or raise an issue in this GitHub repository.

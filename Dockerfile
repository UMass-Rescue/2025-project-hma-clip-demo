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

RUN git clone -b main https://github.com/UMass-Rescue/ThreatExchange.git

RUN cd ThreatExchange && pip install -e ./python-threatexchange

RUN cd ThreatExchange/hasher-matcher-actioner && pip install -e .

RUN git clone -b main https://github.com/UMass-Rescue/tx-extension-clip.git && \
    pip install -e ./tx-extension-clip

RUN threatexchange config extensions add tx_extension_clip

COPY omm_config.py /build/omm_config.py

WORKDIR /build/ThreatExchange/hasher-matcher-actioner

ENV PYTHONPATH=/build/ThreatExchange/hasher-matcher-actioner/src:$PYTHONPATH

EXPOSE 5000

ENV OMM_CONFIG=/build/omm_config.py

CMD ["python", "-m", "flask", "--app", "OpenMediaMatch.app", "run", "--host=0.0.0.0"]

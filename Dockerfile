FROM ghcr.io/facebook/threatexchange/hma:1.0.17

WORKDIR /build

RUN apt-get update && apt-get install -y git && git clone https://github.com/UMass-Rescue/tx-extension-clip.git

RUN pip install -e ./tx-extension-clip && \
    threatexchange config extensions add tx_extension_clip

COPY omm_config.py /build/omm_config.py
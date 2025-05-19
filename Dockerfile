FROM ghcr.io/facebook/threatexchange/hma:1.0.3

WORKDIR /build

COPY tx-extension-clip-0.2.5 /build/tx-extension-clip-0.2.5 

RUN pip install -e ./tx-extension-clip-0.2.5 && \
    threatexchange config extensions add tx_extension_clip

COPY omm_config.py /build/omm_config.py
# https://developers.home-assistant.io/docs/apps/configuration/#app-dockerfile
# Debian rather than Alpine: onnxruntime only ships glibc (manylinux) wheels.
ARG BUILD_FROM=ghcr.io/home-assistant/base-debian:trixie
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# The Wyoming server itself is upstream's src/main.py, fetched at a pinned
# commit. Supervisor builds with this directory as the context, so the copy at
# the repository root is out of reach; bump the ref to pick up upstream changes.
ARG KOKORO_WYOMING_REPO=https://github.com/nordwestt/kokoro-wyoming
ARG KOKORO_WYOMING_REF=3fe86d9fa3b6221f51286d7f45887f45bf060307

# Model files published by kokoro-onnx
ARG MODEL_URL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0

ENV \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:${PATH} \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ORT_DISABLE_TELEMETRY=1

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv "${VIRTUAL_ENV}"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

ADD --checksum=sha256:7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5 \
    ${MODEL_URL}/kokoro-v1.0.onnx /usr/share/kokoro/kokoro-v1.0.onnx
ADD --checksum=sha256:bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d \
    ${MODEL_URL}/voices-v1.0.bin /usr/share/kokoro/voices-v1.0.bin

ADD ${KOKORO_WYOMING_REPO}/raw/${KOKORO_WYOMING_REF}/src/main.py /usr/src/kokoro_wyoming/main.py

COPY rootfs /

LABEL \
    org.opencontainers.image.title="Home Assistant App: Kokoro TTS" \
    org.opencontainers.image.description="Local text-to-speech with Kokoro via the Wyoming protocol" \
    org.opencontainers.image.source="https://github.com/chrishoage/kokoro-wyoming"

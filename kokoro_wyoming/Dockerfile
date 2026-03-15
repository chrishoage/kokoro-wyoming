FROM python:3.12-slim-bookworm
ENV PYTHONPATH=/app
WORKDIR /app/

# Runtime utilities needed by run.sh (jq + netcat for discovery, curl for Supervisor API)
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/var/cache/models \
    if [ ! -f /var/cache/models/kokoro-v1.0.onnx ]; then \
        curl -fsSL -o /var/cache/models/kokoro-v1.0.onnx \
            https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx; \
    fi && \
    if [ ! -f /var/cache/models/voices-v1.0.bin ]; then \
        curl -fsSL -o /var/cache/models/voices-v1.0.bin \
            https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin; \
    fi && \
    cp /var/cache/models/kokoro-v1.0.onnx /app/kokoro-v1.0.onnx && \
    cp /var/cache/models/voices-v1.0.bin /app/voices-v1.0.bin


# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Python package
COPY ./ /app/kokoro_wyoming/

# Copy and prepare run script
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 10200
CMD ["/run.sh"]

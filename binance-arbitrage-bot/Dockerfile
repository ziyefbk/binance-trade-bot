# Multi-stage Docker build for Binance Arbitrage Bot
# Stage 1: Build Rust core with PyO3 bindings

FROM rust:1.75-slim as rust-builder

# Install build dependencies
RUN apt-get update || true && \
    apt-get install -y --allow-unauthenticated --fix-missing \
    python3-dev \
    python3-pip \
    pkg-config \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* || true

# Install maturin for building PyO3 extensions
# Retry installation if pip3 is not available
RUN python3 -m pip install --no-cache-dir --upgrade pip || true && \
    (pip3 install --no-cache-dir maturin || python3 -m pip install --no-cache-dir maturin)

# Set working directory
WORKDIR /build

# Copy Rust source code
COPY rust-core/ /build/rust-core/

# Build the Rust core with maturin
WORKDIR /build/rust-core
RUN maturin build --release

# Stage 2: Final runtime image
FROM python:3.11-slim

# Install runtime dependencies with retry and ignore security repo errors
RUN apt-get update || true && \
    apt-get install -y --allow-unauthenticated \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* || true

# Set working directory
WORKDIR /app

# Copy Python strategy code
COPY python-strategy/ /app/python-strategy/

# Copy config directory
COPY config/ /app/config/

# Copy documentation
COPY docs/ /app/docs/
COPY README.md PROJECT_SUMMARY.md COMPILE_GUIDE.md /app/

# Copy compiled Rust wheel from builder stage
COPY --from=rust-builder /build/rust-core/target/wheels/*.whl /tmp/

# Install Python dependencies and Rust wheel
WORKDIR /app/python-strategy
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir /tmp/*.whl && \
    rm -f /tmp/*.whl

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV RUST_LOG=info

# Expose any necessary ports (optional, for future web dashboard)
# EXPOSE 8080

# Default command: run in backtest mode (safe for testing)
CMD ["python", "main.py", "--backtest"]

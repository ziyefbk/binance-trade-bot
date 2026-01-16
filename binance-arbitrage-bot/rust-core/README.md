# Binance Rust Core

High-performance Rust implementation of Binance trading engine with PyO3 Python bindings.

## Features

- REST API client for Binance
- WebSocket real-time data
- Order execution engine
- Price monitoring
- Rate limiting

## Building

```bash
maturin build --release
```

## Installation

```bash
pip install target/wheels/*.whl
```

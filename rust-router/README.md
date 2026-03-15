# Rust Router (WASM)

This crate contains the low-latency routing core for the capstone.

## Build

- `cargo build`
- `wasm-pack build --target web`

Phase-1 includes a minimal exported function; A* graph search is added in Phase-2.

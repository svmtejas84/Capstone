from pathlib import Path


def test_rust_astar_crate_exists() -> None:
	cargo = Path("router/rust_astar/Cargo.toml")
	assert cargo.exists()


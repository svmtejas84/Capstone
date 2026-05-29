# Windows Setup Notes

- **Python version:** Python 3.11 or newer (repository requires `>=3.11`). See `pyproject.toml`.
- **Script:** Use `setup_windows.ps1` in the repo root to create a virtual environment and install dependencies.

Quick steps (PowerShell):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
./setup_windows.ps1 -InstallDev
```

Notes:
- The script creates a `.venv` directory and installs the package in editable mode.
- If you prefer WSL or Docker, the Linux environment is supported and may be closer to CI.
- Copy and edit `.env.example` to `.env` for local secrets — the script will copy it if `.env` is missing.

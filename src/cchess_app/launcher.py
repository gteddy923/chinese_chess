import importlib
import subprocess
import sys


_DEPENDENCIES = {
    "speech_recognition": "SpeechRecognition>=3.10.0",
    "sounddevice": "sounddevice>=0.4.6",
    "numpy": "numpy>=1.24.0",
}


def _missing_packages() -> list[str]:
    missing = []
    for module_name, package_spec in _DEPENDENCIES.items():
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(package_spec)
    return missing


def _install(packages: list[str]) -> bool:
    if not packages:
        return True
    print("Installing missing dependencies:", ", ".join(packages))
    result = subprocess.run([sys.executable, "-m", "pip", "install", *packages])
    return result.returncode == 0


def main() -> None:
    missing = _missing_packages()
    if missing and not _install(missing):
        print("Failed to install dependencies. Please install them manually and retry.")
        return
    from .app import main as app_main

    app_main()

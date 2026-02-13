import os

def load_env_file(filepath: str = ".env") -> None:
    """
    Very simple .env file loader for standard library only usage.
    """
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

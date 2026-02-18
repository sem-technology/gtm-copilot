import os

def load_env_file(filepath: str = None) -> None:
    """
    Very simple .env file loader for standard library only usage.
    If no filepath is provided, it tries to find .env at the project root.
    """
    if filepath is None:
        # Auto-detect .env at project root (2 levels up from helpers/ directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        potential_env = os.path.abspath(os.path.join(current_dir, "..", "..", ".env"))
        if os.path.exists(potential_env):
            filepath = potential_env
        else:
            # Fallback to CWD
            filepath = ".env"

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

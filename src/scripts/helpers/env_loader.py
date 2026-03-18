import os

def load_env_file(filepath: str = None) -> None:
    """
    Very simple .env file loader for standard library only usage.
    If no filepath is provided, it tries to find .env at the project root.
    """
    if filepath is None:
        # Search for .env starting from current directory up to root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while True:
            potential_env = os.path.join(current_dir, ".env")
            if os.path.exists(potential_env):
                filepath = potential_env
                break
            
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                raise FileNotFoundError(".env file not found in current or any parent directories.")
            current_dir = parent_dir

    if not os.path.exists(filepath):
        raise FileNotFoundError(f".env file not found at: {filepath}")
        
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

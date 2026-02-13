import sys
import os
import json
import argparse

# Add src directory to path to import gtm_client and helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from gtm_client import GTMClient
    from helpers.env_loader import load_env_file
except ImportError as e:
    print(f"Error: Could not import necessary modules: {e}")
    sys.exit(1)

def save_to_json(data, directory, filename):
    """
    Saves the provided data to a JSON file in the specified directory.
    """
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported: {path}")

def main():
    parser = argparse.ArgumentParser(description="Export GTM tags, triggers, and variables to JSON files.")
    parser.add_argument("--account", required=True, help="GTM Account ID")
    parser.add_argument("--container", required=True, help="GTM Container ID")
    parser.add_argument("--workspace", required=True, help="GTM Workspace ID")
    parser.add_argument("--output", default="exports", help="Output directory (default: exports)")
    
    args = parser.parse_args()
    
    # Load credentials from .env
    load_env_file()
    
    # Initialize GTM Client
    client = GTMClient()
    
    workspace_path = f"accounts/{args.account}/containers/{args.container}/workspaces/{args.workspace}"
    
    # Create output directory
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"Created directory: {args.output}")

    try:
        print(f"Starting export for workspace: {workspace_path}")
        
        # Fetch Tags
        print("Fetching tags...")
        tags = client.list_tags(workspace_path)
        save_to_json(tags, args.output, "tags.json")
        
        # Fetch Triggers
        print("Fetching triggers...")
        triggers = client.list_triggers(workspace_path)
        save_to_json(triggers, args.output, "triggers.json")
        
        # Fetch Variables
        print("Fetching variables...")
        variables = client.list_variables(workspace_path)
        save_to_json(variables, args.output, "variables.json")

        # Fetch Built-in Variables
        print("Fetching built-in variables...")
        built_in_vars = client.list_built_in_variables(workspace_path)
        save_to_json(built_in_vars, args.output, "built_in_variables.json")
        
        print("\nExport completed successfully.")
        
    except Exception as e:
        print(f"\nAn error occurred during export: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

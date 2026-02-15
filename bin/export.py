import sys
import os
import json
import argparse

# Add src directory to path to import gtm_client and helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from gtm_client import GTMClient
    from helpers.env_loader import load_env_file
    from helpers.gtm_utils import parse_gtm_workspace_url
except ImportError as e:
    print(f"Error: Could not import necessary modules: {e}")
    sys.exit(1)

def save_to_json(data, directory, filename):
    """
    Saves the provided data to a JSON file in the specified directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported: {path}")

def main():
    parser = argparse.ArgumentParser(description="Export GTM tags, triggers, and variables to JSON files.")
    parser.add_argument("--url", help="GTM Workspace URL")
    parser.add_argument("--account", help="GTM Account ID")
    parser.add_argument("--container", help="GTM Container ID")
    parser.add_argument("--workspace", help="GTM Workspace ID")
    parser.add_argument("--output", help="Output directory (defaults to tmp/GTM-ID)")
    
    args = parser.parse_args()
    
    # Load credentials from .env
    load_env_file()
    
    # Initialize GTM Client
    client = GTMClient()
    
    account_id = args.account
    container_id = args.container
    workspace_id = args.workspace
    output_dir = args.output

    if args.url:
        parsed = parse_gtm_workspace_url(args.url)
        if not parsed:
            print(f"Error: Could not parse GTM URL: {args.url}")
            sys.exit(1)
        account_id = parsed["account_id"]
        container_id = parsed["container_id"]
        workspace_id = parsed["workspace_id"]

    if not all([account_id, container_id, workspace_id]):
        print("Error: Account, Container, and Workspace IDs are required (via --url or individual arguments)")
        sys.exit(1)

    container_path = f"accounts/{account_id}/containers/{container_id}"
    workspace_path = f"{container_path}/workspaces/{workspace_id}"
    
    try:
        # Fetch container info to get Public ID for folder name
        container_info = client.get_container(container_path)
        public_id = container_info.get("publicId", f"GTM-{container_id}")
        
        if not output_dir:
            output_dir = os.path.join("tmp", public_id)

        print(f"Starting export for workspace: {workspace_path}")
        print(f"Output directory: {output_dir}")
        
        # Fetch Tags
        print("Fetching tags...")
        tags = client.list_tags(workspace_path)
        save_to_json(tags, output_dir, "tags.json")
        
        # Fetch Triggers
        print("Fetching triggers...")
        triggers = client.list_triggers(workspace_path)
        save_to_json(triggers, output_dir, "triggers.json")
        
        # Fetch Variables
        print("Fetching variables...")
        variables = client.list_variables(workspace_path)
        save_to_json(variables, output_dir, "variables.json")

        # Fetch Built-in Variables
        print("Fetching built-in variables...")
        built_in_vars = client.list_built_in_variables(workspace_path)
        save_to_json(built_in_vars, output_dir, "built_in_variables.json")
        
        print("\nExport completed successfully.")
        
    except Exception as e:
        print(f"\nAn error occurred during export: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

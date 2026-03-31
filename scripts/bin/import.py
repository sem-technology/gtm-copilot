import sys
import os
import json
import argparse
from typing import Dict, List, Any, Optional

# Add parent directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from gtm_client import GTMClient
    from helpers.env_loader import load_env_file
    from helpers.gtm_utils import parse_gtm_workspace_url
except ImportError as e:
    print(f"Error: Could not import necessary modules: {e}")
    sys.exit(1)

def load_json(directory: str, filename: str) -> List[Dict[str, Any]]:
    """
    Loads data from a JSON file if it exists.
    """
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Skipping...")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(directory: str, filename: str, data: List[Dict[str, Any]]):
    """
    Saves data to a JSON file.
    """
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def clean_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Removes GTM-generated read-only fields from a tag, trigger, or variable.
    """
    cleaned = item.copy()
    # Common fields to remove
    fields_to_remove = [
        "path", "accountId", "containerId", "workspaceId", 
        "fingerprint", "tagId", "triggerId", "variableId", "parentFolderId", "tagManagerUrl",
        "monitoringMetadata"
    ]
    for field in fields_to_remove:
        cleaned.pop(field, None)
    
    return cleaned

class GTMDependencyResolver:
    """
    Resolves dependency between GTM components by name.
    If a component is referenced by name and doesn't exist, it creates it.
    """
    def __init__(self, client: GTMClient, workspace_path: str, directory: str):
        self.client = client
        self.workspace_path = workspace_path
        self.directory = directory
        
        # Original order from JSON files to preserve it during save
        self.variables_list = load_json(directory, "variables.json")
        self.triggers_list = load_json(directory, "triggers.json")
        self.tags_list = load_json(directory, "tags.json")

        # Registry of local components from JSON (keyed by type then name)
        self.local_repo = {
            "variables": {v['name']: v for v in self.variables_list},
            "triggers": {t['name']: t for t in self.triggers_list},
            "tags": {t['name']: t for t in self.tags_list},
        }
        
        # Registry of remote components in the workspace (keyed by type then name)
        print("Fetching existing items in workspace...")
        self.remote_registry = {
            "variables": {v['name']: v for v in client.list_variables(workspace_path)},
            "triggers": {t['name']: t for t in client.list_triggers(workspace_path)},
            "tags": {t['name']: t for t in client.list_tags(workspace_path)},
            "built_in_variables": {v['type']: v for v in client.list_built_in_variables(workspace_path)}
        }

    def resolve_id(self, component_type: str, name_or_id: Any) -> str:
        """
        Resolves a name or old ID to the current remote ID.
        """
        if not name_or_id:
            return name_or_id
            
        val_str = str(name_or_id)
        # If it's already a name in our local repo or remote registry, ensure it exists and get ID.
        if val_str in self.remote_registry.get(component_type, {}) or val_str in self.local_repo.get(component_type, {}):
            return self.ensure_component(component_type, val_str)
            
        return val_str

    def ensure_component(self, component_type: str, name: str) -> str:
        """
        Ensures a component exists remotely and returns its ID.
        """
        # 1. Check if already exists remotely
        if name in self.remote_registry.get(component_type, {}):
            item = self.remote_registry[component_type][name]
            id_map = {"tags": "tagId", "triggers": "triggerId", "variables": "variableId"}
            return item.get(id_map.get(component_type))

        # 2. Not found remotely, check local repo
        if name not in self.local_repo.get(component_type, {}):
            print(f"Warning: Dependency {component_type} '{name}' not found locally or remotely.")
            return name 

        # 3. Exists locally, need to create
        item = self.local_repo[component_type][name]
        print(f" -> Auto-creating dependency: {component_type[:-1]} '{name}'")
        
        processed_item = self._process_dependencies(component_type, item)
        cleaned_item = clean_item(processed_item)
        
        try:
            method_name = f"create_{component_type[:-1]}"
            new_item = getattr(self.client, method_name)(self.workspace_path, cleaned_item)
            
            # Update registries and local repo with the full remote object
            self.remote_registry[component_type][name] = new_item
            self.local_repo[component_type][name].update(new_item)
            
            id_map = {"tags": "tagId", "triggers": "triggerId", "variables": "variableId"}
            return new_item.get(id_map.get(component_type))
        except Exception as e:
            print(f"Error during auto-creation of {name}: {e}")
            raise e

    def _process_dependencies(self, component_type: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finds and resolves all name-based references within a component body.
        Detailed processing for tags, triggers, and variables.
        """
        processed = item.copy()
        
        if component_type == "tags":
            if "firingTriggerId" in processed:
                processed["firingTriggerId"] = [self.resolve_id("triggers", tid) for tid in processed["firingTriggerId"]]
            if "blockingTriggerId" in processed:
                processed["blockingTriggerId"] = [self.resolve_id("triggers", tid) for tid in processed["blockingTriggerId"]]
            if "setupTag" in processed and "setupTag" in processed and "tagName" in processed["setupTag"]:
                processed["setupTag"]["tagName"] = self.resolve_id("tags", processed["setupTag"]["tagName"])
            if "teardownTag" in processed and "teardownTag" in processed and "tagName" in processed["teardownTag"]:
                processed["teardownTag"]["tagName"] = self.resolve_id("tags", processed["teardownTag"]["tagName"])

        # Also process Data Layer Variables (DLVs) or other variable references in parameters
        if "parameter" in processed:
            # Note: Recurse or handle more fields if complex cases exist
            pass

        return processed

def main():
    parser = argparse.ArgumentParser(description="Import GTM items with content-based skipping and local updates.")
    parser.add_argument("--url", help="GTM Workspace URL")
    parser.add_argument("--account", help="GTM Account ID")
    parser.add_argument("--container", help="GTM Container ID")
    parser.add_argument("--workspace", help="GTM Workspace ID")
    parser.add_argument("--directory", help="Directory containing JSON files")
    
    args = parser.parse_args()
    load_env_file()
    
    client = GTMClient()
    
    account_id = args.account
    container_id = args.container
    workspace_id = args.workspace
    directory = args.directory

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
        
        if not directory:
            directory = os.path.join("tmp", public_id)

        print(f"Starting import to workspace: {workspace_path}")
        print(f"Input directory: {directory}")
        
        if not os.path.exists(directory):
            print(f"Error: Directory not found: {directory}")
            sys.exit(1)

        resolver = GTMDependencyResolver(client, workspace_path, directory)

        # 1. Built-in Variables
        built_in_vars = load_json(directory, "built_in_variables.json")
        if built_in_vars:
            print("Enabling built-in variables...")
            existing_built_ins = resolver.remote_registry["built_in_variables"]
            types_to_enable = [v['type'] for v in built_in_vars if v.get('type') not in existing_built_ins]
            if types_to_enable:
                try:
                    client.create_built_in_variables(workspace_path, types_to_enable)
                    print(f"Successfully enabled {len(types_to_enable)} built-in variables.")
                except Exception as e:
                    print(f"Warning: {e}")

        # 2. Main Components (Variables -> Triggers -> Tags)
        for ctype in ["variables", "triggers", "tags"]:
            local_map = resolver.local_repo[ctype]
            if not local_map:
                continue
                
            print(f"Processing {ctype}...")
            for name, item in local_map.items():
                remote_item = resolver.remote_registry[ctype].get(name)
                processed = resolver._process_dependencies(ctype, item)
                
                if remote_item:
                    # Content-based skip logic
                    if clean_item(processed) == clean_item(remote_item):
                        # Even if fingerprint is missing locally, if content matches, we're good
                        print(f" - Skipping {ctype[:-1]} '{name}' (content matches)")
                        # Still update local metadata (ID, fingerprint) from remote for future sync
                        item.update(remote_item)
                        continue
                        
                    print(f" - Updating {ctype[:-1]} '{name}'")
                    try:
                        method_name = f"update_{ctype[:-1]}"
                        new_item = getattr(client, method_name)(remote_item['path'], clean_item(processed))
                        item.update(new_item)
                    except Exception as e:
                        print(f"Error updating {name}: {e}")
                else:
                    print(f" - Creating {ctype[:-1]} '{name}'")
                    try:
                        # ensure_component will create if missing and update item in place
                        resolver.ensure_component(ctype, name)
                    except Exception as e:
                        print(f"Error creating {name}: {e}")

            # Save the updated list back to the JSON file
            original_list = getattr(resolver, f"{ctype}_list")
            save_json(directory, f"{ctype}.json", original_list)

        print("\nImport process completed. Local files updated.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


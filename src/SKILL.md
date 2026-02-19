---
name: gtm-copilot
description: A comprehensive skill for developing, managing, importing, and exporting Google Tag Manager configurations - GTM Copilot
license: MIT
compatibility: "python >= 3.x"
metadata:
  version: 0.0.1
  author: SEM Technology
  homepage: https://github.com/sem-technology/gtm-copilot
disable-model-invocation: false
allowed-tools:
  - run_command
  - list_dir
  - view_file
  - grep_search
  - codebase_search
---

# GTM Copilot Skill
This skill supports the entire Google Tag Manager (GTM) development workflow. All necessary tools and documentation are bundled within this skill directory.

## Directory Structure (Bundled Resources)
This skill is configured as a self-contained package. Agents must always use relative paths within this skill directory.

- `SKILL.md`: Skill definition (this file)
- `.env.example`: Template for environment variable settings
- `LICENSE.txt`: License information
- `scripts/`: Folder containing all program code
  - `bin/`: Executable scripts (auth.py, export.py, import.py)
  - `helpers/`: Utilities and client logic
  - `gtm_client.py`: Core implementation of the GTM API client
  - `authentication.py`: Authentication module
- `resources/`: Folder for supplemental documents and sample data
  - `tags.json`: Implementation sample for tags
  - `triggers.json`: Implementation sample for triggers
  - `variables.json`: Implementation sample for variables
  - `built_in_variables.json`: List of built-in variables

## Command Details
### 1. auth (Authentication Setup)
Performs OAuth2 authentication to access the GTM API.
- **Execution**: `python ./scripts/bin/auth.py`
- **Role**: Input Client ID/Secret and generate a refresh token.

### 2. export (State Extraction)
Exports existing GTM configurations as local JSON files.
- **Execution**: `python ./scripts/bin/export.py --url <GTM_WORKSPACE_URL>`
- **Output**: `./tmp/GTM-XXXXXX/`
- **Role**: Save the current state of tags, triggers, and variables as a snapshot for editing.

### 3. import (Change Synchronization)
Updates the GTM container based on local JSON files.
- **Execution**: `python ./scripts/bin/import.py --url <GTM_WORKSPACE_URL>`
- **Role**: 
  - Create new components
  - Update existing components (only if changes detected)
  - Automatically resolve ID references (from name-based to numeric IDs)

## Development Workflow
1. **Export**: Run `export.py` to get the latest GTM state.
2. **Implementation (AI Work)**: Modify the JSON files under `tmp/`.
   - Add new tags
   - Change trigger conditions
   - Fix variable definitions
3. **Import**: Run `import.py` to synchronize changes.
   - After sync, official IDs and `fingerprint` values are written back to local JSONs.

## Notes on JSON File Generation & Editing
- **Name-based References (Recommended)**: 
  - When specifying firing triggers for tags, you can use the "Trigger Name" instead of a numeric ID. This is especially useful for tags referencing newly created triggers that don't have IDs yet.
  - Use the `{{Variable Name}}` format to reference variables.
- **Dependency Resolution**:
  - If a new tag references a new trigger, the import script automatically detects the dependency and creates the trigger first.
- **Change Detection**:
  - The script compares content hashes and skips API calls if there are no actual changes.
- **Implementation References**:
  - Use the JSON files in the `resources/` directory (e.g., `tags.json`) as references for correct schemas and parameter structures.
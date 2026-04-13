---
name: gtm-copilot
description: A comprehensive skill for developing, managing, importing, and exporting Google Tag Manager configurations - GTM Copilot
license: MIT
compatibility: "python >= 3.x"
metadata:
  version: 0.2.0
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
  - `gtm_client.py`: Core implementation of the GTM API client
  - `authentication.py`: Authentication module
  - `helpers/`: Utilities and client logic
- `resources/`: Folder for supplemental documents and sample data
  - `documents/`: Documents for GTM Copilot
    - `audit_checkpoints.md`: Detailed audit criteria for GTM configurations
  - `server_container/`: Configuration for Server-side GTM
    - `tags.json`
    - `triggers.json`
    - `variables.json`
    - `built_in_variables.json`
  - `web_container/`: Configuration for Web GTM
    - `tags.json`
    - `triggers.json`
    - `variables.json`
    - `built_in_variables.json`

## Configuration
Environment variables are loaded from the `.env` file located in the project root.
- `GTM_CLIENT_ID`: OAuth 2.0 Client ID for GTM API access.
- `GTM_CLIENT_SECRET`: OAuth 2.0 Client Secret for GTM API access.
- `GTM_REFRESH_TOKEN`: OAuth 2.0 Refresh Token for automatic token renewal.
- `GTM_EXPORT_ROOT_PATH`: Environment variable to specify the root directory for GTM files.
  - **Placeholder**: Supports `[[GTM_ID]]` for dynamic path resolution based on the container ID.
  - **Resolution Priority**: CLI Argument > Env Var > Default (`tmp/[[GTM_ID]]`).

## Command Details
### 1. auth (Authentication Setup)
Performs OAuth2 authentication to access the GTM API.
- **Execution**: `python ./scripts/bin/auth.py`
- **Role**: Input Client ID/Secret and generate a refresh token.

### 2. export (State Extraction)
Exports existing GTM configurations as local JSON files.
- **Execution**: `python ./scripts/bin/export.py --url <GTM_WORKSPACE_URL>`
- **Output**: The path defined by `--output` or `GTM_EXPORT_ROOT_PATH` (defaults to `./tmp/GTM-XXXXXX/`).
- **Role**: Save the current state of tags, triggers, and variables as a snapshot for editing.

### 3. import (Change Synchronization)
Updates the GTM container based on local JSON files.
- **Execution**: `python ./scripts/bin/import.py --url <GTM_WORKSPACE_URL>`
- **Input**: The path defined by `--directory` or `GTM_EXPORT_ROOT_PATH` (defaults to `./tmp/GTM-XXXXXX/`).
- **Role**: 
  - Create new components
  - Update existing components (only if changes detected)
  - Automatically resolve ID references (from name-based to numeric IDs)

## Workflow
### Development Workflow
1. **Export**: Run `scripts/bin/export.py` to get the latest GTM state.
2. **Implementation (AI Work)**: Modify the JSON files under `tmp/`.
   - Add new tags
   - Change trigger conditions
   - Fix variable definitions
3. **Import**: Run `scripts/bin/import.py` to synchronize changes.
   - After sync, official IDs and `fingerprint` values are written back to local JSONs.

### Audit Workflow
1. **Export**: Run `scripts/bin/export.py` to get the latest GTM state.
2. **Audit**: 
   - The agent uses the `view_file` tool to read `resources/documents/audit_checkpoints.md` to understand the audit criteria.
   - The agent then analyzes the exported JSON files in `tmp/` based on those criteria.
3. **Report**: The agent provides a summary of findings (issues, risks, and recommendations) to the user.

**Crucial**: The agent must not modify any tags, triggers, or variables, nor perform any import operations, unless specifically instructed to do so by the user.

## Notes on JSON File Generation & Editing
- **Name-based References (Recommended)**: 
  - When specifying firing triggers for tags, you can use the "Trigger Name" instead of a numeric ID. This is especially useful for tags referencing newly created triggers that don't have IDs yet.
  - Use the `{{Variable Name}}` format to reference variables.
- **Dependency Resolution**:
  - If a new tag references a new trigger, the import script automatically detects the dependency and creates the trigger first.
- **Change Detection**:
  - The script compares content hashes and skips API calls if there are no actual changes.
- **Implementation References**:
  - Use the JSON files in the `resources/server_container/` or `resources/web_container/` directories as references for correct schemas and parameter structures.
  - **Important**: Available tags, triggers, and variables differ significantly between Server and Web containers. Ensure you reference the correct directory for your specific container type when implementing new components.
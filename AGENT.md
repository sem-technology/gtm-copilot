# AGENT.md - GTM Copilot Development Guide for AI Agents

This guide explains how to use the GTM development tools in this repository to export, customize, and import Google Tag Manager components.

## Prerequisites

- **Environment**: Ensure `.env` is configured with `GTM_CLIENT_ID`, `GTM_CLIENT_SECRET`, and `GTM_REFRESH_TOKEN`.
- **Dependencies**: Python 3.x with `google-auth` related libraries.

## Authentication Setup (OAuth 2.0)

Since this tool interacts with the GTM API on behalf of a user, it requires OAuth 2.0 credentials. External AI Agents must guide the human user through this process.

### Step 1: Google Cloud Project Setup (Human Action)
The human user must perform these steps in the [Google Cloud Console](https://console.cloud.google.com/):
1. **Create a Project**: Create a new GCP project or select an existing one.
2. **Enable GTM API**: Search for "Google Tag Manager API" and click **Enable**.
3. **Configure OAuth Consent Screen**:
    - Choose **External** user type.
    - Provide app information (app name, support email).
    - Add scopes: `.../auth/tagmanager.readonly`, `.../auth/tagmanager.edit.containers`, etc.
    - Add the user's email as a **Test User** (important!).
4. **Create Credentials**:
    - Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
    - Application type: **Web application**.
    - Authorized redirect URIs: `http://localhost:8000`.
    - Note down the **Client ID** and **Client Secret**.

### Step 2: Obtain Refresh Token (Agent & Human Interaction)
Once Client ID/Secret are ready, the Agent should run the following script and guide the human:

```bash
python src/bin/auth.py
```

**Guidance for the Agent:**
1. The script will ask for Client ID and Secret (or read them from `.env`).
2. It will generate a **URL**. Provide this URL to the human and ask them to open it in their browser.
3. The human will authorize the app and be redirected to a page that may fail to load (since no server is running on localhost:8000), but the URL will contain a `code=` parameter.
4. Ask the human to copy the value of the `code` parameter from the address bar.
5. Enter the code into the script prompt.
6. The script will output the `GTM_REFRESH_TOKEN`.

### Step 3: Finalize .env
The Agent (if it has write access) or the human should update the `.env` file:
```text
GTM_CLIENT_ID=your_client_id
GTM_CLIENT_SECRET=your_client_secret
GTM_REFRESH_TOKEN=your_refresh_token
```

---

## Workflow Overview

### 1. Exporting GTM State
To get the latest state of a GTM workspace, use `src/bin/export.py`. You can provide individual IDs or simply the **Workspace URL**.

**Option A: Using Workspace URL (Recommended)**
```bash
python src/bin/export.py --url https://tagmanager.google.com/#/container/accounts/[ACCOUNT_ID]/containers/[CONTAINER_ID]/workspaces/[WORKSPACE_ID]
```
*Note: This will automatically create and export to `tmp/GTM-XXXXXX/` based on the container's Public ID.*

**Option B: Using Individual IDs**
```bash
python src/bin/export.py --account [ACCOUNT_ID] --container [CONTAINER_ID] --workspace [WORKSPACE_ID] --output tmp/GTM-MY_WORKDIR
```

This creates four JSON files: `tags.json`, `triggers.json`, `variables.json`, and `built_in_variables.json`.

---

### 2. Customizing Components
You can modify the JSON files directly. 

#### Name-based ID Resolution
The `import.py` script supports **name-based references**. Instead of hunting for numeric GTM IDs, you can use the component name:

- **Tags**: In `firingTriggerId` or `blockingTriggerId`, you can use the **Trigger Name** instead of the ID.
- **Variables**: Use `{{Variable Name}}` in any template or string field.
- **Setup/Teardown Tags**: Use the **Tag Name** in the `setupTag.tagName` field.

#### Tips for New Components
- When creating a new component, you don't need to provide `path`, `tagId`, `fingerprint`, etc. These will be automatically populated by the import script.
- Ensure `name` and `type` are correctly set.

---

### 3. Importing Changes
To sync your local changes to GTM, use `bin/import.py`.

**Option A: Using Workspace URL (Recommended)**
```bash
python src/bin/import.py --url https://tagmanager.google.com/#/container/accounts/[ACCOUNT_ID]/containers/[CONTAINER_ID]/workspaces/[WORKSPACE_ID]
```
*Note: This will automatically look for JSON files in `tmp/GTM-XXXXXX/` based on the container's Public ID.*

**Option B: Using Individual IDs**
```bash
python src/bin/import.py --account [ACCOUNT_ID] --container [CONTAINER_ID] --workspace [WORKSPACE_ID] --directory [DIR_PATH]
```

#### Smart Synchronization Features
- **Content-Based Skipping**: The script compares the *actual settings* of the component. If the local content matches the remote content, it will skip the update even if the `fingerprint` property is missing or different.
- **Automatic Local Sync**: Successfully imported/created components are updated in the local JSON files.
    - **ID Resolution**: Temporary "Name-based IDs" are replaced with actual numeric IDs.
    - **Metadata population**: `fingerprint`, `path`, and `tagId` are added back to the JSON files.
- **Dependency Resolution**: If you add a Tag that references a new Trigger (by name), the script will automatically create the Trigger first.

---

### 4. Best Practices for Agents
- **Always Export First**: Before making changes, export the current state to a temporary directory to ensure you are working on the latest version.
- **Verify after Import**: After running `src/bin/import.py`, inspect the local JSON files to confirm that names have been replaced by numeric IDs.
- **Avoid Manual Metadata Edits**: Don't manually edit IDs or fingerprints unless you specifically want to force/manipulate sync behavior. Let the script handle it.

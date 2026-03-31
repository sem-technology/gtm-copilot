# GTM Copilot

This project focuses on building programs and prompts to automate Google Tag Manager (GTM) implementation tasks using AI.

## How it Works

1. **Extraction**: Using the Google Tag Manager API, the tool retrieves existing components such as tags, triggers, and variables, and saves them in JSON format.
2. **AI-Powered Modification**: AI is used to update the JSON files, performing the actual tag implementation logic within the files.
3. **Synchronization**: Once the implementation (JSON editing) is complete, the changes are synced back to Google Tag Manager using the API.

## Architecture

To ensure portability and ease of setup, this project is implemented using **only the Python standard library**. No external dependencies (such as `requests` or `google-auth`) are required.

- **Programming Language**: Python 3.x (Standard Library only)

## Setup (Agent Skills)

To use GTM Copilot as an AI Agent skill, follow these steps:

1. **Download**: Clone this repository into your agent's skill directory.

   **For Claude Code:**
   ```sh
   # User-level
   git clone https://github.com/sem-technology/gtm-copilot.git ~/.claude/skills/gtm-copilot
   # Project-level
   git clone https://github.com/sem-technology/gtm-copilot.git .claude/skills/gtm-copilot
   ```

   **For Gemini (including Antigravity):**
   ```sh
   # User-level
   git clone https://github.com/sem-technology/gtm-copilot.git ~/.agent/skills/gtm-copilot
   # Project-level
   git clone https://github.com/sem-technology/gtm-copilot.git .agent/skills/gtm-copilot
   ```

2. **Authentication**: 
   - Copy `.env.example` to `.env` in the skill directory.
   - Run the authentication script to generate your refresh token:
     ```sh
     python scripts/bin/auth.py
     ```
   - Follow the prompts to authorize and update the values in your `.env` file.

3. **Usage**: Once placed and authenticated, your AI Agent will automatically recognize the tools defined in `SKILL.md` and can start automating your GTM workflow.

For more information on Agent Skills, please refer to [agentskills.io](https://agentskills.io/home).

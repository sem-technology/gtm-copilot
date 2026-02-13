# AI GTM Developer

This project focuses on building programs and prompts to automate Google Tag Manager (GTM) implementation tasks using AI.

## How it Works

1. **Extraction**: Using the Google Tag Manager API, the tool retrieves existing components such as tags, triggers, and variables, and saves them in JSON format.
2. **AI-Powered Modification**: AI is used to update the JSON files, performing the actual tag implementation logic within the files.
3. **Synchronization**: Once the implementation (JSON editing) is complete, the changes are synced back to Google Tag Manager using the API.

## Architecture

To ensure portability and ease of setup, this project is implemented using **only the Python standard library**. No external dependencies (such as `requests` or `google-auth`) are required.

- **Programming Language**: Python 3.x (Standard Library only)
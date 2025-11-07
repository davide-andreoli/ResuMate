# ResuMate

Welcome to ResuMate, your intelligent companion for the entire job application process.

ResuMate helps you craft the perfect resume by allowing you to input your professional experience, experiment with different templates, and chat with AI agents that offer personalized feedback and edits.

## Features

### Core Features

- Add and manage your professional experience
- Render your resume using multiple customizable templates

### Agent specific features:

- Chat with an AI agent about your resume
- Receive suggestions on how to improve specific sections
- Allow the agent to directly modify your resume

## Installation and setup

Once you have cloned the repository, you should proceed by installing the package and depdendencies with the following command:

```sh
poetry install
poetry run playwright install chromium
```

Note: Chromium is required for PDF rendering and must be installed via Playwright.

Next, create a .env file in the project root. It should look something like this (see the Settings section for details on each value):

```env
AGENT_PROVIDER=
AGENT_CREDENTIALS_FILE=
AGENT_PROJECT_ID=
AGENT_MODEL_NAME=
```

## Running ResuMate

Once setup is complete, you can start ResuMate in a few different ways:

- run `resumate` in your terminal: this is the easiest way to run the program, it will startup both the backend and the frontend, and it will open the frontend in a browser window
- run `resumate-backend` in your terminal: this will start only the backend server, which you can try out via the swagger interface
- run `resumate-frontend` in your terminal: this will start only the frontend server and it will open it in a browser window

## Settings

Settings are managed with Pydantic Settings, you can find below the comprehensive list of what you are able to customize.

| Variable                 | Description                                    | Example / Notes                              |
| ------------------------ | ---------------------------------------------- | -------------------------------------------- |
| `AGENT_PROVIDER`         | The LLM provider to use                        | Currently, only `google-vertex` is supported |
| `AGENT_CREDENTIALS_FILE` | Path to your Google Vertex AI credentials file | e.g. `/path/to/credentials.json`             |
| `AGENT_PROJECT_ID`       | Google Cloud project ID                        | Required for Google Vertex                   |
| `AGENT_MODEL_NAME`       | LLM model name                                 | Only **Google Gemini** models are supported  |


## Formats

- experience data: Stored in a simple, portable .yaml file that’s easy to read and edit.
- templates: built using Jinja — you can use the provided templates or create your own.

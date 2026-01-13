# Architecture & Project Structure

## Overview

This project follows a clean separation of concerns architecture with the following core responsibilities:

1. **Configuration Management** - Environment and settings loader
2. **AI Content Generation** - LLM-based email content creation
3. **Email Delivery** - Gmail SMTP integration
4. **Orchestration** - Scheduled execution and workflow management
5. **User Interface** - Optional Streamlit-based UI

---

## Directory Structure

```

gmail-random-mailer/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
│
└── src/
    ├── app.py                  # Streamlit UI: recipient config, execution control, logs
    ├── main.py                 # CLI entrypoint: accepts recipient/count/interval params
    │
    ├── config/
    │   ├── settings.py         # Environment loader, validation, settings singleton
    │   └── prompts.py          # LLM system prompts and templates
    │
    ├── ai/
    │   └── generator.py        # OpenAI API client, returns subject + body
    │
    ├── mail/
    │   ├── gmail_smtp.py       # SMTP client (smtp.gmail.com:587, TLS) + message builder
    │   └── models.py           # Data models: EmailContent, RunConfig
    │
    └── core/
        ├── runner.py           # Orchestration layer: generate → send → schedule loop
        └── logger.py           # Centralized logging utility
```

## Component Responsibilities

### Configuration Layer (`config/`)

- **settings.py**: Validates and exposes environment variables as typed configuration objects
- **prompts.py**: Centralizes LLM prompt engineering and template management

### AI Layer (`ai/`)

- **generator.py**: Abstracts OpenAI API interactions, implements retry logic and error handling

### Mail Layer (`mail/`)

- **gmail_smtp.py**: Handles SMTP authentication, connection pooling, and message transmission
- **models.py**: Defines domain models for email content and execution configuration

### Core Layer (`core/`)

- **runner.py**: Implements execution workflow, state management, and graceful shutdown
- **logger.py**: Provides structured logging for both CLI and UI contexts

### Application Layer

- **main.py**: CLI interface with argument parsing
- **app.py**: Interactive Streamlit dashboard for non-technical users

---

## Design Principles

- **Modularity**: Each component has a single, well-defined responsibility
- **Testability**: Dependencies are injected, enabling easy mocking and unit testing
- **Configurability**: All external dependencies configurable via environment variables
- **Extensibility**: Plugin-ready architecture for alternative AI providers or email services

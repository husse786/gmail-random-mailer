# Gmail Random Mailer

Automatically sends test emails via **Gmail SMTP** using AI-generated content from **OpenAI API**. This tool is designed for repeatable testing of email inbox processing and monitoring systems.

---

## Features

- Gmail SMTP sending (TLS) with App Password authentication
- AI-generated unique **Subject** and **Body** for each email via OpenAI
- Configurable interval-based sending (e.g., every 2 minutes)
- Send **N** emails with customizable count
- Optional Streamlit UI for easy configuration
- CLI support for automation

---

## Prerequisites

1. **Python 3.10+**
2. **Gmail App Password** - [Learn how to create one](https://support.google.com/accounts/answer/185833)
3. **OpenAI API Key** - [Get your API key](https://platform.openai.com/api-keys)
4. VS Code (recommended)

---

## Setup

### 1) Clone and Create Virtual Environment

```bash
git clone https://github.com/husse786/gmail-random-mailer.git
cd gmail-random-mailer
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell
```

### 2) Install Dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
GMAIL_ADDRESS=yourname@gmail.com
GMAIL_APP_PASSWORD=your_app_password
OPENAI_MODEL=gpt-3.5-turbo
DEFAULT_INTERVAL_SECONDS=120
```

---

## Usage

### Option 1: Streamlit UI

```bash
streamlit run src/app.py
```

### Option 2: Command Line

```bash
python src/main.py --to recipient@example.com --count 10 --interval 120
```

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `GMAIL_ADDRESS` | Your Gmail address | Yes |
| `GMAIL_APP_PASSWORD` | Gmail App Password | Yes |
| `OPENAI_MODEL` | OpenAI model to use | No (default: gpt-3.5-turbo) |
| `DEFAULT_INTERVAL_SECONDS` | Default interval between emails | No (default: 120) |

---

## License

MIT

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# Ask AI — Streamlit + OpenAI

A friendly, responsive chat app built with Python, Streamlit, and the OpenAI API.

## Features

- Chat interface with conversation history
- Selectable OpenAI model
- Answer style options: Balanced, Concise, Detailed, Beginner-friendly
- Creativity control
- API key entry in the sidebar for local testing
- Supports `.env` locally and Streamlit Secrets when deployed
- Responsive layout and clear error messaging

## 1. Requirements

- Python 3.10 or newer
- An OpenAI API key with API billing/access enabled

## 2. Run locally

Unzip the project and open a terminal in the project folder.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in a text editor and replace `your_openai_api_key_here` with your real key.

Then start the app:

```powershell
streamlit run app.py
```

Your browser should open automatically. If it does not, visit the local URL printed in the terminal (usually `http://localhost:8501`).

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, then run:

```bash
streamlit run app.py
```

## 3. Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload these project files. **Do not upload `.env` or your API key.**
2. Sign in to Streamlit Community Cloud and create a new app from the repository.
3. Set the main file path to `app.py`.
4. Open the app's **Settings → Secrets** and add:

```toml
OPENAI_API_KEY = "your-real-api-key"
```

5. Deploy or reboot the app.

The app reads `OPENAI_API_KEY` from Streamlit Secrets through the environment only if Streamlit exposes it as an environment variable. If your deployment does not expose secrets as environment variables, update the key initialization in `app.py` to read `st.secrets.get("OPENAI_API_KEY", "")` as a fallback. A safe replacement is:

```python
api_key = st.text_input(
    "OpenAI API key",
    value=os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", "")),
    type="password",
)
```

For deployments using the fallback above, keep the `.streamlit/secrets.toml` file out of GitHub.

## 4. Security notes

- Never commit your API key to GitHub or include it in the ZIP.
- For a public app, do not rely on users entering their own key unless that is your intended product design.
- API usage may incur charges. Consider authentication, usage limits, rate limiting, and budget alerts before sharing publicly.
- Avoid logging API keys or sensitive user prompts.
- The app currently keeps chat history in the active Streamlit session; it does not save conversations to a database.

## Troubleshooting

- **401 / authentication error:** check that the API key is correct and active.
- **Model not found / access error:** select a model your API project can access.
- **Rate limit / quota error:** check API billing, project limits, and usage.
- **Package issue:** upgrade pip and reinstall with `pip install -r requirements.txt`.

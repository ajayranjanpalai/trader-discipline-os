# Trader Discipline OS

A Flask web application for trade journaling, discipline tracking, risk management,
expenses, daily tasks, analytics, and behavioural trading insights.

## Technology

- Flask and SQLAlchemy backend
- HTML, CSS, and JavaScript frontend
- SQLite for local development
- PostgreSQL for production

## Run locally

Requires Python 3.12 or newer.

1. Copy the environment template and update the values:

```powershell
copy .env.example .env
```

2. Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Start the app:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

If you prefer not to use `.env`, set `SECRET_KEY`, `JWT_SECRET_KEY`, and `DATABASE_URL` as environment variables before running.

The local `database.db` file and environment secrets are intentionally excluded
from Git.

## Deploy globally (cloud hosting)

To deploy the app so it runs continuously on the internet, use a cloud platform such
as Render, Heroku, or another Python-capable host. Once deployed, the service stays
online and you do not need to manually start the server.

### Recommended: Render

1. Create a Render PostgreSQL database.
2. Create a new **Blueprint** in Render and connect this GitHub repository.
3. Render reads `render.yaml` and creates the web service.
4. When prompted for `DATABASE_URL`, use the database's **Internal Database URL**.
5. Deploy the Blueprint.

Render will keep the app running and provide a public URL.

### Alternative: Heroku or similar

1. Push your repo to GitHub.
2. Create a new app on the host platform.
3. Configure the build command and start command if needed:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn --workers 1 --threads 4 --timeout 120 app:app
```

4. Add environment variables:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - Optional email settings from `.env.example`

This project already includes a `Procfile` for cloud hosts that use Gunicorn.

### Important production notes

- Use PostgreSQL for production, not SQLite.
- Do not commit `database.db`, `.env`, passwords, tokens, or API keys.
- The in-process noon email scheduler is only started by `python app.py`; it is not
  started by the production Gunicorn command. Use a separate scheduled job if you
  want noon notification emails in production.

## Production notes

- Do not commit `database.db`, `.env`, passwords, tokens, or API keys.
- Render's default service filesystem is temporary, so PostgreSQL should be used
  instead of SQLite for production data.
- The in-process noon email scheduler is only started by `python app.py`; it is not
  started by the production Gunicorn command. Use a dedicated scheduled job before
  relying on noon notification emails in production.

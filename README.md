# Business Finance Dashboard 📊

Secure Streamlit dashboard with Trino database integration for daily business metrics.

## Features ✨

- 🔐 Password-protected authentication
- 📊 Real-time KPI dashboards
- 📈 Interactive Plotly charts
- 💾 Trino database integration
- 🔄 Auto-refresh with caching
- 📱 Responsive design

## Quick Setup 🚀

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Create `.streamlit/secrets.toml`:

```toml
[trino]
host = "your-trino-host.com"
port = 443
user = "your-username"
password = "your-password"
catalog = "your-catalog"
schema = "your-schema"

[auth]
admin = "admin-password"
user1 = "user1-password"
user2 = "user2-password"
```

**⚠️ NEVER commit secrets.toml to git!**

### 3. Run Locally

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Deploy from your repository
4. Add secrets in Settings → Secrets
5. Done! 🎉

## Project Structure

```
finance_dashboard/
├── app.py              # Main dashboard
├── queries.py          # SQL query templates
├── requirements.txt    # Dependencies
├── .streamlit/
│   └── config.toml    # Streamlit config
└── .gitignore         # Ignore secrets
```

## Security 🔒

- All credentials stored in secrets (never in code)
- Password-protected dashboard
- Private repository recommended
- Regular password rotation advised

## Customization

### Add Your Queries

Edit `queries.py` with your actual Trino queries:

```python
SOUNDBOX_DAILY = """
    SELECT * FROM your_table
    WHERE date >= CURRENT_DATE - INTERVAL '30' DAY
"""
```

### Add Users

Update secrets:

```toml
[auth]
newuser = "newpassword"
```

Then update `app.py`:

```python
def get_users():
    return {
        "newuser": hash_password(st.secrets["auth"]["newuser"]),
        # ... other users
    }
```

## Support

For issues or questions, check:
- Streamlit docs: https://docs.streamlit.io/
- Trino docs: https://trino.io/docs/

---

**Made with ❤️ for PPSL**

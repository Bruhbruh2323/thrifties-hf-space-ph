
# THRIFTIES — Trendy Fashion Marketplace (Hugging Face Space)

A stylish, livestream-ready, pre-loved fashion marketplace built with **Streamlit**.

**Key features**
- Shop catalog with filters, cart, checkout simulation
- Live tab with event schedule and video placeholder
- Seller onboarding & listing form + Academy quiz & auto-certificate
- Orders page with simulated tracking
- Admin analytics & eCRM event logging
- Sustainability counters (items reused, eco packaging %)

## Deploy to Hugging Face Spaces
1. Create a new Space → **Streamlit** → Python 3.10+
2. Upload the contents of this folder (or connect to this repo).
3. Ensure `requirements.txt` is present. Spaces will auto-install.
4. Set **Secrets** (optional): `APP_NAME`, `ADMIN_PASSWORD` etc in the Space Settings → Secrets.
5. Click **Run**.

## Local run
```bash
pip install -r requirements.txt
streamlit run app.py
```


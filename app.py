
import os, json, io, time, datetime as dt
import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt

APP_NAME = os.getenv("APP_NAME", "THRIFTIES")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "thrifties-admin")

# ---------- THEME / CSS ----------
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title=f"{APP_NAME} — Pre-loved Fashion Marketplace", page_icon="🛍️", layout="wide")

# ---------- STATE ----------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "events" not in st.session_state:
    st.session_state.events = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "academy_score" not in st.session_state:
    st.session_state.academy_score = None

# ---------- UTILS ----------
DATA_PRODUCTS = "data/products.json"
DATA_EVENTS = "data/events.csv"

def log_event(event: str, meta: dict=None):
    # in-memory + csv append
    ts = dt.datetime.utcnow().isoformat()
    user = st.session_state.user_name or "guest"
    st.session_state.events.append({"timestamp": ts, "event": event, "user": user, "meta": meta or {}})
    try:
        with open(DATA_EVENTS, "a") as f:
            f.write(f"{ts},{event},{user},{json.dumps(meta or {})}\n")
    except Exception:
        pass

@st.cache_data
def load_products():
    with open(DATA_PRODUCTS) as f:
        return json.load(f)

@st.cache_data
def df_products():
    return pd.DataFrame(load_products())

# ---------- HEADER ----------
colL, colR = st.columns([3,2])
with colL:
    st.markdown("""
    <div class='navpill'>
    <b>THRIFTIES</b> · Reuse · Rewear · Relove
    </div>
    """, unsafe_allow_html=True)
with colR:
    st.text_input("Enter your name (for personalized experience)", key="user_name", placeholder="e.g., Kai")

st.markdown("\n")

# ---------- NAV ----------
tabs = st.tabs(["🛒 Shop", "📺 Live", "🧑‍💼 Sell", "🎓 Academy", "📦 Orders", "🛠️ Admin"])

# ---------- SHOP TAB ----------
with tabs[0]:
    log_event("view_shop")
    st.subheader("Discover pre-loved fits ✨")
    df = df_products()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        q = st.text_input("Search", placeholder="denim, dress, retro…")
    with col2:
        cat = st.selectbox("Category", options=["All"] + sorted(df["category"].unique().tolist()))
    with col3:
        size = st.selectbox("Size", options=["All"] + sorted(df["size"].unique().tolist()))
    with col4:
        sort = st.selectbox("Sort by", options=["Newest", "Price ↑", "Price ↓"])    

    filt = df.copy()
    if q:
        mask = filt["title"].str.contains(q, case=False) | filt["tags"].astype(str).str.contains(q, case=False)
        filt = filt[mask]
    if cat != "All":
        filt = filt[filt["category"]==cat]
    if size != "All":
        filt = filt[filt["size"]==size]
    if sort == "Price ↑":
        filt = filt.sort_values("price")
    elif sort == "Price ↓":
        filt = filt.sort_values("price", ascending=False)

    st.markdown("---")

    # Render product cards
    for _, row in filt.iterrows():
        c1, c2 = st.columns([2,3])
        with c1:
            st.markdown("""
            <div class='card'>
            <span class='badge'>{} · {} · size {}</span>
            <h3 style='margin-top:8px'>{}</h3>
            <div class='price'>₱{:.2f}</div>
            <p class='muted'>Condition: {} · Seller: {}</p>
            <p class='muted'>♻️ {}</p>
            </div>
            """.format(row.category, row.brand, row.size, row.title, row.price, row.condition, row.seller, row.sustainable_note), unsafe_allow_html=True)
        with c2:
            st.button("Add to cart", key=f"add_{row.id}", on_click=lambda r=row: (st.session_state.cart.append(dict(r)), log_event("add_to_cart", {"item": r.id})))
            st.button("Wishlist ❤️", key=f"wish_{row.id}", on_click=lambda r=row: log_event("wishlist", {"item": r.id}))
            st.button("Notify me 🔔", key=f"notify_{row.id}", on_click=lambda r=row: log_event("notify", {"item": r.id}))
        st.markdown("---")

    # Cart drawer
    st.subheader("🧺 Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        total = sum([x["price"] for x in st.session_state.cart])
        for item in st.session_state.cart:
            st.write(f"• {item['title']} — ₱{item['price']:.2f}")
        st.write(f"**Total:** ₱{total:.2f}")
        name = st.text_input("Full name")
        addr = st.text_area("Delivery address")
        pay = st.selectbox("Payment method (simulated)", ["COD", "GCash", "Card"])
        if st.button("Checkout"):
            log_event("checkout", {"total": total, "pay": pay})
            st.success("Order placed! You'll see it under Orders with tracking.")

# ---------- LIVE TAB ----------
with tabs[1]:
    log_event("view_live")
    st.subheader("Upcoming live streams & replays")
    st.write("Our live events recreate the ukay-ukay vibe online — real-time claim & chat. (Demo placeholder)")
    st.video("https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
    st.info("Tip: On production, replace with your own livestream/replay URLs.")

    st.markdown("### Schedule")
    sched = pd.DataFrame([
        {"Event": "Payday Super-Stream", "Date": "Dec 15, 8PM", "Host": "EcoFits PH"},
        {"Event": "Vintage Denim Drop", "Date": "Dec 18, 7PM", "Host": "Kai's Closet"},
    ])
    st.dataframe(sched, use_container_width=True)

# ---------- SELL TAB ----------
with tabs[2]:
    log_event("view_sell")
    st.subheader("Seller onboarding & quick listing")
    st.write("Complete the form to list a product. Moderation applies.")
    with st.form("sell_form"):
        title = st.text_input("Title")
        brand = st.text_input("Brand")
        category = st.selectbox("Category", ["Top", "Dress", "Bottom", "Outerwear", "Shoes", "Accessories"])    
        size = st.text_input("Size")
        condition = st.selectbox("Condition", ["Like new", "Gently used", "Good", "Well-loved"])    
        price = st.number_input("Price (PHP)", min_value=0.0, step=1.0)
        seller = st.text_input("Seller name")
        note = st.text_input("Sustainability note", value="Rewear to reduce textile waste")
        img = st.file_uploader("Upload photo (optional)", type=["png","jpg","jpeg"])
        submitted = st.form_submit_button("Submit listing")
    if submitted:
        new = {
            "id": f"THR-{int(time.time())}",
            "title": title, "brand": brand, "category": category, "size": size,
            "condition": condition, "price": float(price), "currency": "PHP",
            "seller": seller, "sustainable_note": note, "images": [], "tags": []
        }
        # save to products.json
        data = load_products()
        data.append(new)
        with open(DATA_PRODUCTS, "w") as f:
            json.dump(data, f, indent=2)
        st.cache_data.clear()
        log_event("seller_submit", {"item": new["id"]})
        st.success("Listing submitted! It now appears in Shop.")

# ---------- ACADEMY TAB ----------
with tabs[3]:
    log_event("view_academy")
    st.subheader("Thrifties Academy — Certification Quiz")
    st.caption("Based on CRM → eCRM best practices: automation, multi-channel, data privacy, and logistics integration.")
    q1 = st.radio("Which is a key difference between eCRM and traditional CRM?", [
        "Manual records only",
        "Multi-channel automation & real-time data",
        "Limited to phone support"
    ])
    q2 = st.radio("Which operational process benefits most from eCRM?", [
        "Paper-based filing",
        "Automated order tracking & feedback",
        "Single-store visits"
    ])
    q3 = st.radio("Which is *critical* to trust & safety?", [
        "Ignoring privacy concerns",
        "Data privacy compliance (DPA) & secure payments",
        "Posting without moderation"
    ])
    q4 = st.radio("Effective live selling requires…", [
        "Long delays",
        "Real-time chat, claim/hold mechanics, vouchers",
        "No analytics"
    ])
    q5 = st.radio("Post-purchase eCRM action: ", [
        "Discard feedback",
        "Prompt reviews & integrate insights",
        "Hide tracking"
    ])
    answers = [q1, q2, q3, q4, q5]
    if st.button("Finish & generate certificate"):
        score = sum([
            answers[0]=="Multi-channel automation & real-time data",
            answers[1]=="Automated order tracking & feedback",
            answers[2]=="Data privacy compliance (DPA) & secure payments",
            answers[3]=="Real-time chat, claim/hold mechanics, vouchers",
            answers[4]=="Prompt reviews & integrate insights",
        ])
        st.session_state.academy_score = score
        log_event("academy_complete", {"score": score})
        # generate simple DOCX certificate
        doc = Document()
        doc.add_heading("Thrifties Academy Certificate", 0)
        p = doc.add_paragraph(f"Awarded to {st.session_state.user_name or 'Participant'} on {dt.date.today().isoformat()}.")
        p = doc.add_paragraph(f"Score: {score}/5")
        p = doc.add_paragraph("Focus areas: eCRM automation, logistics tracking, privacy & trust, live selling operations, feedback loops.")
        for paragraph in doc.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(12)
        bio = io.BytesIO()
        doc.save(bio)
        st.download_button("Download certificate (.docx)", data=bio.getvalue(), file_name="Thrifties_Certificate.docx")
        st.success("Congrats! You're certified.")

# ---------- ORDERS TAB ----------
with tabs[4]:
    log_event("view_orders")
    st.subheader("Track your orders")
    st.write("This is a demo tracker for orders placed in this session.")
    if st.button("Simulate order status progression"):
        for pct in [0, 35, 70, 100]:
            st.progress(pct)
            st.write(["Processing", "Packed", "In transit", "Delivered"][min(pct//35,3)])
            time.sleep(0.4)
        log_event("order_delivered")

# ---------- ADMIN TAB ----------
with tabs[5]:
    log_event("view_admin")
    st.subheader("Admin & Analytics")
    pwd = st.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Admin unlocked")
        ev = pd.DataFrame(st.session_state.events)
        st.dataframe(ev, use_container_width=True)
        st.download_button("Export events CSV", data=ev.to_csv(index=False), file_name="events_export.csv")
        st.write("Products")
        st.dataframe(df_products(), use_container_width=True)
        # sustainability counters (demo)
        items_reused = len(df_products())
        eco_pct = 0.8
        st.markdown(f"<div class='counter'>♻️ Items reused: <b>{items_reused}</b> · 🌱 Eco-packaging: <b>{int(eco_pct*100)}%</b></div>", unsafe_allow_html=True)
    else:
        st.info("Enter admin password to view analytics.")

st.markdown("\n")
st.caption("Demo app — payments/logistics are simulated for classroom & prototyping use.")

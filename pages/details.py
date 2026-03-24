import streamlit as st

st.set_page_config(page_title="Movie Details", page_icon="🎬", layout="wide")

st.markdown("""
<style>
.big-title {
    font-size: 36px;
    font-weight: bold;
    color: #FF4B4B;
}

.rating {
    font-size: 18px;
    font-weight: bold;
    color: #FFD700;
}

.box {
    padding: 15px;
    border-radius: 12px;
    font-size: 15px;
    line-height: 1.6;
    max-height: 250px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

if "movie_data" not in st.session_state:
    st.warning("No movie selected")
    st.stop()

data = st.session_state["movie_data"]

left, right = st.columns([1, 2.5])

with left:
    st.image(data["poster"], width=250)

with right:
    st.markdown(f'<div class="big-title">{data["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rating">⭐ {data["rating"]} / 10</div>', unsafe_allow_html=True)
    st.write(f"📊 Similarity: {data['score']}%")

    st.write("")
    st.markdown("### 🧾 Overview")
    st.markdown(f'<div class="box">{data["overview"]}</div>', unsafe_allow_html=True)

st.divider()

st.markdown("### 🎥 Trailer")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if data["trailer"]:
        st.video(data["trailer"])
    else:
        st.info("Trailer not available")

st.write("")
if st.button("⬅ return"):
    st.switch_page("app.py")
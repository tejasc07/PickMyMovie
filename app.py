import streamlit as st
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb')) 

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"


def recommend(movie, n):
    if movie not in movies['title'].values:
        return [], []

    idx = movies[movies['title'] == movie].index[0]
    dist = similarity[idx]

    movies_list = sorted(
        list(enumerate(dist)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

    names = []
    posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters

#ui
st.set_page_config(page_title="PickMyMovie", page_icon="🎥", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #FF4B4B;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: gray;
        margin-bottom: 30px;
    }
    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">PickMyMovie 🎬</div>', unsafe_allow_html=True)
st.write('Find movies youll love in seconds')
st.write("")

selected_movie = st.selectbox(
    "Choose a movie 🍿",
    movies['title'].values
)

st.write("")

num_movies = st.slider(
    "Pick your movie count",
    min_value=1,
    max_value=8,
    value=4
)

st.write("")

if st.button("Recommend ✨"):
    with st.spinner("Finding best recommendations..."):
        names, posters = recommend(selected_movie, num_movies)

    if not names:
        st.error("Movie not found")
    else:
        cols_per_row = 4 

        for i in range(0, len(names), cols_per_row):
            cols = st.columns(cols_per_row)

            for j in range(cols_per_row):
                if i + j < len(names):
                    with cols[j]:
                        st.image(posters[i + j])
                        st.caption(names[i + j])
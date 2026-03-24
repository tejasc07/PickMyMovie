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

# fetching poster using id
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

# fetching details using id
def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        data = requests.get(url).json()

        rating = data.get('vote_average', 'N/A')
        overview = data.get('overview', 'No description available')

        return rating, overview
    except:
        return "N/A", "Error fetching overview"

# fetching trailer
def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
        data = requests.get(url).json()

        for video in data.get('results', []):
            if video['type'] == 'Trailer' and video['site'] == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
            
        return None
    except:
        return None

# main recommend function
def recommend(movie, n):
    try:
        if movie not in movies['title'].values:
            return [], [], [], [], [], []

        idx = movies[movies['title'] == movie].index[0]
        dist = similarity[idx]

        movies_list = sorted(
            list(enumerate(dist)),
            reverse=True,
            key=lambda x: x[1]
        )[1:n+1]

        names, posters, ratings, overviews, trailers, scores = [], [], [], [], [], []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            
            names.append(movies.iloc[i[0]].title)
            posters.append(fetch_poster(movie_id))

            rating, overview = fetch_details(movie_id)
            ratings.append(rating)
            overviews.append(overview)

            trailers.append(fetch_trailer(movie_id))
            scores.append(round(i[1]*100, 2))

        return names, posters, ratings, overviews, trailers, scores
    
    except:
        return [], [], [], [], [], []

#------------------------------------------UI---------------------------------------------------#
st.set_page_config(page_title="PickMyMovie", page_icon="🎥", layout="wide")

st.markdown("""
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        font-size: 15px;
        color: gray;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">PickMyMovie 🎬</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find movies youll love in seconds<div/>', unsafe_allow_html=True)
st.write("")

selected_movie = st.selectbox(
    "Choose a movie 🍿",
    movies['title'].values
)

st.write("")

num_movies = st.slider(
    "Pick your movie count",
    min_value=1,
    max_value=10,
    value=5
)

st.write("")

if st.button("Recommend ✨"):
    with st.spinner("picking the best ones..."):
        names, posters, ratings, overviews, trailers, scores = recommend(selected_movie, num_movies)

    if not names:
        st.error("Movie not found")
    else:
        st.session_state["results"] = (names, posters, ratings, overviews, trailers, scores)

st.write("")

if "results" in st.session_state:
    names, posters, ratings, overviews, trailers, scores = st.session_state["results"]
else:
    names, posters, ratings, overviews, trailers, scores = [], [], [], [], [], []

if "results" in st.session_state:
    names, posters, ratings, overviews, trailers, scores = st.session_state["results"]

    cols_per_row = 5

    for i in range(0, len(names), cols_per_row):
        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):
            if i + j < len(names):
                idx = i + j

                with cols[j]:
                    st.image(posters[idx])
                    st.caption(names[idx])

                    if st.button("more", key=f"btn_{idx}"):
                        st.session_state["movie_data"] = {
                            "name": names[idx],
                            "poster": posters[idx],
                            "rating": ratings[idx],
                            "overview": overviews[idx],
                            "trailer": trailers[idx],
                            "score": scores[idx]
                        }
                        st.switch_page("pages/details.py")
import streamlit as st
import pandas as pd
import pickle
import requests
from io import BytesIO
import gdown

# ✅ Streamlit setup
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")
st.sidebar.header("🔍 Find by Genre or Keyword")

# ✅ Load precomputed data from Google Drive


@st.cache_data
def load_data():
    try:
        movies_id = "1n8SYQQEYy79lhc6z8CzPnTr8oqK0xBVT"
        sim_id = "1vh-gEkPtw6RUSjzQaJ25UXTQvObSUuiX"

        # ✅ gdown gives you raw binary data, not HTML
        movies_bytes = gdown.download(f"https://drive.google.com/uc?id={movies_id}", None, quiet=False)
        sim_bytes = gdown.download(f"https://drive.google.com/uc?id={sim_id}", None, quiet=False)

        with open(movies_bytes, 'rb') as f:
            movies = pickle.load(f)
        with open(sim_bytes, 'rb') as f:
            similarity = pickle.load(f)

        if not isinstance(movies, pd.DataFrame):
            movies = pd.DataFrame(movies)

        return movies, similarity

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame(), None



movies, similarity = load_data()

if movies.empty or similarity is None:
    st.stop()

# ✅ Sidebar search
search_term = st.sidebar.text_input("Enter a genre or keyword (e.g. romance, action, space)")

if st.sidebar.button("Search"):
    matches = movies[movies['tags'].str.contains(search_term.lower(), case=False)]
    if not matches.empty:
        st.sidebar.success(f"Found {len(matches)} movies related to '{search_term}'")
        for name in matches['title'].head(10):
            st.sidebar.write("🎥", name)
    else:
        st.sidebar.warning("No matches found.")

st.write("### 💡 Find movies similar to the one you love ❤️")

selected_movie = st.selectbox(
    "Select or search for a movie:",
    movies['title'].values
)


# ✅ Poster Fetcher
def fetch_poster(movie_title):
    api_key = "45d06a18fccc22039d620039e653e60c"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    data = requests.get(url).json()

    if not data.get('results'):
        return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

    poster_path = data['results'][0].get('poster_path')
    if not poster_path:
        return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

    return f"https://image.tmdb.org/t/p/w500/{poster_path}"


# ✅ Recommendation logic
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(
            list(enumerate(distances)), reverse=True, key=lambda x: x[1]
        )[1:11]

        recommended_movies = []
        recommended_posters = []
        for i in movie_list:
            title = movies.iloc[i[0]].title
            recommended_movies.append(title)
            recommended_posters.append(fetch_poster(title))

        return recommended_movies, recommended_posters
    except Exception as e:
        st.error(f"⚠️ Recommendation failed: {e}")
        return [], []


# ✅ Recommend button
if st.button('Recommend'):
    with st.spinner('Finding similar movies...'):
        names, posters = recommend(selected_movie)

        if names:
            st.success("Here are your recommendations:")
            cols = st.columns(5)
            for idx, col in enumerate(cols * 2):  # 10 posters total
                if idx < len(names):
                    with col:
                        st.image(posters[idx], use_container_width=True)
                        st.caption(names[idx])
        else:
            st.warning("No recommendations found. Try another movie.")

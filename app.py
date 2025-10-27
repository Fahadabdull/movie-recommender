import streamlit as st
import pickle
import pandas as pd
import requests
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return pd.DataFrame(movies_dict), similarity

movies, similarity = load_data()



# load precomputed data
import pickle
import requests
from io import BytesIO

@st.cache_resource
def load_data():
    # Replace with your actual file IDs
    movies_url = "https://drive.google.com/file/d/1n8SYQQEYy79lhc6z8CzPnTr8oqK0xBVT/"
    similarity_url = "https://drive.google.com/file/d/1vh-gEkPtw6RUSjzQaJ25UXTQvObSUuiX/"

    movies_response = requests.get(movies_url)
    similarity_response = requests.get(similarity_url)

    movies = pickle.load(BytesIO(movies_response.content))
    similarity = pickle.load(BytesIO(similarity_response.content))
    return movies, similarity

st.set_page_config(page_title="🎬 Movie Recommender", layout="centered")

st.title("🎬 Movie Recommender System")
st.sidebar.header("🔍 Find by Genre or Keyword")
search_term = st.sidebar.text_input("Enter a genre or keyword (e.g. romance, action, space)")

if st.sidebar.button("Search"):
    matches = movies[movies['tags'].str.contains(search_term.lower(), case=False)]
    if not matches.empty:
        st.sidebar.success(f"Found {len(matches)} movies related to '{search_term}'")
        for name in matches['title'].head(10):
            st.sidebar.write("🎥", name)
    else:
        st.sidebar.warning("No matches found.")

st.write("Find movies similar to the one you love ❤️")

selected_movie = st.selectbox(
    "Select or search for a movie:",
    movies['title'].values
)
def fetch_poster(movie_title):
    import requests

    url = f"https://api.themoviedb.org/3/search/movie?api_key=45d06a18fccc22039d620039e653e60c&query={movie_title}"
    data = requests.get(url).json()

    # Check if results exist
    if not data.get('results'):
        return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

    poster_path = data['results'][0].get('poster_path')

    # If no poster path found, return a simple clean fallback
    if poster_path is None:
        return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

    return "https://image.tmdb.org/t/p/w500/" + poster_path


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
    
    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))
    return recommended_movies, recommended_posters

if st.button('Recommend'):
    with st.spinner('Finding similar movies...'):
        names, posters = recommend(selected_movie)
        st.success("Here are your recommendations:")
        cols = st.columns(10)
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx], use_container_width=True)
                st.caption(names[idx])


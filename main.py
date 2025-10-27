import pandas as pd
import ast

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("movies.csv")
credits = pd.read_csv("movies_credit.csv")

movies = movies.merge(credits, on='title')
# print(movies.shape)
# print(movies.columns)

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
def fetch_cast(obj):
    L = []
    for i in ast.literal_eval(obj)[:3]:  # take top 3 actors
        L.append(i['name'])
    return L

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            return [i['name']]
    return []

movies['cast'] = movies['cast'].apply(fetch_cast)
movies['crew'] = movies['crew'].apply(fetch_director)

# Convert overview (text) to list of words
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Merge everything into one 'tags' column
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create new dataframe with only 'movie_id', 'title', 'tags'
new_df = movies[['movie_id', 'title', 'tags']].copy()

new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
vectors = tfidf.fit_transform(new_df['tags']).toarray()

similarity = cosine_similarity(vectors)


tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
vectors = tfidf.fit_transform(new_df['tags']).toarray()
def recommend(movie):
    if movie not in new_df['title'].values:
        print("❌ Movie not found in database. Try another title (check spelling and case).")
        return
    
    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:20]
    
    print(f"\n🎬 Because you liked '{movie}', you might also enjoy:")
    for i in movie_list:
        print("👉", new_df.iloc[i[0]].title)

import pickle

pickle.dump(new_df.to_dict(), open('movies.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))



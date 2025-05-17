from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__)

# Load data
df = pickle.load(open('df (1).pkl', 'rb'))
similarity = pickle.load(open('similarity (2).pkl', 'rb'))

# TMDB API key
API_KEY = '8265bd1679663a7ea12ac168da84d2e8'


def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    data = requests.get(url).json()
    return 'https://image.tmdb.org/t/p/w500/' + data['poster_path']


def fetch_rating_and_genres(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    data = requests.get(url).json()
    rating = data.get('vote_average', 'N/A')
    genres = ', '.join([genre['name'] for genre in data.get('genres', [])])
    return rating, genres


def recommend(movie):
    index = df[df['title'] == movie].index[0]
    distances = similarity[index]
    movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_ratings = []
    recommended_genres = []
    recommended_ids = []

    for i in movies:
        movie_id = df.iloc[i[0]].id
        recommended_ids.append(movie_id)
        recommended_movies.append(df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        rating, genres = fetch_rating_and_genres(movie_id)

        # Limit to 3 genres and add "+X more" if needed
        genre_list = genres.split(', ')
        if len(genre_list) > 3:
            display_genres = ', '.join(genre_list[:3]) + f', +{len(genre_list) - 3} more'
        else:
            display_genres = ', '.join(genre_list)

        recommended_ratings.append(rating)
        recommended_genres.append(display_genres)

    # Zip all recommendation data for HTML template
    zipped = zip(recommended_movies, recommended_posters, recommended_ratings, recommended_genres, recommended_ids)
    return zipped


@app.route('/', methods=['GET', 'POST'])
def home():
    selected_movie = None
    zipped_data = None

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        if selected_movie in df['title'].values:
            zipped_data = recommend(selected_movie)

    movie_list = df['title'].values.tolist()
    return render_template('index.html', movie_list=movie_list, selected_movie=selected_movie, zipped_data=zipped_data)


if __name__ == '__main__':
    app.run(debug=True)

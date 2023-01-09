from pymongo import MongoClient
from os import getenv
import imdb
import gridfs
import requests


# initial tmdb class to handle api requests to tmdb, to receive poster image
class TMAPI():

    def __init__(self):
        self.key = getenv("key")
        self.url = f'http://api.themoviedb.org/3/configuration?api_key={self.key}'
        self.img_url = 'http://api.themoviedb.org/3/movie/{imdbid}/images?api_key={KEY}'
        self.r = requests.get(self.url)
        self.conf = self.r.json()
        self.base_url = self.conf['images']['base_url']
        self.sizes = self.conf['images']['poster_sizes'][-1]

    # tmdb_id() receives a movie name, and return the imdb id for a given movie
    def tmdb_id(self, movie_name):
        ia = imdb.Cinemagoer()
        search = ia.search_movie_advanced(movie_name)
        for movie in range(len(search)):
            if str(search[movie].data['kind']) == "movie":
                self.movie_id = f'tt{str(search[movie].movieID)}'
                return self.movie_id
        self.movie_id = ''
        return self.movie_id

    # __image_url() recives movie_name, to be passed on to tmdb_id() function.
    # and return the url with the formatted tmdbapi key and imdb id for searched movie
    def __image_url(self, movie_name):
        image_url = self.img_url.format(KEY=self.key, imdbid=self.tmdb_id(movie_name))
        r = requests.get(image_url)
        image_name = r.json()['posters'][0]['file_path']
        self.url = "{0}{1}{2}".format(self.base_url, self.sizes, image_name)
        return self.url

    # write_image_to_mongo() receives movie name and mongo, mongo refers to the mongo db client from the child class.
    # it calls the image url function to receive the poster image url, and via the requests module return
    # the poster binary data, and calls the insert_img function from the child mongo class
    def write_image_to_mongo(self, mongo, movie_name):
        self.url = self.__image_url(movie_name)
        r = requests.get(self.url)
        content = r.content
        Mongo.insert_img(mongo, content, filename=self.movie_id)

# mongo class is the class that will manipulate the mongo db data and connection
class Mongo(TMAPI):
    def __init__(self, host, port):
        TMAPI.__init__(self)
        self.mdb = MongoClient(host, port)
        self.database = self.mdb['posters']
        self.coll = self.database['fs.files']
        self.fs = gridfs.GridFS(self.database)


    # insert_img() receives the data to be inserted onto the database and the filename.
    # via gridfs module we write the data to mongo db
    # file names and attr are found in fs.file collection, data is stored in fs.chunks collection
    def insert_img(self, data, filename):
        mongo_id = self.fs.put(data, filename=filename)

    # read_data simply, reads data from the database via gridfs object and returns the binary image data
    def read_data(self):
        ans = self.fs.find_one({'filename': self.movie_id})
        image = ans.read()
        return image

    def update(self):
        pass

    def delete(self):
        pass
    # image_cached is the most important function, as it is responsible for cascading
    # and triggering all necessary functions to retrieve the movie poster.
    # it receives the movie name to check if a poster's filename matches the imdb_id equivalent for the searched movie
    # if it has a match, it calls the read_data function, if not it calls the write_image_to_mongo func
    # and then reads it from the database so no local caching is happening
    def image_cached(self, movie_name):
        present = self.fs.find_one({'filename': self.tmdb_id(movie_name)})
        if present is None:
            self.write_image_to_mongo(self, movie_name)
        return self.read_data()

# initializing the mongo class to the mdb object with the hostname for the mongo db server and the port.
mdb = Mongo('mongo', 27017)

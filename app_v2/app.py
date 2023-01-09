from flask import *
from mongo_helper import *
from base64 import b64encode

# initialising flask obj
app = Flask(__name__)


# base route when connecting to the web app's ip
@app.route('/')
def index():
    return render_template('homepage.html')


# search function to handle post and get requests to the web app. when it receives a post request,
# it takes the movie name, and tries to call the image_cached function to receive the binary movie poster data
# b46 encodes it and decodes it to utf-8 and then returns an html block with the data and the movie name
# if any of the steps fails, it returns a fail.html file that promts the user that the search has failed
# and gives him the ability to search again.
# get requests are returned the search.html file
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        user_inp = request.form['name']

        try:
            Mo_file = mdb.image_cached(user_inp)
            image = b64encode(Mo_file).decode('utf-8')
            url = 'data:image/gif;base64,' + image
            return f'<img src={url} alt={user_inp} width="400" height="500">'
        except Exception as e:
            return render_template('fail.html')
    return render_template('search.html')


if __name__ == "__main__":
    app.run(port=80, host="0.0.0.0")
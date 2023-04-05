from flask import Flask, render_template, request, url_for, redirect
from flask_socketio import SocketIO
from flask_caching import Cache
from model import retrieve_uris, checkifany, do_everything

app = Flask(__name__)
socketio = SocketIO(app)
cache = Cache()

@app.route('/', methods=["POST", "GET"])
def index():
   if request.method == "POST": # if form was submitted
      link = request.form["playlisturl"] # gets the input of the form in home.html
      return redirect(f"/results?playlist={link}") # redirecting to /results basically
      # return redirect(url_for("recommend", songs=songs))
   else: # GET request, just reloaded 
      return render_template('home.html')

@app.route('/about')
def about():
   return render_template('about.html')

@app.route('/results')
def recommend():
   link = request.args.get("playlist")
   if link is None: # did form submit properly?
      return f"Nothing got submitted"

   songuris = retrieve_uris(link)
   match checkifany(songuris):
      case 1:
         return f"<h1> You didn't type a valid playlist link. Go back and do it right </h1>"
      case 2:
         return f"<h1> Looks like none of your songs matched with the ones in the database. Sorry about that! Try again with a different playlist. </h1>"
      case 3:
         # return f"<h1> GANG </h1>"
         pass

   final = do_everything(songuris, 10)

   return render_template('results.html', songs=final)

if __name__ == '__main__':
   # app.run(debug=True)
   socketio.run(app)
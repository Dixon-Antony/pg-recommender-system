from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/listings")
def listings():

    pgdata = [{'name':'hello','img_src':'bg4','price':'5000','rating':'3'},
              {'name':'world','img_src':'bg2','price':'4500','rating':'4'},
              {'name':'Jg','img_src':'bg3','price':'5500','rating':'5'},
              {'name':'Dinesh','img_src':'bg4','price':'6000','rating':'2'}]
    

    return render_template('listings.html',pgdata=pgdata, len = len(pgdata))

@app.route("/viewListing")
def viewListing():
    return render_template('viewListing.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/favorites")
def favorites():
    return render_template('favorites.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/login")
def login():
    return render_template('login.html')


if __name__ == "__main__":
  app.run()
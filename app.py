from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/listings")
def listings():
    return render_template('listings.html')

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
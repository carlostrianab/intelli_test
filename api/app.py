from flask import Flask

#Creates the flask application
app = Flask(__name__)

#First route 
@app.route('/')
def index():
    return 'index page'

#Initiates the app 
if __name__ == "__main__":
    app.run(debug=True)
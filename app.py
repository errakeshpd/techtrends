import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from flask.logging import default_handler

count = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global count
    count+=1
    return connection

def close_connection(connection):
    # global count
    # count-=1
    connection.close()

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    close_connection(connection)
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    close_connection(connection)
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('A non existing article is accessed and a 404 page is returned')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "%s" retrieved!', post['title'])
      return render_template('post.html', post=post)
    
# Define the healthz
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

# Define the metrics
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    close_connection(connection)
    #  count the total connection to the database, dont hardcode the value

    response = app.response_class(
        response=json.dumps({"db_connection_count": count, "post_count": len(posts)}),
        status=200,
        mimetype='application/json'
    )
    return response

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page is retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.debug('title not provided for article creation')
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            close_connection(connection)
            app.logger.info('A new article is created with title "%s"', title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.logger.addHandler(default_handler)
   app.logger.setLevel('INFO')
   app.logger.info('Starting the app')
   app.run(host='0.0.0.0', port='3111')

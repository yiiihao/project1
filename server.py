#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "yg2820"
DB_PASSWORD = "4798"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

#DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a interested_event table for users to add event id they are interested in
engine.execute("""DROP TABLE IF EXISTS interested_event;""")
engine.execute("""CREATE TABLE IF NOT EXISTS interested_event (
  id serial);""")
engine.execute("""INSERT INTO interested_event(id) VALUES (1), (5);""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  q1 = text("SELECT *"
     "FROM Events")

  cursor_q1 = g.conn.execute(q1)
  events = []
  for result in cursor_q1:
    events.append(result)  # can also be accessed using result[0]
  cursor_q1.close()
  
  
  q2 = text("SELECT * FROM interested_event")
  cursor_q2 = g.conn.execute(q2)
  interested_event_id = []
  for result in cursor_q2:
    interested_event_id.append(result)
  cursor_q2.close()
           
        
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(event_data = events, 
                 all_tables = engine.table_names(),
                 id_data = interested_event_id)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/medal_ranking')
def medal_ranking():
  return render_template("medal_ranking.html")

@app.route('/athlete_information')
def athlete_information():
  return render_template("athlete_information.html")

@app.route('/event_schedule')
def event_schedule():
  return render_template("event_schedule.html")


# add new data to the interest_event table 添加喜欢的比赛
@app.route('/add', methods=['POST'])
def add():
  new_id = request.form['id']
  print(new_id)
  cmd = 'INSERT INTO interested_event(id) VALUES (:id)';
  g.conn.execute(text(cmd), id = new_id);
  return redirect('/')

# delete input data to the interested_event table 删除喜欢的比赛
@app.route('/delete', methods=['POST'])
def delete():
  new_id = request.form['id']
  print(new_id)
  cmd = 'DELETE FROM interested_event WHERE id=(:id)';
  g.conn.execute(text(cmd), id = new_id);
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

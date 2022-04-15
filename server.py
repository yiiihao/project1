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


# 感兴趣的比赛id表
#Here we create a interested_event table for users to add event id they are interested in
engine.execute("""DROP TABLE IF EXISTS interested_event;""")
engine.execute("""CREATE TABLE IF NOT EXISTS interested_event (
  id int,
  primary key (id),
  foreign key (id) references Events(event_id));""")
#engine.execute("""INSERT INTO interested_event(id) VALUES (1), (5);""")



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



#首页html
@app.route('/')
def index():

  # DEBUG: this is debugging code to see what request looks like
  # print(request.args)
          
  return render_template("index.html")

#创建分页面1 奖牌
@app.route('/medal_ranking')
def medal_ranking():
#   # DEBUG: this is debugging code to see what request looks like
#   print(request.args) 
  
    return render_template("medal_ranking.html")

# # 互动功能

# 返回全部奖牌榜 return medal ranking for all
@app.route('/view', methods=['POST'])
def view():
  #cmd = "SELECT * FROM Medals_of_event_of_athlete"

  cmd = text("select noc, max(case when medal_type = 'gold' then num_medal else 0 end) as gold, max(case when medal_type = 'silver' then num_medal else 0 end) as silver, max(case when medal_type = 'bronze' then num_medal else 0 end) as bronze "
             "from (SELECT noc, medal_type, count(medal_type) AS num_medal FROM Medals_of_event_of_athlete a LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id "
             "GROUP BY noc, medal_type) temp group by noc ORDER BY gold DESC, silver DESC")
    
  cursor = g.conn.execute(cmd)
  data = []
  for result in cursor:
    #print(result)
    data.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(view_data = data)
    
  return render_template("medal_ranking.html", **context)

# # 选择想要的奖牌信息 select information for medals
@app.route("/medal_ranking" , methods=['GET', 'POST'])
def test():
    v1 = request.form.get('category')
    v2 = request.form.get('type')
    v3 = request.form.get('country')
    
    category = v1
    medal_type = v2
    country = v3
    
    q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name "
            "FROM Medals_of_event_of_athlete a "
            "LEFT JOIN Athletes b "
            "ON a.athlete_id = b.athlete_id "
            "LEFT JOIN Events c "
            "ON a.event_id = c.event_id "
            "WHERE NOC = :d3 AND discipline = :d1 AND medal_type = :d2")
    
    if v1 == "ALL" and v2 == "ALL" and v3 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id")
    elif v1 == "ALL" and v2 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id "
                  "WHERE NOC = :d3")
    elif v1 == "ALL" and v3 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id "
                  "WHERE medal_type = :d2")
    elif v2 == "ALL" and v3 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id "
                  "WHERE discipline = :d1")
    elif v1 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id "
                  "WHERE medal_type = :d2 and NOC = :d3")
    elif v2 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id "
                  "WHERE discipline = :d1 and NOC = :d3")
    elif v3 == "ALL":
        q0 = text("SELECT medal_type, concat(first_name, ' ', last_name), noc, discipline,category,event_name FROM Medals_of_event_of_athlete a "
                  "LEFT JOIN Athletes b ON a.athlete_id = b.athlete_id LEFT JOIN Events c ON a.event_id = c.event_id "
                  "WHERE discipline = :d1 and medal_type = :d2")
    
    cursor_q0 = g.conn.execute(q0,d1=category,d2=medal_type,d3=country)
    medal_info = []
    for result in cursor_q0:
      medal_info.append(result)  # can also be accessed using result[0]
    cursor_q0.close()
    
    context = dict(medal_data = medal_info, raw_data = [v1,v2,v3])

    return render_template("medal_ranking.html", **context)




#创建分页面2 运动员
@app.route('/athlete_information')
def athlete_information():
    
  # query all athlete names 选出所有的运动员名字
  q1 = text("SELECT concat(first_name, ' ', last_name) "
     "FROM Athletes")

  cursor_q1 = g.conn.execute(q1)
  athlete = []
  for result in cursor_q1:
    athlete.append(result)  # can also be accessed using result[0]
  cursor_q1.close()

  context = dict(athlete_name = athlete)

  return render_template("athlete_information.html", **context)


# 查找喜欢的运动员 find information about athletes interested
@app.route('/find', methods=['POST'])
def find():
    
  name = request.form['name']
  first_name, last_name = name.split()
  print(first_name, last_name)

  cmd2 = text("SELECT b.first_name, b.last_name, nickname, b.gender, b.noc, birthday, age, c.first_name, c.last_name "
              "FROM Athletes b LEFT JOIN Instruct a ON a.athlete_id = b.athlete_id LEFT JOIN Coaches c ON a.coach_id = c.coach_id "
              "WHERE b.first_name = :v1 AND b.last_name = :v2")
  cursor_q2 = g.conn.execute(cmd2, v1 = first_name, v2=last_name)
  data2 = []
  for result in cursor_q2:
    #print(result)
    data2.append(result)  # can also be accessed using result[0]
  cursor_q2.close()

  cmd1 = text("SELECT concat(first_name, ' ', last_name) Athlete, NOC Country, discipline,category, event_name Event_Name, location, day Event_Day, start_time " 
              "FROM Events a " 
              "LEFT JOIN Participate b "
              "ON a.event_id = b.event_id " 
              "LEFT JOIN Athletes c " 
              "ON b.athlete_id = c.athlete_id " 
              "WHERE first_name = :v1 AND last_name = :v2")

  cursor_q1 = g.conn.execute(cmd1, v1 = first_name,v2=last_name)
  data1 = []
  for result in cursor_q1:
    #print(result)
    data1.append(result)  # can also be accessed using result[0]
  cursor_q1.close()

  # query all athlete names 选出所有的运动员名字
  q = text("SELECT concat(first_name, ' ', last_name)"
     "FROM Athletes")

  cursor_q = g.conn.execute(q)
  athlete = []
  for result in cursor_q:
    athlete.append(result)  # can also be accessed using result[0]
  cursor_q.close()
  
  context = dict(athlete_name = athlete, athlete_data = data1, event_data = data2)
  
  return render_template("athlete_information.html", **context)
  #return redirect('/event_schedule')

  




#创建分页面3 比赛信息
@app.route('/event_schedule')
def event_schedule():
    
  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  # query all events
  q1 = text("SELECT *"
     "FROM Events")

  cursor_q1 = g.conn.execute(q1)
  events = []
  for result in cursor_q1:
    events.append(result)  # can also be accessed using result[0]
  cursor_q1.close()
  
  # query all interested events
  q2 = text("SELECT * FROM interested_event")
  cursor_q2 = g.conn.execute(q2)
  interested_event_id = []
  for result in cursor_q2:
    interested_event_id.append(result[0])
  cursor_q2.close()
           
  context = dict(event_data = events, 
                 id_data = interested_event_id)

  return render_template("event_schedule.html", **context)

#创建分页面4 错误
@app.route('/error')
def error():
  return render_template("event_schedule.html", **context)
    
# 互动功能
# 添加喜欢的比赛 add new data to the interest_event table
@app.route('/add', methods=['POST'])
def add():
  error = None
  new_id = request.form['id']
  print(new_id)

#   query = 'SELECT * FROM interested_event'
#   cursor = g.conn.execute(text(query))
#   exists_id = []
#   for result in cursor:
#     exists_id.append(result[0])
#   cursor.close()
  
#   #print(exists_id)

#   if new_id in exists_id:
#     error = "Event id already exists"
#   else:
#     cmd = 'INSERT INTO interested_event(id) VALUES (:id)';
#     g.conn.execute(text(cmd), id = new_id);
#     return redirect('/event_schedule')

  try:
      cmd = 'INSERT INTO interested_event(id) VALUES (:id)';
      g.conn.execute(text(cmd), id = new_id);
  except:
      error_statement = "Error: id already exists or out of range!"
      return render_template("error.html", error_statement = error_statement)
  return redirect('/event_schedule')

# 删除喜欢的比赛 delete input data to the interested_event table
@app.route('/delete', methods=['POST'])
def delete():
  new_id = request.form['id']
  print(new_id)
        
  try:
      cmd = 'DELETE FROM interested_event WHERE id=(:id)';
      g.conn.execute(text(cmd), id = new_id);
  except:
      error_statement = "Error: id does not exist in the table!"
      return render_template("error.html", error_statement = error_statement)
  return redirect('/event_schedule')


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

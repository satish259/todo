#!flask/bin/python
# This follows the steps in and uses code from https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

from flask import Flask, jsonify, request, url_for, make_response
from flask_httpauth import HTTPBasicAuth

global user
app = Flask(__name__)
auth = HTTPBasicAuth()

tasks = [
    {
        'id': 1,
        'title': 'Buy groceries',
        'description': 'Milk, Bread', 
        'complete': False
    },
    {
        'id': 2,
        'title': 'Learn Python',
        'description': 'Need to find a good Python tutorial on the web', 
        'complete': False
    }
]

users = {
    "user1": "password1"
}

@auth.verify_password
def verify_password(username, password):
    if username not in users or password != users[username]:
        return False
    return True

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

#@app.route('/todo/api/v1.0/logout')
#def logout():
#   user=None 
#   return user 

#Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/todo/api/v1.0/task/1
@app.route('/todo/api/v1.0/task/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    app.logger.info('START - get_task')
    rOut="Task not found"
    rStatus=404
    app.logger.info("task_id=" +  str(task_id))
    task = [task for task in tasks if task['id'] == task_id]
    app.logger.info("task=" +  str(task))
    try:
        if len(task) != 0:
            rOut=jsonify({'task': make_public_task(task[0])})
            rStatus=302
    except Exception as e:
        app.logger.exception(e)
    app.logger.info('END - get_task')
    return rOut, rStatus

#Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/todo/api/v1.0/tasks
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    app.logger.info('START - get_tasks')
    rOut="No tasks found"
    rStatus=404
    try:
        rOut=jsonify({'tasks': [make_public_task(task) for task in tasks]})
        rStatus=200
    except Exception as e:
        app.logger.exception(e)
    app.logger.info('END - get_tasks')
    return rOut, rStatus 

#Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/todo/api/v1.0/task/add -ContentType "application/json" -Method POST -Body '{ "title":"Visit Library","description":"Get Python book" }'
@app.route('/todo/api/v1.0/task/add', methods=['POST'])
@auth.login_required
def create_task():
    app.logger.info('START - create_task')
    rOut="Unable to add task"
    rStatus=400
    validated = validateTask(request.json)
    if not validated:
        app.logger.info(str(validated))
    else:
        try:
            task = {
                'id': tasks[-1]['id'] + 1,
                'title': str(request.json['title']),
                'description': str(request.json.get('description', "")),
                'complete': bool(request.json.get('complete', False)),
            }
            tasks.append(task)
            rOut= jsonify({'Added successfully': make_public_task(task)})
            rStatus=201
        except Exception as e:
            app.logger.exception(e)
    app.logger.info('END - create_task')
    return rOut, rStatus


@app.route('/todo/api/v1.0/task/update/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    app.logger.info('START - update_task')
    rOut="Unable to update task"
    rStatus=400
    app.logger.info("task_id=" +  str(task_id))
    task = [task for task in tasks if task['id'] == task_id]
    app.logger.info("task=" +  str(task))
    validated = validateTask(request.json)
    if not validated:
        app.logger.info(str(validated))
    else:
        try:
            task[0]['title'] = request.json.get('title', task[0]['title'])
            task[0]['description'] = request.json.get('description', task[0]['description'])
            task[0]['complete'] = request.json.get('complete', task[0]['complete'])
            rOut= jsonify({'Updated successfully': make_public_task(task[0])})
            rStatus=205
        except Exception as e:
            app.logger.exception(e)
    app.logger.info('END - update_task')
    return rOut, rStatus

#Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/todo/api/v1.0/task/delete/1
@app.route('/todo/api/v1.0/task/delete/<int:task_id>', methods=['GET'])
@auth.login_required
def delete_task(task_id):
    app.logger.info('START - delete_task')
    rOut="Unable to delete task"
    rStatus=400
    app.logger.info("task_id=" +  str(task_id))
    task = [task for task in tasks if task['id'] == task_id]
    app.logger.info("task=" +  str(task))
    try:
        if len(task) != 0:
            tasks.remove(task[0])
            rOut = jsonify({'Deleted successfully': make_public_task(task)})
            rStatus=303
        else:
            rOut="Task not found"
            rStatus=404
    except Exception as e:
        app.logger.exception(e)
    app.logger.info('START - delete_task')
    return rOut, rStatus

#Function to validate task items
def validateTask(jsonTask):
    rOut=[]
    if ('title' in jsonTask and isinstance(jsonTask['title'], str)) or 'title' in jsonTask: rOut.append(str(jsonTask['title']) + ' is not string')
    if 'description' in jsonTask and isinstance(jsonTask['description'], str): rOut.append(str(jsonTask['description']) + ' is not string')
    if 'complete' in jsonTask and isinstance(jsonTask['complete'], bool): rOut.append(str(jsonTask['description']) + ' is not bool')
    rOut=True
    return rOut 

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

if __name__ == '__main__':
    app.run(debug=True)



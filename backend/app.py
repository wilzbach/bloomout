#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import environ
import datetime
import pymongo
from bson.json_util import dumps
from mongo_base import employees, messages, projects
from graph import build_graph
from flask import abort, Flask, jsonify, request
from watson import nltk, tone, personality

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/api/history', methods=['GET'])
def history():
    return dumps(messages.find().sort('date', pymongo.DESCENDING))


@app.route('/api/chat', methods=['POST'])
def chat():
    req = request.get_json()
    if "body" not in req:
        abort(400, "No text provided.")
    resp = nltk(req["body"])
    messages.insert_one({
        "emotion": resp,
        "from": req["from"],
        "to": req["to"],
        "body": req["body"],
        'created_at': datetime.datetime.now()
    })
    return jsonify(resp)


@app.route('/api/graph', methods=['GET'])
def graph():
    return jsonify(build_graph())


@app.route('/api/employee/<emp_id>', methods=['GET'])
def get_employee(emp_id):
    employee = employees.find_one({'id': int(emp_id)})
    if employee:
        return dumps(employee)
    else:
        abort(400, 'Employee not found')


@app.route('/api/employees', methods=['GET', 'POST'])
def get_or_create_employees():
    if request.method == 'POST':
        return ('', 204)
    else:
        all_employees = []
        for employee in employees.find():
            all_employees.append(employee)

        return dumps(all_employees)


@app.route('/api/project/<proj_id>', methods=['GET'])
def get_project(proj_id):
    project = projects.find_one({'id': int(proj_id)})
    if project:
        return dumps(project)
    else:
        abort(400, 'Project not found')


@app.route('/api/projects', methods=['GET'])
def get_or_create_projects():
    if request.method == 'POST':
        return ('', 204)
    else:
        all_projects = []
        for project in projects.find():
            all_projects.append(project)

        return dumps(all_projects)


if __name__ == '__main__':
    port = environ.get("PORT", "6001")
    app.run(debug=True, port=int(port), use_reloader=True)

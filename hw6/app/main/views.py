from flask import Flask, jsonify, request, redirect, url_for

import json
import threading

from . import main

from ..task import run

@main.route('/', methods=['GET', 'POST'])
def index():
	return '<h1>OS-Prac lab6 Homepage</h1>'

@main.route('/job/task', methods=['GET', 'POST'])
def submit():
	json_data = request.get_json()
	
	task_id = json_data['name']
	
	threading.Thread(target=run.run_task, args=[json_data]).start()

	# threading.Timer(int(json_data["timeout"]), run.kill_task, args=[task_id]).start()

	ret = {"code": 0, "data": {}, "message": ""}
	ret["data"]["task_id"] = task_id
	
	return jsonify(ret)

@main.route('/job/kill', methods=['GET', 'POST'])
def kill():
	task_id = request.args['task_id']
	return jsonify(run.kill_task(task_id))

@main.route('/job/status', methods=['GET', 'POST'])
def status():
	task_id = request.args['task_id']
	return jsonify(run.task_status.get(task_id))


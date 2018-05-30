from flask import Flask, jsonify, request, redirect, url_for
from xmlrpc.client import ServerProxy

from . import main

slave1 = ServerProxy('http://localhost:8000')
slave2 = ServerProxy('http://162.105.175.75:8000')

# slave_pool = [slave1]

# test for multi slaves
slave_pool = [slave1, slave2]

def get_slave():
	import random
	return slave_pool[random.randint(0, len(slave_pool) - 1)]

@main.route('/', methods=['GET', 'POST'])
def index():
	result = {}
	for slave in slave_pool:
		tasks = slave.get_all_tasks()
		for task in tasks:
			result[task] = slave.get_task_status({'name': task})
	return jsonify(result)

@main.route('/job/task', methods=['GET', 'POST'])
def submit():
	json_data = request.get_json()
	return jsonify(get_slave().run_task(json_data))

@main.route('/job/kill', methods=['GET', 'POST'])
def kill():
	json_data = request.get_json()
	for slave in slave_pool:
		if slave.check_task_exist(json_data):
			return jsonify(slave.kill_task(json_data))
	return jsonify({"code":1, "message": "Not found"})

@main.route('/job/status', methods=['GET', 'POST'])
def status():
	json_data = request.get_json()
	for slave in slave_pool:
		if slave.check_task_exist(json_data):
			return jsonify(slave.get_task_status(json_data))
	return jsonify({"code":1, "message": "Not found"})

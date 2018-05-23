from flask import Flask, jsonify, request, redirect, url_for
from xmlrpc.client import ServerProxy

from . import main

slave = ServerProxy('http://localhost:8000')

@main.route('/', methods=['GET', 'POST'])
def index():
	return '<h1>OS-Prac lab6 Homepage</h1>'

@main.route('/job/task', methods=['GET', 'POST'])
def submit():
	json_data = request.get_json()
	return jsonify(slave.run_task(json_data))

@main.route('/job/kill', methods=['GET', 'POST'])
def kill():
	json_data = request.get_json()
	return jsonify(slave.kill_task(json_data))

@main.route('/job/status', methods=['GET', 'POST'])
def status():
	json_data = request.get_json()
	return jsonify(slave.get_task_status(json_data))

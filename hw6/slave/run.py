#!/usr/bin/python3
import lxc
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


task_status = {}
task_cluster = {}

def get_all_tasks():
    return list(task_status.keys())

def get_task_status(data):
    task_id = data['name']
    return {"cluster":task_cluster[task_id], "status": task_status[task_id]}

def kill_task(data):
    task_id = data['name']
    c = lxc.Container(task_id)
    if c.state == "STOPPED":
        return {"code":0, "data":"" , "message":""} # empty value
    
    # Try to stop
    c.stop()

    # Check if stop successfully
    if not c.stop():
        return {"code":1, "data": "fail", "message":""}
    else:
        task_status[task_id] = "Failed"
        return {"code":0, "data": "success", "message":""}

def run_task_in_container(data):
    global task_status
    global task_cluster

    slave_id = "slave1"

    task_id = data['name']
    commandLine = data['commandLine']
    
    code_succ = {"code":0, "task_id": task_id, "message":"successful!"}
    code_fail = {"code":1, "task_id": task_id, "message":"failed!"}
    
    out_file = open(data.get('outputPath', 'data/output.txt'), 'w+')
    log_file = open(data.get('logPath', 'data/log.txt'), 'w+')
    
    def close_and_mark(status_str):
        task_status[task_id] = status_str
        out_file.close()
        log_file.close()

    c = lxc.Container(task_id)

    if not c.defined:
        # Create the container rootfs
        lxc_choice = {"dist": "debian","release": "sid","arch": "amd64"}
        if not c.create("download", lxc.LXC_CREATE_QUIET, lxc_choice):
            print("Failed to create the container rootfs", file=log_file)
            close_and_mark("Failed")
            return code_fail

    image = data.get('image', None)
    if image is not None:
        rootfs_path = '/var/lib/lxc/%s/config' % image
        c.set_config_item('lxc.rootfs', rootfs_path)
    
    resource = data.get('resource', None)
    if resource is not None:
        if 'cpu' in resource:
            c.set_config_item('lxc.cgroup.cpuset.cpus', resource.get('cpu'))
        if 'memeory' in resource:
            c.set_config_item('lxc.cgroup.memory.limit_in_bytes', resource.get('memeory'))

    # Start the container
    if not c.start():
        print("Failed to start the container", file=log_file)
        close_and_mark("Failed")
        return code_fail
    
    task_cluster[task_id] = slave_id
    task_status[task_id] = "Running"

    """
    # Query some information
    print("Container state: %s" % c.state)
    print("Container PID: %s" % c.init_pid)
    sys.stdout.flush()
    """

    # Wait for connectivity
    if not c.get_ips(timeout=30):
        print("Failed to connect the container", file=log_file)
        close_and_mark("Failed")
        return code_fail
    
    # Execute the task
    retry_time = int(data.get('maxRetryCount', 0))
    success_flag = False
    for retry in range(retry_time + 1):
        exit_code = c.attach_wait(lxc.attach_run_command, ["bash", "-c", commandLine], stdout=out_file, stderr=log_file)
        if exit_code == 0:
            success_flag = True
            break
    
    # Check if it's succeeded
    if not success_flag:
        print("Fail for %d times!" % retry_time, file=log_file)
        close_and_mark("Failed")
    
    # Shutdown the container
    if not c.shutdown(30):
        c.stop()
        if not c.stop():
            print("Failed to kill the container", file=log_file)
            close_and_mark("Failed")
    
    if success_flag:
        close_and_mark("Succeeded")
        return code_succ
    else:
        return code_fail

def run_task(data):
    task_id = data['name']
    threading.Thread(target=run_task_in_container, args=[data]).start()
    threading.Timer(int(data.get("timeout", 60)), kill_task, args=[{'name': task_id}]).start()
    ret = {"code": 0, "data": {}, "message": ""}
    ret["data"]["task_id"] = task_id
    return ret



if __name__ == '__main__':

    # Create server
    server = SimpleXMLRPCServer(("localhost", 8000))
    server.register_function(run_task)
    server.register_function(kill_task)
    server.register_function(get_task_status)
    server.register_function(get_all_tasks)

    server.serve_forever()


#!/usr/bin/python3
import lxc
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


slave_id = "slave1"
slave_ip = "localhost"

task_status = {}

def get_all_tasks():
    return list(task_status.keys())

def get_task_status(data):
    task_id = data['name']
    return {"cluster":slave_id, "status": task_status[task_id]}

def check_task_exist(data):
	task_id = data['name']
	return task_id in task_status

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

    task_id = data['name']
    commandLine = data['commandLine']

    task_status[task_id] = "Pending"

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

    # Load the image
    image = data.get('image', None)
    if image is not None:
        rootfs_path = '/var/lib/lxc/%s/rootfs' % image
        c.set_config_item('lxc.rootfs', rootfs_path)
    
    # Limit the resource
    resource = data.get('resource', None)
    if resource is not None:
        if 'cpu' in resource:
            c.set_config_item('lxc.cgroup.cpuset.cpus', resource.get('cpu'))
        if 'memeory' in resource:
            c.set_config_item('lxc.cgroup.memory.limit_in_bytes', resource.get('memeory'))

    # Mount the package path
    package_path = data.get('packagePath', None)
    if package_path is not None:
        c.set_config_item('lxc.mount.entry', '%s home none bind,rw,create=dir 0 0' % package_path)
 
    # Start the container
    if not c.start():
        print("Failed to start the container", file=log_file)
        close_and_mark("Failed")
        return code_fail
    
    task_status[task_id] = "Running"

    """
    # print some information about container
    print("Container state: %s" % c.state)
    print("Container PID: %s" % c.init_pid)
    sys.stdout.flush()
    """

    success_flag = False

    # Wait for connectivity
    if not c.get_ips(timeout=30):
        print("Failed to connect the container", file=log_file)
        close_and_mark("Failed")
    else:
        # Execute the task
        retry_time = int(data.get('maxRetryCount', 0))
        
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
            close_and_mark("Unknown")
    
    # return
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
    server = SimpleXMLRPCServer((slave_ip, 8000))
    server.register_function(run_task)
    server.register_function(kill_task)
    server.register_function(check_task_exist)
    server.register_function(get_task_status)
    server.register_function(get_all_tasks)
    server.serve_forever()


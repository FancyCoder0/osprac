#!/usr/bin/python3
import lxc
import sys
import os

task_status = {}
task_belong = {}

def kill_task(task_id):
    c = lxc.Container(task_id)
    if c.state == "STOPPED":
        return {"code":0, "data":None, "message":""} # empty value
    
    # Try to stop
    c.stop()

    # Check if stop successfully
    if not c.stop():
        return {"code":1, "data": "fail", "message":""}
    else:
        return {"code":0, "data": "success", "message":""}


# sleep 6 && echo 10 && echo 20
def run_task(data):
    global task_status
    global task_belong

    slave_id = "slave1"

    task_id = data['name']
    commandLine = data['commandLine']
    
    code_succ = {"code":0, "task_id": task_id, "message":"successful!"}
    code_fail = {"code":1, "task_id": task_id, "message":"failed!"}
    
    out_file = open(data.get('outputPath', 'output.txt'), 'w+')
    log_file = open(data.get('logPath', 'log.txt'), 'w+')
    
    def close_and_mark(status_str):
        task_status[task_id] = status_str
        out_file.close()
        log_file.close()

    c = lxc.Container(task_id)
    lxc_choice = {"dist": "debian","release": "sid","arch": "amd64"}

    if not c.defined:
        # Create the container rootfs
        if not c.create("download", lxc.LXC_CREATE_QUIET, lxc_choice):
            print("Failed to create the container rootfs", file=log_file)
            close_and_mark("Failed")
            return code_fail

    # Start the container
    if not c.start():
        print("Failed to start the container", file=log_file)
        close_and_mark("Failed")
        return code_fail
    
    task_belong[task_id] = slave_id
    task_status[task_id] = "Running"

    # Query some information
    print("Container state: %s" % c.state)
    print("Container PID: %s" % c.init_pid)
    sys.stdout.flush()

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
        return code_fail
    
    # Shutdown the container
    if not c.shutdown(30):
        c.stop()
        if not c.stop():
            print("Failed to kill the container", file=log_file)
            close_and_mark("Failed")
            return code_fail

    close_and_mark("Succeeded")
    return code_succ

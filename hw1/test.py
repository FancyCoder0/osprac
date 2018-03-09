#!/usr/bin/python3
import lxc
import sys

# Setup the container object
c = lxc.Container("test_container")
if c.defined:
    print("Container already exists", file=sys.stderr)
    sys.exit(1)

# Create the container rootfs
if not c.create("download", lxc.LXC_CREATE_QUIET, {"dist": "debian",
                                                   "release": "sid",
                                                   "arch": "amd64"}):
    print("Failed to create the container rootfs", file=sys.stderr)
    sys.exit(1)

# Start the container
if not c.start():
    print("Failed to start the container", file=sys.stderr)
    sys.exit(1)

# Query some information
print("Container state: %s" % c.state)
print("Container PID: %s" % c.init_pid)

# Wait for connectivity
if not c.get_ips(timeout=30):
    print("Failed to connect the container", file=sys.stderr)
    sys.exit(1)

# Run the updates
# Write my name & id into file
c.attach_wait(lxc.attach_run_command,
	      ["bash","-c","echo 'Luyao Ren 1500012787' > Hello-Container"])
# Print file's contain
c.attach_wait(lxc.attach_run_command,
	      ["cat","Hello-Container"])
# Shutdown the container
if not c.shutdown(30):
    c.stop()
    if not c.stop():
        print("Failed to kill the container", file=sys.stderr)
        sys.exit(1)

"""
# Destroy the container
if not c.destroy():
    print("Failed to destroy the container.", file=sys.stderr)
    sys.exit(1)
"""

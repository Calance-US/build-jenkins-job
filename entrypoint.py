#!/usr/bin/env python3

# use of https://python-jenkins.readthedocs.io/en/latest/index.html
import json
import sys
import time

import jenkins


def mandatory_arg(argv):
    if argv == "":
        raise ValueError(
            "Only job_params can be empty. Required fields: url, token, user and path"
        )
    return argv


# mandatory
JENKINS_URL = mandatory_arg(sys.argv[1])
JENKINS_TOKEN = mandatory_arg(sys.argv[2])
JENKINS_USER = mandatory_arg(sys.argv[3])
JOB_PATH = mandatory_arg(sys.argv[4])

# not mandatory
JOB_PARAMS = sys.argv[5] or "{}"

# create/connect jenkins server
server = jenkins.Jenkins(
    f"https://{JENKINS_URL}", username=JENKINS_USER, password=JENKINS_TOKEN
)
user = server.get_whoami()
version = server.get_version()
print(f"Hello {user['fullName']} from Jenkins {version}")

split = JOB_PATH.split("job/")
job_name = "".join(split)
queue_id = server.build_job(
    job_name, parameters=json.loads(JOB_PARAMS), token=JENKINS_TOKEN
)

max_queue_polls = 30
poll_count = 0
build_number = None

while build_number is None and poll_count < max_queue_polls:
    queue_item = server.get_queue_item(queue_id)
    if "executable" in queue_item:
        build_number = queue_item["executable"]["number"]
        print(f"Build started: #{build_number}")
        break
    time.sleep(3)
    poll_count += 1

if build_number is None:
    print(
        f"ERROR: Max queue polls ({max_queue_polls}) reached — build has not started yet."
    )
    print(f"DEBUG: You can check the Jenkins pipeline here: {JENKINS_URL}/{JOB_PATH}")
    sys.exit(1)

status = None
while status is None:
    build_info = server.get_build_info(job_name, build_number)
    if build_info["building"]:
        print("Build still running...")
        time.sleep(5)
    else:
        status = build_info["result"]

print(f"Job finished with status: {status}")
print(f"::set-output name=job_status::{status}")

if status != "SUCCESS":
    sys.exit(1)

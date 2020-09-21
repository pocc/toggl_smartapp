# Proxy for smartthings requests to toggl 
# because smartthings groovy API is broken for httpPosts
# Use 200 instead of 4** return codes so user can see error
from flask import Flask, request 
from toggl.TogglPy import Toggl
import requests
import time
import json

app = Flask(__name__) 

def write_log(msg):
    print(msg)
    with open("smartapp.log", "a") as f:
        f.write("\n" + str(time.time()) + " | " + msg)

@app.route('/toggl_smartapp', methods=["GET"])
def print_post():
    write_log("Received: " + str(dict(request.args)))
    if "action" not in request.args or len(request.args["action"]) == 0 or request.args["action"] not in ["start", "stop"]:
        err_msg = "ERR: Action not provided or is not 'start' or 'stop'", 
        write_log(err_msg)
        return err_msg, 200 # 400
    if "toggl_api_token" not in request.args or len(request.args["toggl_api_token"]) == 0:
        err_msg = "ERR: Toggl API token not provided"
        write_log(err_msg)
        return err_msg, 200 # 400
    action = request.args["action"] 
    api_token = request.args["toggl_api_token"]
    toggl = Toggl()
    toggl.setAPIKey(api_token)
    if action == "stop":
        currentTimer = toggl.currentRunningTimeEntry()
        response = toggl.stopTimeEntry(currentTimer['data']['id'])
        write_log("Received from toggl:" + str(response))
        return response, 200
    
    if "desc" not in request.args or len(request.args["desc"]) == 0:
        err_msg = "ERR: Description not provided"
        write_log(err_msg)
        return err_msg, 200 # 400
    if "project" not in request.args or len(request.args["project"]) == 0:
        err_msg = "ERR: Project not provided"
        write_log(err_msg)
        return err_msg, 200 # 400
    desc = request.args["desc"]
    project_name = request.args["project"]
       
    write_log("Sending request for workspaces")
    workspaces = toggl.request("https://api.track.toggl.com/api/v8/workspaces") 
    all_projects = []
    for w in workspaces:
        workspace_id = w["id"]
        resp = toggl.request(f"https://api.track.toggl.com/api/v8/workspaces/{workspace_id}/projects")
        # Resp can be none if a workspace has no projects
        if resp:
            all_projects += resp
    all_project_names = [p["name"] for p in all_projects]
    if project_name not in all_project_names:
        err_msg = f"ERR: Project with name `{project_name}` not found."
        write_log(err_msg)
        return err_msg, 200 # 404
    project_id = -1
    for p in all_projects:
        if p["name"] == project_name:
            project_id = p["id"]
    if project_id == -1:
        err_msg = f"ERR: No project ID can be found for project with name `{project_name}`."
        write_log(err_msg)
        return err_msg, 200 # 404
    write_log(f"Performing action {action} on entry.")
    response = toggl.startTimeEntry(desc, project_id)
    write_log("Received from toggl:" + str(response))
    return response, 200
app.run(host='157.245.238.3', port=5432, debug=True)


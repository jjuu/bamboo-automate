import logging
from .. import requests
import re

from collections import OrderedDict


def get_tasks(conn, job_id, sort_by_title=False):
    params = {
        "buildKey": job_id
    }
    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/editBuildTasks.action',
        params)

    root = res  # .getroot()

    tasks = OrderedDict()

    li_items = root.find_class('item')
    for order_id, li in enumerate(li_items, start=1):
        key = int(li.attrib['data-item-id'])
        edit_link = None
        del_link = None
        title = li.find('.//h3').text
        description = None
        try:
            description = li.find('.//div').text
        except:
            pass
        links = li.findall('.//a')
        for l in links:
            href = l.attrib['href']
            match = re.search('editTask', href)
            if match:
                edit_link = href
            match = re.search('confirmDeleteTask', href)
            if match:
                del_link = href
                req_id = href

        if sort_by_title:
            title_desc = (title, description)
            tasks[title_desc] = {
                'task_id': key,
                'title': title,
                'description': description,
                'edit_link': edit_link,
                'del_link': del_link,
                'order_id': order_id
            }

        else:
            tasks[key] = {
                'task_id': key,
                'title': title,
                'description': description,
                'edit_link': edit_link,
                'del_link': del_link,
                'order_id': order_id
            }

    return tasks


def get_task_params(conn, job_id, task_id):
    # '/build/admin/edit/editTask.action?planKey=DNSWRD-CIM-JOB0&taskId=1'
    params = {
        "planKey": job_id,
        "taskId": task_id
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/editTask.action',
        params)

    html_root = res
    task_params = OrderedDict()
    form = html_root.find('.//form[@id="updateTask"]')
    li_inputs = form.findall('.//input')
    selects = form.findall('.//select')
    for input in li_inputs:
        name = input.attrib.get('name')
        type = input.attrib.get('type')
        if type == "checkbox":
            is_checked = input.attrib.get('checked')
            if is_checked and is_checked == "checked":
                value = "true"
            else:
                value = "false"
        else:
            value = input.attrib.get('value')

        task_params[name] = value

    for select in selects:
        name = select.attrib.get('name')
        value = select.value
        if not value:
            value = select.value_options[0]
        task_params[name] = value

    return task_params


def update_task(conn, job_id, task_id, task_params):
    params = {
        "bamboo.successReturnMode": "json",
        "planKey": job_id,
        "checkBoxFields": "taskDisabled",
        "confirm": "true",
        "createTaskKey": task_id,
        "decorator": "nothing",
        "taskId": 0,
        "finalising": "true",
        "userDescription": None

    }

    params.update(task_params)

    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/build/admin/edit/updateTask.action',
        params)

    return res


def add_job_task(conn, job_id,  task_params):
    params = {
        "bamboo.successReturnMode": "json",
        "planKey": job_id,
        "checkBoxFields": "taskDisabled",
        "confirm": "true",
        "createTaskKey": "",
        "decorator": "nothing",
        "taskId": 0,
        "finalising": "true",
        "userDescription": None
    }
    params.update(task_params)
    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/build/admin/edit/createTask.action',
        params)

    return res


def delete_job_task(conn, job_id, task_id):
    params = {
        "bamboo.successReturnMode": "json",
        "planKey": job_id,
        "confirm": "true",
        "createTaskKey": None,
        "decorator": "nothing",
        "taskId": task_id
    }
    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/build/admin/edit/deleteTask.action',
        params)

    return res


def move_job_task(conn, job_id, task_id, finalising=False, beforeId=None, afterId=None):
    """ Move a task in the runtime order.

    Arguments:
    conn -- the connection object
    job_id -- the id of the job
    task_id -- the id of the task to move
    finalising -- true, if task should be a final task
    beforeId -- id of the task which should be before this task
    afterId -- id of the task which should be after this taks

    """
    params = {
        "planKey": job_id,
        "finalising": "true" if finalising else "false",
        "taskId": task_id
    }
    if beforeId:
        params.update({"beforeId": beforeId})
    if afterId:
        params.update({"afterId": afterId})
    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/build/admin/ajax/moveTask.action',
        params)
    logging.debug(params)

    return res


def update_environment_variables(conn, job_id, task_id, environment_variables):
    task_params = get_task_params(conn, job_id, task_id)
    if task_params.get('environmentVariables') is None:
        return
    task_params['environmentVariables'] = environment_variables

    return update_task(conn, job_id, task_id, task_params)


def add_repository(conn, job_id, task_id, repository_id, checkout_dir):
    task_params = get_task_params(conn, job_id, task_id)
    checkout_dirs = OrderedDict()
    for param_name, param_value in task_params.items():
        res = re.findall('checkoutDir_(\d)', param_name)
        if res:
            checkout_dirs[int(res[0])] = param_value
    if len(checkout_dirs) == 0 or checkout_dir in checkout_dirs.values():
        return

    selcted_index = max(checkout_dirs.keys()) + 1
    task_params['selectedRepository_%s' % selcted_index] = repository_id
    task_params['checkoutDir_%s' % selcted_index] = checkout_dir

    return update_task(conn, job_id, task_id, task_params)


def add_job_task_script(conn, job_id, is_task_disabled=False, task_description="", script_location="INLINE",
                        script="pwd", argument="", environment_variables="", working_sub_directory=""):
    script_params = {
        "userDescription": task_description,
        "checkBoxFields": "taskDisabled",
        "scriptLocation": script_location,
        "selectFields": "scriptLocation",
        "checkBoxFields": "runWithPowershell",
        "script": script if script_location == "FILE" else "",
        "scriptBody": script if script_location == "INLINE" else "",
        "argument": argument,
        "environmentVariables": environment_variables,
        "workingSubDirectory": working_sub_directory,
        "createTaskKey": "com.atlassian.bamboo.plugins.scripttask:task.builder.script",
        "taskId": "0",
        "planKey": job_id,
        "bamboo.successReturnMode": "json",
        "decorator": "nothing",
        "confirm": "true"
    }
    if is_task_disabled:
        script_params['taskDisabled'] = 'true'

    return add_job_task(conn, job_id, script_params)

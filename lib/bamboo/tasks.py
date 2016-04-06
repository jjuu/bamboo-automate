import re
import sys
import logging
from collections import OrderedDict

from .. import requests
import constants

from .jobs import get_jobs


def get_tasks(conn, job_id, sort_by_title=False):
    params = {
        "buildKey": job_id
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/editBuildTasks.action',
        params)

    tasks = OrderedDict()

    li_items = res.find_class('item')
    for order_id, li in enumerate(li_items, start=1):
        data_item_id = int(li.attrib['data-item-id'])
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
                'task_id': data_item_id,
                'title': title,
                'description': description,
                'edit_link': edit_link,
                'del_link': del_link,
                'order_id': order_id
            }
        else:
            tasks[data_item_id] = {
                'task_id': data_item_id,
                'title': title,
                'description': description,
                'edit_link': edit_link,
                'del_link': del_link,
                'order_id': order_id
            }

    return tasks


def get_task_edit_html(conn, job_id, task_id):
    params = {
        "planKey": job_id,
        "taskId": task_id
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/editTask.action',
        params)

    return res


def get_task_params(conn, job_id, task_id, form_html=None):

    if form_html is None:
        params = {
            "planKey": job_id,
            "taskId": task_id
        }

        html_root = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/build/admin/edit/editTask.action',
            params
        )
    else:
        html_root = form_html

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

    check_box_field_list = []
    check_box_fields = form.findall('.//input[@name="checkBoxFields"]')
    for cbf in check_box_fields:
        check_box_field_list.append(cbf.value)

    task_params['checkBoxFields'] = check_box_field_list

    select_field_list = []
    select_fields = form.findall('.//input[@name="selectFields"]')
    for sf in select_fields:
        select_field_list.append(sf.value)

    task_params['selectFields'] = select_field_list

    return task_params


def __update_task(conn, params):
    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/build/admin/edit/updateTask.action',
        params)

    return res


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

    return __update_task(conn, params)


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


def add_job_task_script(conn, job_id, is_task_disabled=False, is_run_with_power_shell=False, task_description="",
                        script_location="INLINE", script="pwd", argument="", environment_variables="",
                        working_sub_directory=""):
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

    if is_run_with_power_shell:
        script_params['runWithPowershell'] = 'true'

    return add_job_task(conn, job_id, script_params)


def is_task_exist(conn, task_name, stage_key, script_path):
    """
    Figure out if the task exists already for bamboo v5.7.2+
    :return:
    """
    params = {
        "buildKey": stage_key
    }

    html_root = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/editBuildTasks.action',
        params)

    task_html = html_root.findall('.//li[@class="item"]')

    task_params = {
        'planKey': stage_key
    }

    for task_item in task_html:
        task_id = task_item.attrib.get('data-item-id')

        task_params.update({
            'taskId': task_id
        })

        task_html_root = requests.get_ui_return_html(
                            conn,
                            conn.baseurl + '/build/admin/edit/editTask.action',
                            task_params)

        task_heading = task_html_root.find('.//div[@class="task-heading"]').find('.//h2').text
        if task_heading == task_name:
            input_elt = task_html_root.find('.//input[@id="script"]')
            if input_elt.value == script_path:
                return True

    return False


def find_jobs_keys_from_plan(conn, plan_key):
    """
    Find all stage keys from plan for bamboo v5.7.2+
    :param conn:
    :param plan_key:
    :return:
    """
    params = {
        "planKey": plan_key
    }

    html_root = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/defaultStages.action',
        params)

    edit_task_html = html_root.find('.//ul[@id="editstages"]')
    if edit_task_html is None:
        return None

    stage_html_list = edit_task_html.findall('.//a[@class="job"]')

    stage_key_info = {}
    for stage_html in stage_html_list:
        stage_key = stage_html.attrib['id'].replace('viewJob_', '')
        stage_name = stage_html.text
        stage_key_info[stage_key] = stage_name

    return stage_key_info


def create_job_task_with_script(conn, plan_key, task_desc, script_path, argument,
                                environment_variables, working_sub_directory):
    """
    For bamboo v5.7.2+
    :param conn:
    :param user_desc: like Update Kernel Fragments
    :param plan_key: like DNSWRD-SDKLPY-PPCE5
    :param environmentVariables: like ARCH="ppce500mc"
    :param script_path: like '../ci/kernel_fragments.sh'
    :param working_sub_directory: linux
    :return:
    """
    params = {
        'userDescription': task_desc,
        'checkBoxFields': 'taskDisabled',
        'scriptLocation': 'FILE',
        'selectFields': 'scriptLocation',
        'checkBoxFields': 'runWithPowershell',
        'script': script_path,
        'scriptBody': None,
        'argument': argument,
        'environmentVariables': environment_variables,
        'workingSubDirectory': working_sub_directory,
        'createTaskKey': 'com.atlassian.bamboo.plugins.scripttask:task.builder.script',
        'taskId': '0',
        'planKey': plan_key,
        'bamboo.successReturnMode': 'json',
        'decorator': 'nothing',
        'confirm': 'true',
    }

    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/build/admin/edit/createTask.action',
        params)

    return res


def batch_create_job_task_with_script(conn, plan_key, script_path,
                                      task_desc='',
                                      argument='',
                                      environment_variables='',
                                      working_sub_directory=''):
    """
    Batch create task for all the stages in a task. For bamboo v5.7.2+
    :param conn:
    :param plan_key:
    :param task_desc:
    :param environment_variables:
    :param script_path:
    :param working_sub_directory:
    :return:
    """
    jobs = find_jobs_keys_from_plan(conn, plan_key)

    if jobs is None:
        logging.error(constants.INCORRECT_PLAN_KEY_ERROR_MSG % plan_key)
        return

    for job_key, job_name in jobs.iteritems():
        is_task_exist_flag = is_task_exist(conn, 'Script configuration', job_key, script_path)
        if is_task_exist_flag:
            logging.info('Task %s with a script "%s" already exists.' % (job_name, script_path))
        else:
            environment_variables = __replace_job_name(environment_variables, job_name)
            script_info = (job_key, task_desc, script_path,
                            argument, environment_variables,
                            working_sub_directory)

            logging.info('Create one task for job %s.\n\t'
                         ' Description: %s\n\t'
                         ' Script_path: %s\n\t'
                         ' Argument: %s\n\t'
                         ' environment_variables: %s\n\t'
                         ' working_sub_directory:%s' % script_info)

            create_job_task_with_script(conn, *script_info)


def __replace_job_name(environment_variables, job_name):
    env_vars = {}
    if re.search('{.+}', environment_variables) is not None:
        if re.search('{.+}', environment_variables) is not None:
            for env_var in re.findall('{.+}', environment_variables):
                if env_var.strip('{}') == constants.KEY_OF_JOB_NAME:
                    env_vars[constants.KEY_OF_JOB_NAME] = job_name
                else:
                    logging.error('Not supported type of variable: %s.' % env_var)

            if env_vars:
                environment_variables = environment_variables.format(**env_vars)

    return environment_variables


def update_job_script_task(conn, plan_key, task_title, job_key=None, task_desc=None, script_path=None,
                           update_task_desc=None, argument=None,
                           environment_variables=None, working_sub_directory=None,
                           disable_task_flag=None, run_as_powershell_flag=None,
                           env_var_key=None, env_var_value=None, mode='override'):

    params = [script_path, update_task_desc, argument, environment_variables,
              working_sub_directory, disable_task_flag, run_as_powershell_flag,
              env_var_key, env_var_value]

    param_none = filter(lambda x: x is None, params)
    if len(param_none) == len(params):
        logging.warning('Need parameters to update.')
        return
    else:
        update_params = {}
        if script_path is not None:
            update_params['script'] = script_path

        if update_task_desc is not None:
            update_params['userDescription'] = update_task_desc

        if argument is not None:
            update_params['argument'] = argument

        if environment_variables is not None:
            update_params['environmentVariables'] = environment_variables

        if working_sub_directory is not None:
            update_params['workingSubDirectory'] = working_sub_directory

        if env_var_key is not None:
            update_params['environmentVariables'] = ''

    task_title = task_title.lower()
    jobs = get_jobs(conn, plan_key)

    for __job_key, job_info in jobs.iteritems():
        if job_key is not None and job_key != __job_key.split('-')[2]:
            continue

        tasks = get_tasks(conn, __job_key)
        for task_id, task_info in tasks.iteritems():
            task_title_temp = task_info['title'].lower()
            task_desc_temp = task_info['description']
            if task_desc_temp is None:
                task_desc_temp = ''

            if task_title != task_title_temp:
                continue
            elif (task_desc is not None and task_desc == task_desc_temp.lower())\
                        or (task_desc is None):
                origin_task_params = get_task_params(conn, __job_key, task_id)

                if origin_task_params['scriptLocation'] != 'FILE':
                    continue

                params = {
                    'userDescription': update_task_desc,
                    'scriptLocation': 'FILE',
                    'selectFields': 'scriptLocation',
                    'checkBoxFields': 'runWithPowershell',
                    'script': script_path,
                    'scriptBody': '',
                    'argument': argument,
                    'environmentVariables': environment_variables,
                    'workingSubDirectory': working_sub_directory,
                    'taskId': task_id,
                    'planKey': plan_key,
                    'bamboo.successReturnMode': 'json',
                    'decorator': 'nothing',
                    'confirm': 'true',
                }

                params.update(origin_task_params)

                if mode == constants.update_task_mode_append:
                    update_params_with_append = {}
                    for form_name, form_value in update_params.iteritems():
                        update_params_with_append[form_name] = '%s %s' % (origin_task_params[form_name], form_value)

                    params.update(update_params_with_append)
                elif mode == constants.update_task_mode_modify:
                    env_var_items_list = []
                    update_params_with_modify = {}
                    if 'environmentVariables' in update_params:
                        origin_env_var = origin_task_params['environmentVariables']
                        for env_var_items in origin_env_var.split(' '):
                            env_var_item_list = env_var_items.split('=')
                            if len(env_var_item_list) == 2:
                                previous_env_var_item_key = env_var_item_list[0]
                                previous_env_var_item_value = env_var_item_list[1]

                                if previous_env_var_item_key == env_var_key:
                                    env_var_items_list.append('%s=%s' % (previous_env_var_item_key, env_var_value))
                                else:
                                    env_var_items_list.append('%s=%s' % (previous_env_var_item_key, previous_env_var_item_value))
                            else:
                                env_var_items_list.append(env_var_items)

                        update_params_with_modify['environmentVariables'] = ' '.join(env_var_items_list)

                    params.update(update_params_with_modify)
                else:
                    params.update(update_params)

                if disable_task_flag is True:
                    params['taskDisabled'] = 'true'
                elif disable_task_flag is False:
                    params['taskDisabled'] = 'false'

                if run_as_powershell_flag is True:
                    params['runWithPowershell'] = 'true'
                elif run_as_powershell_flag is False:
                    params['runWithPowershell'] = 'false'

                params['checkBoxFields'] = ['taskDisabled', 'runWithPowershell']
                params['environmentVariables'] = __replace_job_name(params['environmentVariables'], job_info[0])

                requests.post_ui_return_html(
                    conn,
                    conn.baseurl + '/build/admin/edit/updateTask.action',
                    params
                )

                logging.info('Success to update %s, Job name: %s, Title: %s' % (plan_key, job_info[0], task_title))


def update_source_code_checkout_config(conn, plan_key, job_short_key,
                                       checkout_number, repo_name, checkout_dir):
    job_key = '%s-%s' % (plan_key, job_short_key)
    tasks = get_tasks(conn, job_key)
    for task_id, task_info in tasks.iteritems():
        task_title = task_info['title']
        if constants.TASK_TITLE_SOURCE_CODE_CHECKOUT == task_title:
            selected_repo_name_key = 'selectedRepository_%s' % checkout_number
            checkout_dir_key = 'checkoutDir_%s' % checkout_number
            edit_html = get_task_edit_html(conn, job_id=job_key, task_id=task_id)
            task_params = get_task_params(conn, job_id=job_key, task_id=task_id, form_html=edit_html)
            selected_repo = edit_html.find('.//select[@name="%s"]' % selected_repo_name_key)
            if selected_repo is None:
                logging.error('Invalid checkout number %s' % checkout_number)
                return
            else:
                checkout_options = selected_repo.findall('.//option')
                for option in checkout_options:
                    option_value = option.attrib.get('value')
                    if repo_name == 'default' and option_value == constants.TASK_REPO_DEFAULT_VALUE:
                        task_params[selected_repo_name_key] = constants.TASK_REPO_DEFAULT_VALUE
                    elif option.text == repo_name:
                        task_params[selected_repo_name_key] = option_value

            if checkout_dir is None:
                checkout_dir = edit_html.find('.//input[@name="%s"]' % checkout_dir_key).value

            if checkout_dir_key in task_params:
                task_params[checkout_dir_key] = checkout_dir

            return __update_task(conn, params=task_params)

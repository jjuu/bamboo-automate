import logging
from .. import requests

from collections import OrderedDict


def get_job_short_key(job_key):
    keys = job_key.split('-')
    if len(keys) != 3:
        raise Exception('Job key error')
    else:
        return keys[-1]


def get_jobs(conn, plan_id, sort_by_title=False):
    params = {
        "buildKey": plan_id
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/editChainDetails.action',
        params)

    root = res  # .getroot()

    jobs = OrderedDict()

    li_jobkeys = root.findall('.//li[@data-job-key]')
    for li in li_jobkeys:
        key = li.attrib['data-job-key']
        edit_link = li.find('.//a').attrib['href']
        del_link = None
        title = li.find('.//a').text
        description = None
        try:
            description = li.attrib['title']
        except:
            pass

        if sort_by_title:
            jobs[title] = (key, description, edit_link, del_link,)
        else:
            jobs[key] = (title, description, edit_link, del_link,)

    return jobs


def get_job_params(conn, job_id):
    params = {
        "buildKey": job_id
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/editBuildDetails.action',
        params)

    html_root = res
    job_params = OrderedDict()
    form = html_root.find('.//form[@id="updateBuildDetails"]')
    li_inputs = form.findall('.//input')
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
        job_params[name] = value

    return job_params


def disable_job(conn, job_id):
    job_params = get_job_params(conn, job_id)
    params = {
        "buildKey": job_params.get('buildKey'),
        "buildName": job_params.get('buildName'),
        'buildDescription': job_params.get('buildDescription'),
        "checkBoxFields": "enabled",
        "save": "Save"
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/updateBuildDetails.action',
        params)

    return res


def enable_job(conn, job_id):
    job_params = get_job_params(conn, job_id)
    params = {
        "buildKey": job_params.get('buildKey'),
        "buildName": job_params.get('buildName'),
        'buildDescription': job_params.get('buildDescription'),
        "checkBoxFields": "enabled",
        "enabled": "true",
        "save": "Save"
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/updateBuildDetails.action',
        params)

    return res


def add_one_job(conn, plan_id, job_name, job_description, is_enabled=True, job_key=None):

    if job_key:
        sub_build_key = job_key.upper()
    else:
        sub_build_key = job_name.upper()

    sub_build_key = filter(str.isupper, sub_build_key.upper())

    params = {
        "buildKey": plan_id,
        "existingStage": "Build and Analyze",
        "buildName": job_name,
        "subBuildKey": sub_build_key,
        "buildDescription": job_description,
        "tmp.createAsEnabled": "true" if is_enabled else "false",
        "checkBoxFields": "tmp.createAsEnabled",
        "bamboo.successReturnMode": "json-as-html",
        "confirm": "nothing"
    }

    res = requests.post_ui_no_return(
        conn,
        conn.baseurl + '/chain/admin/createJob.action',
        params)

    return res


def change_jobs_status_by_key(conn, plan_id, job_keys, enable_true_disable_false=False):
    if not job_keys:
        return

    jobs = get_jobs(conn, plan_id)

    for job_key, job_info in jobs.iteritems():
        short_job_key = get_job_short_key(job_key)
        if short_job_key in job_keys:
            if enable_true_disable_false:
                enable_job(conn, job_key)
                logging.info('Enable job: %s :: %s' % (job_info[0], short_job_key))
            else:
                disable_job(conn, job_key)
                logging.info('Disable job: %s :: %s' % (job_info[0], short_job_key))


def get_stages(conn, plan_id):
    params = {
        "planKey": plan_id
    }

    html_root = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/defaultStages.action',
        params)

    return html_root


def clone_job(conn, plan_id, stage_name, job_name, job_short_id, plan_id_to_clone, job_id_to_clone,
              desc='', enable_job_flag=True):
    if stage_name is None:
        html_root = get_stages(conn, plan_id)
        stages = html_root.find('.//ul[@id="editstages"]').findall('.//dt')
        if not stages:
            logging.error('No stages found.')
        else:
            stage_name = stages[0].text

    params = {
        'buildKey': plan_id,
        'buildName': job_name,
        'subBuildKey': job_short_id,
        'chainKeyToClone': plan_id_to_clone,
        'jobKeyToClone': job_id_to_clone,
        'selectFields': ['chainKeyToClone', 'jobKeyToClone'],
        'existingStage': stage_name,
        'buildDescription': desc,
        'checkBoxFields': 'tmp.createAsEnabled',
        'cloneJob': 'true',
        'ignoreUnclonableSubscriptions': 'false',
        'bamboo.successReturnMode': 'json',
        'decorator': 'nothing',
        'confirm': 'true'
    }

    if enable_job_flag is True or enable_job_flag == 'true':
        params['tmp.createAsEnabled'] = 'true'

    res = requests.post_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/createClonedJob.action',
        params
    )

    return res
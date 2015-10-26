import logging
from .. import requests

from collections import OrderedDict


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
    params = {
        "bamboo.successReturnMode": "json",
        "buildKey": plan_id,
        "buildName": job_name,
        "subBuildKey": job_key.upper() if job_key else job_name.upper(),
        "buildDescription": job_description,
        "existingStage": "Default Stage",
        "checkBoxFields": "tmp.createAsEnabled",
        "tmp.createAsEnabled": "true" if is_enabled else "false",
        "save": "Create job"
    }

    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/chain/admin/createJob.action',
        params)

    return res
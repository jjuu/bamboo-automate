import logging
from .. import requests
import re


def _get_requirements(conn, job_id):
    params = {
        "buildKey": job_id
    }
    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/build/admin/edit/defaultBuildRequirement.action',
        params)

    root = res  # .getroot()

    requirements = {}

    td_labels = root.find_class('labelCell')
    for td in td_labels:
        key = None
        req_id = None
        edit_link = None
        del_link = None
        tr = td.getparent()
        links = tr.findall('.//a')
        for l in links:
            href = l.attrib['href']
            match = re.search('capabilityKey=(.*)', href)
            if match:
                key = match.group(1)
            match = re.search('editBuildRequirement.*requirementId=(\d+)', href)
            if match:
                edit_link = href
                req_id = match.group(1)
            match = re.search('deleteBuildRequirement.*requirementId=(\d+)', href)
            if match:
                del_link = href
                req_id = match.group(1)

        if not key:
            key = td.text.strip()

        requirements[key] = (req_id, edit_link, del_link,)

    return requirements


def delete_job_requirement(conn, job_id, req_key):
    requirements = _get_requirements(conn, job_id)
    logging.debug('%s', requirements)
    res = None
    req_id, _, del_link = requirements[req_key]
    if req_id != None:
        res = requests.post_ui_no_return(conn, del_link, {})

    return res


def delete_job_all_requirements(conn, job_id):
    requirements = _get_requirements(conn, job_id)
    res = None
    for req_id, _, del_link in requirements.itervalues():
        if req_id != None:
            res = requests.post_ui_no_return(conn, del_link, {})

    return res


def get_job_requirement(conn, job_id):
    requirements = {}
    res = requests.get_ui_return_json(
        conn,
        conn.baseurl + '/rest/api/latest/config/job/' + job_id + '/requirement', None)
    if not res:
        return requirements
    for re in res:
        key = re.get('key')
        if key:
            requirements[key] = {
                'key': key,
                'matchType': re.get('matchType'),
                'matchValue': re.get('matchValue')
            }
    return requirements


def add_job_requirement(conn, job_id, req_key, req_value):
    requirements = get_job_requirement(conn, job_id)
    if requirements and req_key in requirements.keys():
        return None
    params = {
        "key": req_key,
        "matchType": "EQUALS",
        "matchValue": req_value
    }
    logging.debug(params)
    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/rest/api/latest/config/job/' + job_id + '/requirement',
        params, content_type='application/json')

    return res


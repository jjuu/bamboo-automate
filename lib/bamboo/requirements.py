import re
import logging

from . import constants
from .. import requests


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
                'rid': re.get('id'),
                'key': key,
                'matchType': re.get('matchType'),
                'matchValue': re.get('matchValue')
            }
    return requirements


def add_job_requirement(conn, job_id, require_key, require_type, require_value=None, mode='update'):
    if require_type not in constants.requirements:
        logging.error('Invalid require type: %s' % require_type)
        return None

    require_type = require_type.upper()
    requirements = get_job_requirement(conn, job_id)

    if requirements and require_key in requirements.keys():
        requirement = requirements[require_key]
        rid = requirement['rid']

        if require_type != 'EXISTS':
            if mode == constants.REQUIREMENT_MODIFY_MODE_ADD:
                logging.info('Key(%s) already in job(%s). Do nothing about it.' % (require_key, job_id))
                return
            elif mode == constants.REQUIREMENT_MODIFY_MODE_APPEND:
                origin_value = requirements[require_key].get('matchValue')
                if require_value in origin_value.split(constants.AGENT_SLICE_MARK):
                    logging.info('Agent(%s) already exists in %s. ' % (require_value, origin_value))
                    return
                else:
                    logging.info('Key(%s) already in job(%s). Append new agent to the end.' % (require_key, job_id))

                require_value = origin_value + constants.AGENT_SLICE_MARK + require_value
            elif mode == constants.REQUIREMENT_MODIFY_MODE_UPDATE:
                logging.info('Key(%s) already in job(%s). Update to %s :: %s :: %s.'
                             % (require_key, job_id, require_key, require_type, require_value))
            else:
                logging.error('Invalid mode.')
                return

            params = {
                'id': rid,
                'matchType': require_type,
                'matchValue': require_value
            }
        else:
            params = {
                'id': rid,
                'matchType': require_type
            }

        res = requests.put_rest_return_json(
                conn,
                '/rest/api/latest/config/job/%s/requirement/%s' % (job_id, requirement['rid']),
                params
        )

        return res
    else:
        params = {
            "key": require_key,
            "matchType": require_type
        }

        if require_value is not None:
            params['matchValue'] = require_value

        res = requests.post_ui_return_json(
            conn,
            conn.baseurl + '/rest/api/latest/config/job/' + job_id + '/requirement',
            params,
            content_type='application/json')

        logging.info('Add agent(%s :: %s :: %s) to job(%s).'
                     % (require_key, require_type, require_value, job_id))
        return res

import logging
from .. import requests

from collections import OrderedDict


def _iterate_json_entity_results(request, conn, entity, path, params):
    start_index = 0
    params.update({
        "start-index": start_index
    })
    entities = entity + 's'
    res = request(conn, path, params)
    logging.debug('%s', res[entities]['max-result'])
    part_result_size = res[entities]['max-result']
    result_size = res[entities]['size']
    part_res = res
    while start_index <= result_size:
        logging.debug('size = %s max-result = %s', res[entities]['size'], res[entities]['max-result'])
        logging.debug('start_index = %s', start_index)
        start_index = start_index + part_result_size
        params.update({
            "start-index": start_index
        })
        part_res = request(conn, path, params)
        res[entities][entity].extend(part_res[entities][entity])

    return res


def _get_entity(conn, entity, expand):
    params = {
        "expand": expand
    }

    res = _iterate_json_entity_results(
        requests.get_rest_return_json,
        conn,
        entity,
        conn.baseurl + '/rest/api/latest/' + entity,
        params)

    return res


def get_plans(conn, expand=''):
    return _get_entity(conn, 'plan', expand)


def get_projects(conn, expand=''):
    return _get_entity(conn, 'project', expand)


def get_plans_of_project(conn, project_id):

    params = {
        'expand': 'plans.plan',
        'start-index': 0
    }

    start_index = 0
    plans = []

    res = requests.get_rest_return_json(
            conn,
            conn.baseurl + '/rest/api/latest/project/%s' % project_id,
            params)

    plans.extend(res['plans']['plan'])

    part_result_size = res['plans']['max-result']
    result_size = res['plans']['size']

    while start_index <= result_size:
        start_index = start_index + part_result_size
        params.update({'start-index': start_index})

        res = requests.get_rest_return_json(
            conn,
            conn.baseurl + '/rest/api/latest/project/%s' % project_id,
            params)

        for p in res['plans']['plan']:
            if p not in plans:
                plans.append(p)

    return plans


def get_plan_params(conn, plan_id):
    params = {
        "buildKey": plan_id
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/editChainDetails.action',
        params)

    html_root = res
    plan_params = OrderedDict()
    form = html_root.find('.//form[@id="saveChainDetails"]')
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
        plan_params[name] = value

    return plan_params


def disable_plan(conn, plan_id):
    plan_params = get_plan_params(conn, plan_id)

    params = {
        "buildKey": plan_params.get('buildKey'),
        "projectName": plan_params.get('projectName'),
        'chainName': plan_params.get('chainName'),
        'chainDescription': plan_params.get('chainDescription'),
        "checkBoxFields": "enabled",
        "save": "Save"
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/saveChainDetails.action',
        params)

    return res


def enable_plan(conn, plan_id):
    plan_params = get_plan_params(conn, plan_id)

    params = {
        "buildKey": plan_params.get('buildKey'),
        "projectName": plan_params.get('projectName'),
        'chainName': plan_params.get('chainName'),
        'chainDescription': plan_params.get('chainDescription'),
        "checkBoxFields": "enabled",
        "enabled": "true",
        "save": "Save"
    }

    res = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/saveChainDetails.action',
        params)

    return res
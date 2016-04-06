import json
import logging
from .. import requests

from collections import OrderedDict


def get_queue_plans(conn):
    params = {
        'expand': 'queuedBuilds'
    }

    queue_plans = requests.get_rest_return_json(
                      conn,
                      conn.baseurl + '/rest/api/latest/queue',
                      params
                  )

    size = queue_plans.get('queuedBuilds').get('size')
    if size != 0:
        return queue_plans.get('queuedBuilds').get('queuedBuild')
    else:
        return []


def queue_filter(conn, queue_plans, project_short_key, plan_short_keys=None):
    plans = []
    for plan in queue_plans:
        plan_key = plan.get('planKey')
        __proj_short_key, __plan_short_key, __job_short_key = __get_plan_info(plan_key)
        if project_short_key == __proj_short_key and plan_short_keys is None:
            plans.append(plan)
        elif project_short_key == __proj_short_key and __plan_short_key in plan_short_keys:
            plans.append(plan)

    return plans


def get_secondary_plans(conn, queue_plans, project_short_key, primary_short_plan_keys):
    primary_plan_keys = ['%s-%s' % (project_short_key, pspk) for pspk in primary_short_plan_keys]
    def is_sub_branch(plan_key):
        __proj_short_key, __plan_short_key, __job_short_key = __get_plan_info(plan_key)
        if '%s-%s-' % (__proj_short_key, __plan_short_key) not in primary_plan_keys:
            pass

    secondary_plans = []
    for plan in queue_plans:
        plan_key = plan['planKey']
        __proj_short_key, __plan_short_key, __job_short_key = __get_plan_info(plan_key)

        if __proj_short_key == project_short_key and __plan_short_key not in primary_short_plan_keys:
            secondary_plans.append(plan)

    return secondary_plans


def __get_plan_info(plan_key):
    __proj_short_key, __plan_short_key, __job_short_key = plan_key.split('-')
    return __proj_short_key, __plan_short_key, __job_short_key


def set_plan_before(conn, queue_plans, result_key, prev_result_key):
    params = {
        'resultKey': result_key,
        'prevResultKey': prev_result_key,
        'itemType': 'BUILD'
    }

    requests.post_ui_no_return(
        conn,
        conn.baseurl + '/bamboo/build/admin/ajax/reorderBuild.action',
        params
    )


def reorder_plans(conn, short_project_key, primary_short_plan_keys):
    queue_plans = get_queue_plans(conn)

    secondary_plans = get_secondary_plans(conn, queue_plans, short_project_key, primary_short_plan_keys)
    logging.info('secondary_plan_keys: %s' % ', '.join([sp['planKey'] for sp in secondary_plans]))

    if secondary_plans:
        first_secondary_plan = secondary_plans[0]
        first_secondary_plan_index = queue_plans.index(first_secondary_plan)
        for index in range(first_secondary_plan_index + 1, len(queue_plans)):
            primary_plan = queue_plans[index]

            __proj_short_key, __plan_short_key, __job_short_key = __get_plan_info(primary_plan['planKey'])
            if __proj_short_key == short_project_key and __plan_short_key in primary_short_plan_keys:
                if first_secondary_plan_index == 0:
                    prev_result_key = ''
                else:
                    prev_result_key = queue_plans[first_secondary_plan_index - 1]['buildResultKey']

                set_plan_before(conn, queue_plans, primary_plan['buildResultKey'], prev_result_key)

































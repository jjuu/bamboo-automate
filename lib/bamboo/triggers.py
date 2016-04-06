
import logging
from collections import OrderedDict

from .. import requests

import constants


def get_trigger_id_list(conn, plan_id, trigger_name, trigger_desc=None):
    """
    Get all the trigger ids
    :param conn:
    :param plan_id:
    :param trigger_name:
    :param trigger_desc:
    :return:
    """
    params = {
        "buildKey": plan_id,
    }

    trigger_name = trigger_name.lower()

    html_root = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/editChainTriggers.action',
        params)

    trigger_id_list = []

    editor_html = html_root.find('.//div[@id="panel-editor-list"]')
    if editor_html is None:
        logging.error(constants.INCORRECT_PLAN_KEY_ERROR_MSG % plan_id)
        return None

    trigger_list = editor_html.findall('.//li[@class="item"]')
    for index, trigger_html in enumerate(trigger_list):
        tri_name = trigger_html.find('.//*[@class="item-title"]').text.lower()
        tri_desc_html = trigger_html.find('.//*[@class="item-description"]')

        if tri_desc_html is not None:
            tri_desc = tri_desc_html.text.lower()
        else:
            tri_desc = None

        if tri_name == trigger_name \
                and (trigger_desc is None or tri_desc == trigger_desc.lower()):
            trigger_id_list.append(index+1)

    return trigger_id_list


def update_trigger_to_commit(conn, plan_id, trigger_name, enable_repos_list, trigger_desc=None,
                             raise_multiple_triggers=False):
    """
    This method is for bamboo v5.7.2
    Batch update the trigger
    :param conn:
    :param plan_id:
    :param enable_repos_list:
                A name list of which repository can be enabled
    :param trigger_name:
                Name of the trigger, ignore case,
                 'repository triggered build', 'stash repository triggered' for example
    :param trigger_desc:
                The trigger description
    :param raise_multiple_triggers:
                True: if the trigger specified is more than one, raise exception for safe
    :return:
    """
    trigger_id_list = get_trigger_id_list(conn, plan_id, trigger_name, trigger_desc)
    if trigger_id_list is None:
        return

    if raise_multiple_triggers and len(trigger_id_list) > 0:
        raise Exception('Multiple triggers!')

    params = {
        "buildKey": plan_id,
        "decorator": "nothing",
        "confirm": "true",
    }

    res_list = []
    for trigger_id in trigger_id_list:
        params.update({
            'triggerId': trigger_id
        })

        trigger_params = OrderedDict()
        trigger_params['buildKey'] = plan_id
        trigger_params['triggerId'] = trigger_id
        trigger_params["confirm"] = "true"
        trigger_params['decorator'] = 'nothing'
        trigger_params['submit'] = 'Yes'

        form = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/editChainTrigger.action',
            params)

        form_inputs = form.findall('.//input')

        options = form.findall('.//select[@name="selectedBuildStrategy"]/option')
        for option in options:
            is_selected = option.attrib.get('selected')
            value = option.attrib.get('value')
            if is_selected == 'selected':
                del option.attrib['selected']

            if value == 'trigger':
                option.attrib['selected'] = 'selected'

        trigger_params['selectedBuildStrategy'] = 'trigger'

        form.cssselect('fieldset[id="fieldArea_repositoryTriggers"]')[0].attrib['style']='display:block'

        repos_value_list = []

        for form_input in form_inputs:
            name = form_input.attrib.get('name')
            i_type = form_input.attrib.get('type')

            if i_type == 'checkbox' and name == 'repositoryTrigger':
                input_id = form_input.attrib.get('id')
                tmp_repos_name = form.find('.//label[@for="'+input_id+'"]').text.strip().replace('\n', '')
                if tmp_repos_name in enable_repos_list:
                    value = form_input.attrib.get('value')
                    repos_value_list.append(value)
                    form_input.attrib['checked'] = 'checked'
                else:
                    if form_input.attrib.get('checked') == 'checked':
                        del form_input.attrib['checked']

            elif i_type == 'checkbox' and name != 'repositoryTrigger':
                is_checked = form_input.attrib.get('checked')
                if is_checked and is_checked == "checked":
                    value = "true"
                else:
                    value = "false"
            else:
                value = form_input.attrib.get('value')

            trigger_params[name] = value

        trigger_params['repositoryTrigger'] = repos_value_list

        res = requests.post_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/updateChainTrigger.action',
            trigger_params
        )

        res_list.append(res)

    return res_list










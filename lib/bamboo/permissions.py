import logging
from .. import requests

import constants
from ..tools.utils import *


def _check_permission(html_root, usertype, username, permission):
    if usertype == 'other':
        usertype = 'role'
    if username == 'Logged in Users':
        username = 'ROLE_USER'
    elif username == 'Anonymous Users':
        username = 'ROLE_ANONYMOUS'
    permission_input_field_name = 'bambooPermission_' + usertype + '_' + username + '_' + permission.upper()  # bambooPermission_user_B19537_READ
    # permission_cell_name = permission_input_field_name+'_cell'
    permission_xpath = './/input[@name="' + permission_input_field_name + '"]'
    logging.debug('xpath to search for permission checkbox = %s' % permission_xpath)
    el = html_root.find(permission_xpath)
    if el == None:
        logging.debug('element not found')
        return False
    logging.debug('element is checked = %s', True if 'checked' in el.attrib else False)
    if 'checked' in el.attrib:
        return True
    else:
        return False


def _get_type_permissions(html_root, usertype):
    table_user = html_root.findall('.//table[@id="configureBuild' + usertype.capitalize() + 'Permissions"]/tr')
    logging.debug('xpath to search for permission table = %s' % table_user)

    user_permissions = {}

    for tr in table_user:
        key = None
        try:
            key = tr.find('td[1]/a').attrib['href'].rsplit('/', 1)[1]
        except:
            key = tr.find('td[1]').text
        read_p = _check_permission(tr, usertype, key, 'READ')
        write_p = _check_permission(tr, usertype, key, 'WRITE')
        build_p = _check_permission(tr, usertype, key, 'BUILD')
        clone_p = _check_permission(tr, usertype, key, 'CLONE')
        admin_p = _check_permission(tr, usertype, key, 'ADMINISTRATION')

        user_permissions[key] = {'read': read_p,
                                 'write': write_p,
                                 'build': build_p,
                                 'clone': clone_p,
                                 'admin': admin_p}

    return user_permissions


def get_plan_permissions(conn, plan_id):
    params = {
        "buildKey": plan_id
    }
    res = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/editChainPermissions.action',
            params)

    root = res  # .getroot()

    user_permissions = _get_type_permissions(root, 'user')
    group_permissions = _get_type_permissions(root, 'group')
    other_permissions = _get_type_permissions(root, 'other')

    return {'user': user_permissions,
            'group': group_permissions,
            'other': other_permissions}


def mod_plan_permissions(conn, plan_id, permission_params):
    params = {
        "bamboo.successReturnMode": "json",
        "buildKey": plan_id,
        "newGroup": None,
        "newUser": None,
        "principalType": "User",
        "save": "Save",
        "selectFields": "principalType",
    }

    params.update(permission_params)
    res = requests.post_ui_return_json(
            conn,
            conn.baseurl + '/chain/admin/config/updateChainPermissions.action',
            params)

    return res


def get_user_granted_perms(conn, plan_id):
    """
    Get the permissions of users of a plan for bamboo v5.7.2+
    :param conn:
    :param plan_id:
    :param u_type
    :return:
    """
    params = {
        "buildKey": plan_id,
    }

    html_root = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/editChainPermissions.action',
            params)

    permisson_html = html_root.find('.//table[@id="configureBuildUserPermissions"]')
    if permisson_html is None:
        logging.error(constants.INCORRECT_PLAN_KEY_ERROR_MSG % plan_id)
        return None, None

    user_tr_html_list = permisson_html.findall('tr')

    plan_perms = {}
    for tr_html in user_tr_html_list:
        td_html_list = tr_html.findall('.//td')
        for index, td_html in enumerate(td_html_list):
            if index == 0:
                user_info = td_html.find('.//a').text
                _, user_id = user_info.split('-')
                user_id = user_id.lower()
                plan_perms[user_id] = {}
            else:
                user_perm_input = td_html.find('.//input')
                user_perm_name = user_perm_input.attrib.get('name')
                user_perm_granted = user_perm_input.attrib.get('checked')
                if user_perm_granted == 'checked':
                    plan_perms[user_id][user_perm_name] = True
                else:
                    plan_perms[user_id][user_perm_name] = False

    logged_user_permisson_html = html_root.find('.//table[@id="configureBuildOtherPermissions"]')
    logged_user_tr_html_list = logged_user_permisson_html.findall('.//tr')

    plan_perms['$logged-in-user'] = {}
    for tr_html in logged_user_tr_html_list:
        td_html_list = tr_html.findall('.//td')
        for index, td_html in enumerate(td_html_list):
            if td_html.attrib.get('class') is not None:
                user_perm_input = td_html.find('.//input')
                user_perm_name = user_perm_input.attrib.get('name')
                user_perm_granted = user_perm_input.attrib.get('checked')
                if user_perm_granted == 'checked':
                    plan_perms['$logged-in-user'][user_perm_name] = True
                else:
                    plan_perms['$logged-in-user'][user_perm_name] = False

    create_user_button_html = html_root.find('.//a[@id="createUserPrincipalButton"]')
    entity_id = __get_entity_id(create_user_button_html)

    return plan_perms, entity_id


def __get_entity_id(create_user_button_html):
    href = create_user_button_html.attrib.get('href')
    kv_list = href.split('&')
    for kv in kv_list:
        if kv.find('entityId') != -1:
            kv_item = kv.split('=')
            entity_id = kv_item[1]
            return entity_id


def create_permission_principal_for_user(conn, plan_id, user_id, entity_id):
    """
    Create a permission of a plan for the user (bamboo v5.7.2+)
    :param conn:
    :param plan_id:
    :param user_id:
    :return:
    """
    params = {
        "principalType": "User",
        "newUser": user_id,
        "newGroup": "",
        "entityId": entity_id,
        "returnUrl": "/chain/admin/config/editChainPermissions.action?&saved=true&buildKey=" + plan_id,
        "bamboo.successReturnMode": "json",
        "decorator": "nothing",
        "confirm": "true"
    }

    res = requests.post_ui_return_json(
            conn,
            conn.baseurl + '/ajax/createPermissionPrincipal.action',
            params
    )

    return res


def grant_user_perms_of_plan(conn, plan_id, user_id_list=None, perm_list=None,
                             logged_in_users_perm_list=None, ):
    plan_perms, entity_id = get_user_granted_perms(conn, plan_id)

    user_id_list = make_none_list(user_id_list)
    perm_list = make_none_list(perm_list)
    logged_in_users_perm_list = make_none_list(logged_in_users_perm_list)

    params = {
        "buildKey": plan_id,
        "save": "Save",
        "atl_token": "",
        "atl_token_source": "js"
    }

    previous_perms = {}
    for plan_perm in plan_perms.itervalues():
        for perm_name, perm_value in plan_perm.iteritems():
            if perm_value is True:
                previous_perms[perm_name] = 'on'

    params.update(previous_perms)

    grant_perms = {}
    perm_set = set(perm_list)
    for user_id in user_id_list:
        user_id = user_id.upper()
        for perm in perm_set:
            if perm == constants.PLAN_PERM_VIEW:
                # If user has perm of View(V)
                grant_name = constants.PLAN_PERM_MAPPING[constants.PLAN_PERM_VIEW] % user_id
            elif perm == constants.PLAN_PERM_EDIT:
                # If user has perm of Edit(E)
                grant_name = constants.PLAN_PERM_MAPPING[constants.PLAN_PERM_EDIT] % user_id
            elif perm == constants.PLAN_PERM_BUILD:
                # If user has perm of Build(B)
                grant_name = constants.PLAN_PERM_MAPPING[constants.PLAN_PERM_BUILD] % user_id
            elif perm == constants.PLAN_PERM_CLONE:
                # If user has perm of Clone(C)
                grant_name = constants.PLAN_PERM_MAPPING[constants.PLAN_PERM_CLONE] % user_id
            elif perm == constants.PLAN_PERM_ADMIN:
                # If user has perm of Admin(A)
                grant_name = constants.PLAN_PERM_MAPPING[constants.PLAN_PERM_ADMIN] % user_id
            else:
                logging.warning('Not allowed permission %s.' % perm)
                continue

            if user_id.lower() not in plan_perms:
                logging.warning('User %s has no permission of the plan. Append it.' % user_id)
            elif grant_name not in params:
                grant_perms[grant_name] = 'on'

    for login_perm in logged_in_users_perm_list:
        if login_perm == constants.PLAN_PERM_VIEW:
            grant_name = constants.PLAN_ROLE_PERM_MAPPING[constants.PLAN_PERM_VIEW]
        elif login_perm == constants.PLAN_PERM_EDIT:
            grant_name = constants.PLAN_ROLE_PERM_MAPPING[constants.PLAN_PERM_EDIT]
        elif login_perm == constants.PLAN_PERM_BUILD:
            grant_name = constants.PLAN_ROLE_PERM_MAPPING[constants.PLAN_PERM_BUILD]
        elif login_perm == constants.PLAN_PERM_CLONE:
            grant_name = constants.PLAN_ROLE_PERM_MAPPING[constants.PLAN_PERM_CLONE]
        elif login_perm == constants.PLAN_PERM_ADMIN:
            grant_name = constants.PLAN_ROLE_PERM_MAPPING[constants.PLAN_PERM_ADMIN]
        else:
            logging.warning('Not allowed permission %s.' % login_perm)
            continue

        if grant_name not in params:
            grant_perms[grant_name] = 'on'

    params.update(grant_perms)

    root_html = requests.post_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/updateChainPermissions.action',
            params
    )

    return root_html


def get_logged_in_user_granted_perms(conn, plan_id):
    params = {
        "buildKey": plan_id,
    }

    html_root = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/editChainPermissions.action',
            params
    )

    permisson_html = html_root.find('.//table[@id="configureBuildOtherPermissions"]')
    if permisson_html is None:
        logging.error(constants.INCORRECT_PLAN_KEY_ERROR_MSG % plan_id)
        return None, None

    tr_html_list = permisson_html.findall('.//tr')

    plan_perms = {}
    plan_perms['logged-in-user'] = {}

    for tr_html in tr_html_list:
        td_html_list = tr_html.findall('.//td')
        for index, td_html in enumerate(td_html_list):
            if td_html.attrib.get('class') is not None:
                user_perm_input = td_html.find('.//input')
                user_perm_name = user_perm_input.attrib.get('name')
                user_perm_granted = user_perm_input.attrib.get('checked')
                if user_perm_granted == 'checked':
                    plan_perms['logged-in-user'][user_perm_name] = True
                else:
                    plan_perms['logged-in-user'][user_perm_name] = False

    create_user_button_html = html_root.find('.//a[@id="createUserPrincipalButton"]')
    entity_id = __get_entity_id(create_user_button_html)

    return plan_perms, entity_id

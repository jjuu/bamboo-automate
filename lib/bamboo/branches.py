import logging

from .. import requests
from types import *


def add_plan_branch(conn, plan_id, branch_name, branch_description=None):
    """ Add a branch to a plan.

    This function only creates the branch.
    It must be configured and enabled afterwards.

    The redirectUrl in the result contains the branch ID.

    """
    assert type(branch_name) is StringType, 'branch_name is not type String: %r' % branch_name
    params = {
        "bamboo.successReturnMode": "json",
        "planKey": plan_id,
        "planKeyToClone": plan_id,
        "branchName": branch_name,
        "branchDescription": branch_description,
        "branchVcsFields": None,
        "checkBoxFields": "tmp.createAsEnabled",
        "confirm": "true",
        "creationOption": "MANUAL",
        "decorator": "nothing"
    }

    res = requests.post_ui_return_json(
            conn,
            conn.baseurl + '/chain/admin/createPlanBranch.action',
            params)

    return res


def enable_plan_branch(conn, branch_id):
    params = {
        "enabled": "false",
        "branchName": "testbranch",
        "branchDescription": "mydesc",
        "branchConfiguration.cleanup.disabled": "true",
        "buildKey": branch_id,
        "checkBoxFields": "enabled",
        "checkBoxFields": "branchConfiguration.cleanup.disabled",
        "planKey": branch_id,
        "returnUrl": "",
        "save": "Save",
    }

    res = requests.post_ui_return_html(
            conn,
            conn.baseurl + '/branch/admin/config/saveChainBranchDetails.action',
            params)

    return res


def mod_plan_branch_details(conn, branch_id, branch_params):
    """ Modify the branch details.

    The parameters must include:
    * branchDescription
    * branchName
    * enabled

    Arguments:
    conn -- the connection
    branch_id -- the unique ID of the branch
    branch_params -- the parameters in a dictionary

    """
    params = {
        "branchConfiguration.cleanup.disabled": "true",
        "buildKey": branch_id,
        "checkBoxFields": "enabled",
        "checkBoxFields": "branchConfiguration.cleanup.disabled",
        "checkBoxFields": "overrideBuildStrategy",
        "checkBoxFields": "repositoryTrigger",
        "checkBoxFields": "custom.triggerrCondition.plansGreen.enabled",
        "planKey": branch_id,
        "returnUrl": "",
        "save": "Save",
        "selectFields": "selectedBuildStrategy",
    }
    params.update(branch_params)

    res = requests.post_ui_return_html(
            conn,
            conn.baseurl + '/branch/admin/config/saveChainBranchDetails.action',
            params)

    return res


def delete_plan_branch(conn, branch_id):
    params = {
        "buildKey": branch_id,
        "save": "confirm"
    }

    res = requests.post_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/deleteChain!doDelete.action',
            params)

    return res


def get_plan_branches(conn, plan_id, sort_by_title=False):
    """ Retrieve information about all branches of this plan.

    TODO: reimplement this to use the rest api.

    """
    params = {
        "buildKey": plan_id
    }
    res = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/editChainDetails.action',
            params)

    root = res  # .getroot()

    branches = {}
    li_branches = root.findall('.//ul[@class="branches"]/li')
    for li in li_branches:
        key = None
        try:
            key = li.find('./a').attrib['id'].rsplit('_', 1)[1]
        except:
            logging.error('no key for branch found.')
        edit_link = li.find('./a').attrib['href']
        title = li.find('./a').text

        if sort_by_title:
            branches[title] = (key, edit_link,)
        else:
            branches[key] = (title, edit_link,)

    return branches


def get_branch_configure_res(conn, plan_id):
    params = {
        'buildKey': plan_id
    }

    res = requests.get_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/configureBranches.action',
            params
    )

    return res


def update_configure_branch(conn, plan_id, enabled=None, matching_pattern=None, clean_up_days=None):
    """
    Update branch configure, for v5.7.2
    """
    res = get_branch_configure_res(conn, plan_id)

    if enabled is None:
        enabled = res.find('.//input[@name="enabled"]').checked

    if matching_pattern is None:
        matching_pattern = res.find('.//input[@name="matchingPattern"]').value

    branches_defaultBranchIntegration_enabled = res.find(
        './/input[@name="branches.defaultBranchIntegration.enabled"]').checked

    branch_updater = res.find(
        './/select[@name="branches.defaultBranchIntegration.branchUpdater.mergeFromBranch"]').value
    if branch_updater is None:
        branch_updater = \
        res.find('.//select[@name="branches.defaultBranchIntegration.branchUpdater.mergeFromBranch"]').value_options[0]

    gate_keeper = res.find('.//select[@name="branches.defaultBranchIntegration.gateKeeper.checkoutBranch"]').value
    if gate_keeper is None:
        gate_keeper = \
        res.find('.//select[@name="branches.defaultBranchIntegration.gateKeeper.checkoutBranch"]').value_options[0]

    strategy_actives = res.findall('.//input[@name="branches.defaultBranchIntegration.strategy"]')
    for strategy_active in strategy_actives:
        strategy_value = strategy_active.attrib.get('value')
        if strategy_value == 'BRANCH_UPDATER':
            branch_updater_push_enabled = res.find(
                './/input[@name="branches.defaultBranchIntegration.branchUpdater.pushEnabled"]').checked
            branch_updater_value = strategy_value
        elif strategy_value == 'GATE_KEEPER':
            gate_keeper_push_enabled = res.find(
                './/input[@name="branches.defaultBranchIntegration.gateKeeper.pushEnabled"]').checked
            gate_keeper_value = strategy_value
        else:
            logging.error('Unknown strategy active')
            return

    remote_jira_branch_linking_enabled = res.find('.//input[@name="remoteJiraBranchLinkingEnabled"]').checked

    which_notification = None
    notifications = res.findall('.//input[@name="defaultNotificationStrategy"]')
    for notification in notifications:
        if notification.checked is True:
            which_notification = notification.value

    if clean_up_days is None:
        clean_up_days = res.find('.//input[@name="timeOfInactivityInDays"]').value
    elif enabled == 'false' or enabled is None:
        logging.warning('Automatically manage branches flag is false, so the remove-after-day will be set to 30. ')

    params = {
        'planKey': plan_id,
        'checkBoxFields': ['enabled',
                           'remoteJiraBranchLinkingEnabled',
                           'branches.defaultBranchIntegration.enabled',
                           'branches.defaultBranchIntegration.branchUpdater.pushEnabled',
                           'branches.defaultBranchIntegration.gateKeeper.pushEnabled'],
        'selectFields': ['branches.defaultBranchIntegration.branchUpdater.mergeFromBranch',
                         'branches.defaultBranchIntegration.branchUpdater.pushEnabled'],
        'matchingPattern': matching_pattern,
        'branches.defaultBranchIntegration.branchUpdater.mergeFromBranch': branch_updater,
        'branches.defaultBranchIntegration.gateKeeper.checkoutBranch': gate_keeper,
        'remoteJiraBranchLinkingEnabled': 'true',
        'defaultNotificationStrategy': which_notification,
        'timeOfInactivityInDays': clean_up_days,
        'save': 'Save',
        'atl_token': '',
        'atl_token_source': 'js'
    }

    if enabled == 'true' or enabled is True:
        params['enabled'] = 'true'

    if branches_defaultBranchIntegration_enabled:
        params['branches.defaultBranchIntegration.enabled'] = 'true'

    if branch_updater_push_enabled:
        params['branches.defaultBranchIntegration.branchUpdater.pushEnabled'] = 'true'
        params['branches.defaultBranchIntegration.strategy'] = branch_updater_value

    if gate_keeper_push_enabled:
        params['branches.defaultBranchIntegration.gateKeeper.pushEnabled'] = 'true'
        params['branches.defaultBranchIntegration.strategy'] = gate_keeper_value

    if remote_jira_branch_linking_enabled:
        params['remoteJiraBranchLinkingEnabled'] = 'true'

    res = requests.post_ui_return_html(
            conn,
            conn.baseurl + '/chain/admin/config/updateBranches.action',
            params
    )

    return res
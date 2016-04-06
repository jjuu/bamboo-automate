from collections import OrderedDict

import json
import logging

from .. import requests


def get_repositories(conn, plan_id):
    params = {
        'buildKey': plan_id
    }

    html_root = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/editChainRepository.action',
        params
    )

    repo_info = OrderedDict()
    repositories_html = html_root.find('.//div[@id="panel-editor-list"]').findall('.//li')

    for repository in repositories_html:
        if repository.attrib.get('class') == 'toolbar-item':
            continue

        repo_item_id = repository.attrib['data-item-id']
        repo_display_name = repository.find('.//h3[@class="item-title"]').text

        repo_info[repo_display_name] = {
            'repo_item_id': repo_item_id
        }

    return repo_info


def get_repo_html(conn, plan_id, repo_id):
    params = {
        'planKey': plan_id,
        'repositoryId': repo_id,
        'decorator': 'nothing',
        'confirm': 'true'
    }

    repo_html = requests.get_ui_return_html(
        conn,
        conn.baseurl + '/chain/admin/config/editRepository.action',
        params
    )

    return repo_html


def get_repo_server_key(repo_html):
    return repo_html.find('.//input[@name="repository.stash.server"]').value


def get_repo_from_server(conn, server_key, repo_slug, start=0):
    params = {
        'start': start,
        'query': repo_slug,
        'limit': 10,
        'serverKey': server_key
    }

    repo_json = requests.get_rest_return_json(
        conn,
        conn.baseurl + '/rest/stash/latest/projects/repositories',
        params
    )

    return repo_json


def get_repo_by_key(conn, server_key, project_key, repo_slug, limit=None):
    start = 0
    while True:
        repos = get_repo_from_server(conn, server_key, repo_slug, start)
        repos_info = repos['values']

        if repos['size'] == 0:
            break

        for repo_info in repos_info:
            if project_key == repo_info['project']['key']:
                return repo_info

        start += 10

        if limit is not None and start > limit:
            break


def get_repo_branches(conn, server_key, repo_key, repo_slug, repo_url, start=0):
    params = {
        'start': start,
        'query': '',
        'limit': 10,
        'serverKey': server_key,
        'projectKey': repo_key,
        'repositorySlug': repo_slug,
        'repositoryUrl': repo_url
    }

    branches = requests.get_rest_return_json(
        conn,
        conn.baseurl + '/rest/stash/latest/projects/repositories/branches',
        params
    )

    return branches


def set_repo_form_params(conn, plan_id, hidden_repo_id, repo_id, stash_repo_id, branch, project_key,
                         repository_slug, repository_url, repo_html, reps_type='stash-rep'):
    repo_type = repo_html.find('.//select[@id="selectedRepository"]').value

    if repo_type.split(':')[1] != reps_type:
        return None

    input_html = repo_html.findall('.//input')
    input_html.extend(repo_html.findall('.//select'))

    form = OrderedDict()

    def get_form_info(name, ftype='input'):
        return repo_html.find('.//%s[@name="%s"]' % (ftype, name)).value

    form['planKey'] = plan_id
    form['repositoryId'] = hidden_repo_id
    form['selectFields'] = ['selectedRepository', 'filter.pattern.option',
                            'selectedWebRepositoryViewer', 'webRepository.hg.scheme']
    form['selectedRepository'] = get_form_info('selectedRepository', 'select')
    form['filter.pattern.option'] = get_form_info('filter.pattern.option', 'select')
    form['selectedWebRepositoryViewer'] = get_form_info('selectedWebRepositoryViewer', 'select')
    form['webRepository.hg.scheme'] = get_form_info('webRepository.hg.scheme', 'select')

    form['filter.pattern.option'] = get_form_info('filter.pattern.option', 'select')
    form['selectedWebRepositoryViewer'] = get_form_info('selectedWebRepositoryViewer', 'select')
    form['webRepository.hg.scheme'] = 'bitbucket'
    form['repositoryName'] = get_form_info('repositoryName')
    form['repository.stash.server'] = get_form_info('repository.stash.server')
    form['repository.stash.repositoryId'] = stash_repo_id
    form['repository.stash.branch'] = branch
    form['repository.stash.projectKey'] = project_key
    form['repository.stash.repositorySlug'] = repository_slug
    form['repository.stash.repositoryUrl'] = repository_url

    form_val = get_form_info('repository.stash.useShallowClones')
    if form_val is not None:
        form['repository.stash.useShallowClones'] = form_val

    form_val = get_form_info('repository.stash.useRemoteAgentCache')
    if form_val is not None:
        form['repository.stash.useRemoteAgentCache'] = form_val

    form_val = get_form_info('repository.stash.useSubmodules')
    if form_val is not None:
        form['repository.stash.useSubmodules'] = form_val

    form_val = get_form_info('repository.stash.verbose.logs')
    if form_val is not None:
        form['repository.stash.verbose.logs'] = form_val

    form_val = get_form_info('repository.stash.fetch.whole.repository')
    if form_val is not None:
        form['repository.stash.fetch.whole.repository'] = form_val

    form_val = get_form_info('repository.common.quietPeriod.enabled')
    if form_val is not None:
        form['repository.common.quietPeriod.enabled'] = form_val

    form['checkBoxFields'] = ['repository.stash.useShallowClones', 'repository.stash.useRemoteAgentCache',
                              'repository.stash.useSubmodules', 'repository.stash.verbose.logs',
                              'repository.stash.fetch.whole.repository', 'repository.common.quietPeriod.enabled']
    form['repository.stash.commandTimeout'] = get_form_info('repository.stash.commandTimeout')
    form['repository.common.quietPeriod.period'] = get_form_info('repository.common.quietPeriod.period')
    form['repository.common.quietPeriod.maxRetries'] = get_form_info('repository.common.quietPeriod.maxRetries')
    form['filter.pattern.regex'] = get_form_info('filter.pattern.regex')
    form['changeset.filter.pattern.regex'] = get_form_info('changeset.filter.pattern.regex')
    form['webRepository.stash.url'] = get_form_info('webRepository.stash.url')
    form['webRepository.stash.project'] = get_form_info('webRepository.stash.project')
    form['webRepository.stash.repositoryName'] = get_form_info('webRepository.stash.repositoryName')
    form['webRepository.fisheyeRepositoryViewer.webRepositoryUrl'] = get_form_info('webRepository.fisheyeRepositoryViewer.webRepositoryUrl')
    form['webRepository.fisheyeRepositoryViewer.webRepositoryRepoName'] = get_form_info('webRepository.fisheyeRepositoryViewer.webRepositoryRepoName')
    form['webRepository.fisheyeRepositoryViewer.webRepositoryPath'] = get_form_info('webRepository.fisheyeRepositoryViewer.webRepositoryPath')
    form['webRepository.genericRepositoryViewer.webRepositoryUrl'] = get_form_info('webRepository.genericRepositoryViewer.webRepositoryUrl')
    form['webRepository.genericRepositoryViewer.webRepositoryUrlRepoName'] = get_form_info('webRepository.genericRepositoryViewer.webRepositoryUrlRepoName')
    form['webRepository.hg.scheme'] = get_form_info('webRepository.hg.scheme', 'select')
    form['bamboo.successReturnMode'] = 'json-as-html'
    form['decorator'] = 'nothing'
    form['confirm'] = 'true'

    return form


def __update_repo_and_branch(conn, forms):

    res = requests.post_ui_return_json(
        conn,
        conn.baseurl + '/chain/admin/config/updateRepository.action',
        forms
    )

    if res['status'] == 'OK':
        logging.info('Success updated.')
    else:
        logging.info('Fail to update due to unknown reason.')


def update_repo_branch(conn, plan_id, project_key, repo_display_name, repo_slug, branch_name):

    repos = get_repositories(conn, plan_id)

    for display_name, repo_info in repos.iteritems():
        if display_name == repo_display_name:
            hidden_repo_id = repo_info['repo_item_id']
            repo_html = get_repo_html(conn, plan_id, hidden_repo_id)

            server_key = get_repo_server_key(repo_html)

            repo_info = get_repo_by_key(conn,server_key, project_key, repo_slug)

            repo_slug = repo_info['slug']
            repo_id = repo_info['id']
            repo_url = repo_info['sshCloneUrl']
            repo_key = repo_info['project']['key']

            forms = set_repo_form_params(conn, plan_id=plan_id, hidden_repo_id=hidden_repo_id, repo_id=repo_id,
                                         stash_repo_id=repo_id, branch=branch_name, project_key=repo_key,
                                         repository_slug=repo_slug, repository_url=repo_url, repo_html=repo_html)

            logging.info('Try to update %s, display_name %s, repository %s, branch %s'
                         % (project_key, display_name, repo_slug, branch_name))
            __update_repo_and_branch(conn, forms)



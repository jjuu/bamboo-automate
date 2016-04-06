

HTTP_METHOD_GET = 'GET'
HTTP_METHOD_POST = 'POST'
HTTP_RESPONSE_STATUS_NOT_OK = {'status':'NotOK'}


# max retry times
MAX_RETRIES = 3

# retry sleep time
RETRY_SLEEP = 5


bamboo_read_perm = "bambooPermission_user_%s_READ"
bamboo_write_perm = "bambooPermission_user_%s_WRITE"
bamboo_build_perm = "bambooPermission_user_%s_BUILD"
bamboo_clone_perm = "bambooPermission_user_%s_CLONE"
bamboo_admin_perm = "bambooPermission_user_%s_ADMINISTRATION"

bamboo_role_read_perm = 'bambooPermission_role_ROLE_USER_READ'
bamboo_role_write_perm = 'bambooPermission_role_ROLE_USER_WRITE'
bamboo_role_build_perm = 'bambooPermission_role_ROLE_USER_BUILD'
bamboo_role_clone_perm = 'bambooPermission_role_ROLE_USER_CLONE'
bamboo_role_admin_perm = 'bambooPermission_role_ROLE_USER_ADMINISTRATION'

# View(V), Edit(E), Build(B), Clone(C), Admin(A)
PLAN_PERM_VIEW = 'v'
PLAN_PERM_EDIT = 'e'
PLAN_PERM_BUILD = 'b'
PLAN_PERM_CLONE = 'c'
PLAN_PERM_ADMIN = 'a'
PERM_TUPLE = (PLAN_PERM_VIEW, PLAN_PERM_EDIT, PLAN_PERM_BUILD, PLAN_PERM_CLONE, PLAN_PERM_ADMIN)

PLAN_PERM_MAPPING = {}
PLAN_PERM_MAPPING[PLAN_PERM_VIEW] = bamboo_read_perm
PLAN_PERM_MAPPING[PLAN_PERM_EDIT] = bamboo_write_perm
PLAN_PERM_MAPPING[PLAN_PERM_BUILD] = bamboo_build_perm
PLAN_PERM_MAPPING[PLAN_PERM_CLONE] = bamboo_clone_perm
PLAN_PERM_MAPPING[PLAN_PERM_ADMIN] = bamboo_admin_perm

PLAN_ROLE_PERM_MAPPING = {}
PLAN_ROLE_PERM_MAPPING[PLAN_PERM_VIEW] = bamboo_role_read_perm
PLAN_ROLE_PERM_MAPPING[PLAN_PERM_EDIT] = bamboo_role_write_perm
PLAN_ROLE_PERM_MAPPING[PLAN_PERM_BUILD] = bamboo_role_build_perm
PLAN_ROLE_PERM_MAPPING[PLAN_PERM_CLONE] = bamboo_role_clone_perm
PLAN_ROLE_PERM_MAPPING[PLAN_PERM_ADMIN] = bamboo_role_admin_perm

# Incorrect plan key error message
INCORRECT_PLAN_KEY_ERROR_MSG = 'Incorrect plan key %s. No this plan or not the plan admin.'

# Bamboo task type
TASK_TYPES = ['script_location']
TASK_VARIABLE_NAMES = ['{job_name}']
KEY_OF_JOB_NAME = 'job_name'

bamboo_host_default = ''      # the bamboo host, for example http://my-bamboo.host.net
bamboo_baseurl = ''

FINISH_MSG = '######## Finish %s .... ########'

requirements = ['exists', 'equals', 'matches']

update_task_mode = ['append', 'modify', 'override']
update_task_mode_append = 'append'
update_task_mode_modify = 'modify'
update_task_mode_override = 'override'

TASK_TITLE_SOURCE_CODE_CHECKOUT = 'Source Code Checkout'
TASK_REPO_DEFAULT_VALUE = 'defaultRepository'

# CT stands for condition type
CT_ALL_BUILDS_COMPLETED = 'all_builds_completed'
CT_CHANGE_OF_BUILD_STATUS = 'change_of_build_status'
CT_FAILED_BUILDS_AND_FIRST_SUCCESSFUL = 'failed_builds_and_first_successful'
CT_AFTER_X_BUILD_FAILURES = 'after_x_build_failures'
CT_COMMENT_ADDED = 'comment_added'
CT_CHANGE_OF_RESPONSIBILITIES = 'change_of_responsibilities'
CT_ALL_JOBS_COMPLETED = 'all_jobs_completed'
CT_CHANGE_OF_JOB_STATUS = 'change_of_job_status'
CT_FAILED_JOBS_AND_FIRST_SUCCESSFUL = 'failed_jobs_and_first_successful'
CT_FIRST_FAILED_JOB_FOR_PLAN = 'first_failed_job_for_plan'
CT_JOB_ERROR = 'job_error'
CT_JOB_HUNG = 'job_hung'
CT_JOB_QUEUE_TIMEOUT = 'job_queue_timeout'
CT_JOB_QUEUED_WITHOUT_CAPABLE_AGENTS = 'job_queued_without_capable_agents'

conditions = {
    CT_ALL_BUILDS_COMPLETED: 'chainCompleted.allBuilds',
    CT_CHANGE_OF_BUILD_STATUS: 'chainCompleted.changedChainStatus',
    CT_FAILED_BUILDS_AND_FIRST_SUCCESSFUL: 'chainCompleted.failedChains',
    CT_AFTER_X_BUILD_FAILURES: 'chainCompleted.XFailedChains',
    CT_COMMENT_ADDED: 'buildCommented',
    CT_CHANGE_OF_RESPONSIBILITIES: 'responsibilityChanged',
    CT_ALL_JOBS_COMPLETED: 'buildCompleted.allBuilds',
    CT_CHANGE_OF_JOB_STATUS: 'buildCompleted.changedBuildStatus',
    CT_FAILED_JOBS_AND_FIRST_SUCCESSFUL: 'buildCompleted.firstJobFailed',
    CT_FIRST_FAILED_JOB_FOR_PLAN: 'buildCompleted.firstJobFailed',
    CT_JOB_ERROR: 'buildError',
    CT_JOB_HUNG: 'buildHung',
    CT_JOB_QUEUE_TIMEOUT: 'buildQueueTimeout',
    CT_JOB_QUEUED_WITHOUT_CAPABLE_AGENTS: 'buildMissingCapableAgent'
}


RECIPIENT_USER = 'recipient.user'
RECIPIENT_WATCHERS = 'recipient.watcher'
RECIPIENT_COMMITTER = 'recipient.committer'
RECIPIENT_RESPONSIBLE = 'recipient.responsible'

recipients = [RECIPIENT_USER, RECIPIENT_WATCHERS, RECIPIENT_COMMITTER, RECIPIENT_RESPONSIBLE]

AGENT_SLICE_MARK = '|'

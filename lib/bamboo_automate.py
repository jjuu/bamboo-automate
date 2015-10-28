from lib.high_level_functions import *
from lib.bamboo.authenticate import *
from lib.bamboo.variables import *


createTaskKey = ["com.atlassian.bamboo.plugins.ant:task.builder.ant",
                 "com.atlassian.bamboo.plugins.bamboo-artifact-downloader-plugin:artifactdownloadertask",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.bower",
                 "com.atlassian.bamboo.plugins.scripttask:task.builder.command",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:deployAppTask",
                 "com.atlassian.bamboo.plugins.bamboo-variable-inject-plugin:dump",
                 "net.gejza.bamboo.plugins.bamboo-gnutools-tasks:task.gnutools.make",
                 "com.atlassian.bamboo.plugins.bamboo-grails-plugin:grailsBuilderTaskType",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.grunt",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.gulp",
                 "com.heroku.bamboo.heroku-bamboo-plugin:com.heroku.bamboo.WarDeploymentTask",
                 "com.atlassian.bamboo.plugins.bamboo-variable-inject-plugin:inject",
                 "com.atlassian.bamboo.plugins.testresultparser:task.testresultparser.junit",
                 "com.atlassian.bamboo.plugins.maven:task.builder.maven",
                 "com.atlassian.bamboo.plugins.maven:task.builder.mvn2",
                 "com.atlassian.bamboo.plugins.maven:task.builder.mvn3",
                 "com.atlassian.bamboo.plugins.maven:task.mvn.dependencies.processor",
                 "com.atlassian.bamboo.plugin.dotnet:mbunit",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.reporter.mocha",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.mocha",
                 "com.atlassian.bamboo.plugin.dotnet:msbuild",
                 "com.atlassian.bamboo.plugin.dotnet:mstest",
                 "com.atlassian.bamboo.plugin.dotnet:mstestRunner",
                 "com.atlassian.bamboo.plugin.dotnet:nant",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.node",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.nodeunit",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.npm",
                 "com.atlassian.bamboo.plugin.dotnet:nunit",
                 "com.atlassian.bamboo.plugin.dotnet:nunitRunner",
                 "com.atlassian.bamboo.plugins.php:task.builder.phpunit",
                 "com.atlassian.bamboo.plugins.php:task.builder.phpunit33X",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:reloadAppTask",
                 "com.atlassian.bamboo.plugins.bamboo-scp-plugin:scptask",
                 "com.atlassian.bamboo.plugins.scripttask:task.builder.script",
                 "com.atlassian.bamboo.plugins.vcs:task.vcs.checkout",
                 "com.atlassian.bamboo.plugins.bamboo-scp-plugin:sshtask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:startAppTask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:stopAppTask",
                 "com.atlassian.bamboo.plugins.testresultparser:task.testresultparser.testng",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:undeployAppTask",
                 "com.atlassian.bamboo.plugins.vcs:task.vcs.branching",
                 "com.atlassian.bamboo.plugins.vcs:task.vcs.tagging",
                 "com.atlassian.bamboo.plugin.dotnet:devenv",
                 "com.atlassian.bamboo.plugins.ant:task.builder.ant",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.bower",
                 "com.atlassian.bamboo.plugins.scripttask:task.builder.command",
                 "com.atlassian.bamboo.plugins.bamboo-grails-plugin:grailsBuilderTaskType",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.grunt",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.gulp",
                 "com.atlassian.bamboo.plugins.maven:task.builder.maven",
                 "com.atlassian.bamboo.plugins.maven:task.builder.mvn2",
                 "com.atlassian.bamboo.plugins.maven:task.builder.mvn3",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.mocha",
                 "com.atlassian.bamboo.plugin.dotnet:msbuild",
                 "com.atlassian.bamboo.plugin.dotnet:nant",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.node",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.nodeunit",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.npm",
                 "com.atlassian.bamboo.plugins.scripttask:task.builder.script",
                 "com.atlassian.bamboo.plugin.dotnet:devenv",
                 "com.atlassian.bamboo.plugins.testresultparser:task.testresultparser.junit",
                 "com.atlassian.bamboo.plugin.dotnet:mbunit",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.reporter.mocha",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.mocha",
                 "com.atlassian.bamboo.plugin.dotnet:mstest",
                 "com.atlassian.bamboo.plugin.dotnet:mstestRunner",
                 "com.atlassian.bamboo.plugins.bamboo-nodejs-plugin:task.builder.nodeunit",
                 "com.atlassian.bamboo.plugin.dotnet:nunit",
                 "com.atlassian.bamboo.plugin.dotnet:nunitRunner",
                 "com.atlassian.bamboo.plugins.php:task.builder.phpunit",
                 "com.atlassian.bamboo.plugins.php:task.builder.phpunit33X",
                 "com.atlassian.bamboo.plugins.testresultparser:task.testresultparser.testng",
                 "com.atlassian.bamboo.plugins.bamboo-artifact-downloader-plugin:artifactdownloadertask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:deployAppTask",
                 "com.heroku.bamboo.heroku-bamboo-plugin:com.heroku.bamboo.WarDeploymentTask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:reloadAppTask",
                 "com.atlassian.bamboo.plugins.bamboo-scp-plugin:scptask",
                 "com.atlassian.bamboo.plugins.bamboo-scp-plugin:sshtask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:startAppTask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:stopAppTask",
                 "com.atlassian.bamboo.plugins.tomcat.bamboo-tomcat-plugin:undeployAppTask",
                 "com.atlassian.bamboo.plugins.vcs:task.vcs.checkout",
                 "com.atlassian.bamboo.plugins.vcs:task.vcs.branching",
                 "com.atlassian.bamboo.plugins.vcs:task.vcs.tagging",
                 "com.atlassian.bamboo.plugins.bamboo-variable-inject-plugin:dump",
                 "com.atlassian.bamboo.plugins.bamboo-variable-inject-plugin:inject"
]

logging.basicConfig(level=logging.DEBUG)
host='http://localhost:6990'
user_name='admin'
user_pwd='admin'
conn = authenticate(host, user_name, user_pwd)

###enable/disable plans and jobs
plan_id = 'SWRD-CM'
disable_plan(conn, plan_id)
enable_plan(conn, plan_id)

job_id = 'SWRD-CM-JOB2'
disable_job(conn, job_id)
enable_job(conn, job_id)

##add a new job to each plan
plan_id = 'SWRD-CM'
job_name = 'job6'
job_description = 'job6_description'
res = add_one_job(conn, plan_id, job_name, job_description)


####Modify environment variables for each job
job_id = 'SWRD-CM-JOB4'
task_id = 2
environment_variables = "JAVA_OPTS=\"-Xmx256m -Xms128m\""
res = update_environment_variables(conn, job_id, task_id, environment_variables)



####### Add a repository to each job
job_id = 'SWRD-CM-JOB01'
task_id = 1
repository_id = "2343563"
checkout_dir = "community/poky12"
res = add_repository(conn, job_id, task_id, repository_id, checkout_dir)



# modify permissions on each job
plan_id = 'SWRD-CM'
#usertype, username, permissiontype, value
change_plan_permission(conn, plan_id, ('user', 'username', 'clone', False))


#Add a task about "script" type
job_id = "DNSWRD-CIM-JOB5"
task_description = "1234"
is_task_disabled = False
script_location = "INLINE"
script = "pwd"
argument = ""
environment_variables = ""
working_sub_directory = ""
add_job_task_script(conn, job_id, is_task_disabled,task_description, script_location, script, argument, environment_variables,
                    working_sub_directory)
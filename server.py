import pprint
from wsgiref import simple_server
import json
import falcon
from github import Github
import os
import config

g = Github(os.environ.get('GITHUB_TOKEN'))


class EchoResource(object):
    def on_get(self, req, res):
        pprint.pprint(req)

    def on_post(self, req, res):
        payload = json.loads(req.params['payload'])
        pprint.pprint(payload)


class GithubEventHandler(object):
    def on_get(self, req, res):
        pprint.pprint(req.params)

        status = req.params['status']
        repo_name = req.params['repo']
        gitsha = req.params['gitsha']

        repo = g.get_repo(repo_name)
        if status == 'success':
            repo.get_commit(sha=gitsha).create_status(
                state="success",
                target_url="https://jenkins.core.cvent.org/view/SocialTables/job/st-cdk-deploy",
                description="Jenkins job is successful",
                context="cvent/jenkins"
            )
        elif status == 'error':
            repo.get_commit(sha=gitsha).create_status(
                state="error",
                target_url="https://jenkins.core.cvent.org/view/SocialTables/job/st-cdk-deploy",
                description="Jenkins job has failed",
                context="cvent/jenkins"
            )

    def on_post(self, req, res):
        action = req.media['action']
        # pprint.pprint(req.media)
        if action == 'opened':
            self.process_pull_request(req.media['pull_request'])

    def process_pull_request(self, pr: dict):
        print(f'Title: {pr["title"]}')

        repo = g.get_repo(pr['base']['repo']['full_name'])
        repo.get_commit(sha=pr['head']['sha']).create_status(
            state="pending",
            target_url="https://jenkins.core.cvent.org/view/SocialTables/job/st-cdk-deploy",
            description="Jenkins server is running",
            context="cvent/jenkins"
        )


app = falcon.API()

echo = EchoResource()
gevents = GithubEventHandler()

app.add_route('/', echo)
app.add_route('/event_handler', gevents)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', config.PORT, app)
    print(f'Ready to receive requests on {config.PORT}')
    httpd.serve_forever()

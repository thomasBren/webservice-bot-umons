import os
from flask import Flask, request
from github import Github, GithubIntegration

app = Flask(__name__)

app_id = '311888'

# Read the bot certificate
with open(
        os.path.normpath(os.path.expanduser('bot_key.pem')),
        'r'
) as cert_file:
    app_key = cert_file.read()
    
# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)

def issue_opened_event(repo, payload):
    issue = repo.get_issue(number=payload['issue']['number'])
    author = issue.user.login

    
    response = f"Thanks for opening this issue, @{author}! " \
                f"The repository maintainers will look into it ASAP! :speech_balloon:"
    issue.create_comment(f"{response}")
    issue.add_to_labels('pending')

def pull_request_event(repo, payload):

    pull_request = repo.get_pull(number=payload['pull_request''number'])
    if pull_request.is_merged():
        pull_request.create_issue_comment(f"Thanks pull request successfully merged")



@app.route("/", methods=['POST'])
def bot():
    payload = request.json

    if not 'repository' in payload.keys():
        return "", 204

    owner = payload['repository']['owner']['login']
    repo_name = payload['repository']['name']

    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )
    repo = git_connection.get_repo(f"{owner}/{repo_name}")

    # Check if the event is a GitHub issue creation event
    if all(k in payload.keys() for k in ['action', 'issue']) and payload['action'] == 'opened':
        issue_opened_event(repo, payload)
    if all(k in payload.keys() for k in ['action', 'pull_request']) and payload['action'] == 'closed':
        pull_request_event(repo, payload)

    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)

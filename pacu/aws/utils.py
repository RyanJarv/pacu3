import json
from urllib.parse import urlencode
from urllib.request import urlopen

import boto3
import typer

app = typer.Typer()


def whoami():
    sess = boto3.Session()
    sts = sess.client('sts')
    resp = sts.get_caller_identity()
    print(f"Arn: {resp['Arn']}")
    print(f"UserID: {resp['UserId']}")
    print(f"Account: {resp['Account']}")


def login(
        stdout: bool = typer.Option(False, help="Print the URL to StdOut instead of opening a browser."),
        duration: int = typer.Option(12, help="Session duration in hours.")
):
    """ Login to the web console.

    Login to the web console using the default browser. If a browser can not be launched or if -s is passed then the
    URL will be printed to StdOut instead.
    """
    sess = boto3.Session()
    sts = sess.client('sts')

    login_name = 'pacu-session'

    params = {
        'Action': 'getSigninToken',
    }

    creds = sess.get_credentials()

    #  arn:aws:iam::336983520827:user/me@aws.ryanjarv.sh
    t = sts.get_caller_identity()['Arn'].split(':')[5].split('/')[0]

    # We can't continue if:
    #   If the resource type is not a user or a role,
    #   or if the type is a user but we are using temporary credentials.
    if t not in ['user', 'role'] or (t == 'user' and creds.token):
        print("[ERROR] The GetFederatedToken API can only be called with the long term credentials of an IAM user.")
        return
    else:
        res = sts.get_federation_token(  # type: ignore[attr-defined]
            Name=login_name,
            DurationSeconds=duration * 60 * 60,
            Policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": "*"
                    }
                ]
            })
        )

    params['Session'] = json.dumps({
        'sessionId': res['Credentials']['AccessKeyId'],
        'sessionKey': res['Credentials']['SecretAccessKey'],
        'sessionToken': res['Credentials']['SessionToken'],
    }, default=str)

    resp = urlopen(url='https://signin.aws.amazon.com/federation?' + urlencode(params))
    signin_token = json.loads(resp.read())['SigninToken']
    params = {
        'Action': 'login',
        'Issuer': login_name,
        'Destination': 'https://console.aws.amazon.com/console/home',
        'SigninToken': signin_token
    }

    url = 'https://signin.aws.amazon.com/federation?' + urlencode(params)

    if stdout:
        print('Paste the following URL into a web browser to login as session {}...\n'.format(url))
    else:
        ret = typer.launch(url)
        if ret == 0:
            print('Successfully Launched a new session in the browser')
        else:
            print('Failed to launch the default browser. Try pasting the following URL into a web browser to login '
                  'as session {}...\n'.format(url))

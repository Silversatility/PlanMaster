import json
import argparse
import csv

from pprint import pprint

import requests

SIGNUP_PATH = "/api/v1/signup/?token={token}"
VALIDATE_PATH = "/api/v1/signup-validate/?token={token}"


def parse_args():
    parser = argparse.ArgumentParser(description='Sign up CrewBoss users from a CSV')
    parser.add_argument('--url', help='Base URL to the server to send the signup to')
    parser.add_argument('--token', help='Private API token to authorize the signup')
    parser.add_argument('csv_file', help='CSV file with users')

    args = parser.parse_args()
    return args


def send_request(url, path, data, token):
    try:
        request_url = f"{url}{path}"
        request_url = request_url.format(token=token)
        print(request_url)
        response = requests.post(
            url=request_url,
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps(data)
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
        return json.loads(response.content)
    except json.decoder.JSONDecodeError:
        pass
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def read_csv_file(path):
    users = []
    with open(path, 'r') as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            users.append(row)
    return users


def main():
    args = parse_args()
    users = read_csv_file(args.csv_file)

    print(users)

    for user in users:
        pprint(user)
        result = send_request(args.url, VALIDATE_PATH, user, args.token)
        print(result)
        if result.get('valid', False):
            result = send_request(args.url, SIGNUP_PATH, user, args.token)
        else:
            print(result)

    pprint(args)


if __name__ == "__main__":
    main()

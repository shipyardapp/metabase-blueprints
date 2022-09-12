import requests
import sys
import shipyard_utils as shipyard

EXIT_CODE_INVALID_CREDENTIALS = 200


def get_session_headers(metabase_url, username, password):
    response = requests.post(f'http://{metabase_url}/api/session',
                         json={'username': username,
                               'password': password})
    if response.status_code == requests.codes.ok:
        session_id = response.json()['id']
        headers = {'X-Metabase-Session': session_id}
        return headers
    else:
        print("Error getting credentials, check if username or password are correct")
        sys.exit(EXIT_CODE_INVALID_CREDENTIALS)




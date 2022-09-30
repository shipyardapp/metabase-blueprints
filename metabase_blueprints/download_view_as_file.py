import requests
import sys
import os
import shipyard_utils as shipyard
import argparse

EXIT_CODE_INVALID_CREDENTIALS = 200
EXIT_CODE_INVALID_REPORT_ID = 201
EXIT_CODE_UNKNOWN_ERROR = 202


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--metabase-url', dest='metabase_url', required=True)
    parser.add_argument('--username', dest='username', required=True)
    parser.add_argument('--password', dest='password', required=True)
    parser.add_argument('--dashboard-id', dest='dashboard_id', required=True)
    parser.add_argument('--dashcard-id', dest='dashcard_id', required=True)
    parser.add_argument('--card-id', dest='card_id', required=True)
    parser.add_argument('--dest-file-name',
                        dest='dest_file_name',
                        required=True)
    parser.add_argument('--dest-folder-name',
                        dest='dest_folder_name',
                        default='',
                        required=False)
    parser.add_argument('--file-type',
                        dest='file_type',
                        choices=['json', 'xlsx', 'csv'],
                        type=str.lower,
                        required=True)
    args = parser.parse_args()
    return args


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



def download_query_results(metabase_url, dashboard_id, dashcard_id, card_id,
                       file_format, headers):
    """Download query as file
    https://www.metabase.com/docs/latest/api/dashboard#post-apidashboarddashboard-iddashcarddashcard-idcardcard-idqueryexport-format
    """
    metabase_api_base = f"http://{metabase_url}/api/"
    download_api = metabase_api_base + f"dashboard/{dashboard_id}/dashcard/{dashcard_id}/card/{card_id}/query/{file_format}"
    report_request = requests.post(download_api, headers=headers)

    status_code = report_request.status_code

    if status_code == 200:
        return report_request

    elif status_code == 401:  # Invalid credentials
        print("Metabase API returned an Unauthorized response,",
              "check if credentials are correct and try again")
        sys.exit(EXIT_CODE_INVALID_CREDENTIALS)

    elif status_code == 404:  # Invalid run
        print("Mode report: report id or run id not found")
        sys.exit(EXIT_CODE_INVALID_REPORT_ID)

    else:  # some other error
        print(f"Mode run report returned an unknown status {status_code}/n",
              f"returned data: {report_request.text}")
        sys.exit(EXIT_CODE_UNKNOWN_ERROR)



def main():
    args = get_args()
    metabase_url = args.metabase_url
    username = args.username
    password = args.password
    dashboard_id = args.dashboard_id
    dashcard_id = args.dashcard_id
    card_id = args.card_id
    dest_file_name = args.dest_file_name
    file_format = args.file_type
    if args.dest_folder_name:
        dest_folder_name = args.dest_folder_name
    else:
        dest_folder_name = os.getcwd()

    shipyard.files.create_folder_if_dne(dest_folder_name)
    destination_file_path = shipyard.files.combine_folder_and_file_name(
        dest_folder_name, dest_file_name)  

    # create session headers
    headers = get_session_headers(
                    metabase_url, 
                    username, 
                    password)

    print(f'Downloading the contents of the query results as {file_format}')
    query_results = download_query_results(metabase_url, dashboard_id, dashcard_id, card_id,
                       file_format, headers)
    
    with open(destination_file_path, 'wb+') as f:
        f.write(query_results.content)
    print(
        f'The contents of card {card_id} were successfully written to {destination_file_path}')


if __name__ == "__main__":
    main()
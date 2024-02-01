from flask import Flask, request, jsonify
import requests
import logging
import os

app = Flask(__name__)
sandbox_project_id = os.environ['DREMIO_SANDBOX_PROJECT_ID']
prod_project_id = os.environ['DREMIO_PROD_PROJECT_ID']
sandbox_key = os.environ['DREMIO_SANDBOX_KEY']
prod_key = os.environ['DREMIO_PROD_KEY']

def get_dataset_desc(dataset_path):
    response = requests.get(
        f"https://api.dremio.cloud/v0/projects/{sandbox_project_id}/catalog/by-path/{dataset_path}",
        headers={"Authorization": f"Bearer {sandbox_key}"},
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get metadata for dataset: {response.content}")
        return None

def get_dataset_metadata(dataset_path, all_datasets, env):
    projectId = sandbox_project_id
    key = sandbox_key
    if env == 'PROD':
        projectId = prod_project_id
        key = prod_key
    response = requests.get(
        f"https://api.dremio.cloud/v0/projects/{projectId}/catalog/by-path/{dataset_path}",
        headers={"Authorization": f"Bearer {key}"},
    )
    if response.status_code == 200:
        datasets = response.json().get("children", [])
        for dataset in datasets:
            sPath = '/'.join(dataset["path"])
            if dataset["type"] == "CONTAINER":
                if dataset["containerType"] == "FOLDER":
                    get_dataset_metadata(sPath, all_datasets, env)
            elif dataset["type"] == "DATASET":
                all_datasets.append(sPath)
    else:
        print(f"Failed to get metadata for dataset: {response.content}")


@app.after_request
def after_request(response):
    # Only add CORS headers if the Origin header exists and is from localhost
    origin = request.headers.get('Origin')
    if origin and 'localhost' in origin:
        # Add CORS headers to the response
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/listalldatasets', methods=['GET'])
def ListAllDatasets():
    logging.info('ListAllDatasets function processed a request.')
    env = request.args.get('env')
    all_datasets = []
    get_dataset_metadata("demo-catalog-01", all_datasets, env)
    return jsonify(all_datasets)

@app.route('/showdatasetdesc', methods=['GET'])
def ShowDatasetDesc():
    logging.info('ShowDatasetDesc function processed a request.')
    name = request.args.get('name')

    if name:
        result = get_dataset_desc(name)
        if result is not None:
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to retrieve dataset description"}), 500
    else:
        return jsonify({"message": "No name parameter provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)

    

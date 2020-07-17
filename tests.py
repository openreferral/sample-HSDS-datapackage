# for f in all_resources/*.csv simple/*.csv; do

"""
git clone 'https://github.com/openreferral/sample-data'
git clone 'https://github.com/openreferral/hsds-validator.git'
git clone 'https://github.com/openreferral/specification.git'

cd specificiation
git checkout dev
cp datapackage.json ../hsds-validator/src/datapackage.json

cd ../hsds-validator
docker build --tag 'openreferral/validator:dev-schema' .

docker rm -f openreferral-validator; docker run -d --network=host -e HOST=0.0.0.0 -e PORT=8004 --name=openreferral-validator openreferral/validator:latest
docker rm -f openreferral-validator-dev-schema; docker run -d --network=host -e HOST=0.0.0.0 -e PORT=8005 --name=openreferral-validator-dev-schema openreferral/validator:dev-schema

cd ../sample-data
python3 -m venv .ve
source .ve/bin/activate
pip install -r requirements.txt
py.test tests.py


"""

import json
import pytest
import os
import requests

CURRENT_SCHEMA_PORT = 8004
DEV_SCHEMA_PORT = 8005
PORTS = [CURRENT_SCHEMA_PORT, DEV_SCHEMA_PORT]


def validate_file(name, path, port):
    files = {"file": open(path, "r")}
    r = requests.post(
        "http://localhost:{}/validate/csv".format(port),
        data={"type": name},
        files=files,
    )
    return r.json()["valid"]


@pytest.mark.parametrize('dirname, current_fails, dev_fails', [
    ("all_resources", [], []),
    ("simple", [], []),
    ("simple_non_unique", ['location', 'phone'], ['location', 'phone']),
    ("all_resources_non_enum", ["eligibility"], []),
])
def test_datapackage_dir(dirname, current_fails, dev_fails):
    with open(os.path.join(dirname, "datapackage.json")) as fp:
        datapackage = json.load(fp)
        for resource in datapackage["resources"]:
            for port in PORTS:
                if resource["name"] in current_fails and port == CURRENT_SCHEMA_PORT:
                    expected = False
                elif resource["name"] in dev_fails and port == DEV_SCHEMA_PORT:
                    expected = False
                else:
                    expected = True
                assert (
                    validate_file(
                        name=resource["name"],
                        path=os.path.join(dirname, resource["path"]),
                        port=port,
                    )
                    == expected
                )

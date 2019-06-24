import json
import os
import requests
import requests.exceptions
import sys

from voluptuous import Schema, Invalid


# minimal schema definitions to recognize formats
SCHEMA_MESHVIEWER = Schema({
    'timestamp': str,
    'nodes': [dict],
    'links': [dict]
})

SCHEMA_NODESJSONV1 = Schema({
    'timestamp': str,
    'version': 1,
    'nodes': dict
})

SCHEMA_NODESJSONV2 = Schema({
    'timestamp': str,
    'version': 2,
    'nodes': [dict]
})


def validate_macaddr(candidate):
    blocks = candidate.split(':')

    if len(blocks) != 6:
        raise Invalid

    try:
        int(''.join(blocks), 16)
    except ValueError:
        raise Invalid

    return candidate


SCHEMA_ALFRED = Schema({
    validate_macaddr: dict
})

SCHEMA_FRANKEN_EXTENDED_ROUTERLIST = Schema({
    'version': "1.1.0",
    'nodes': [dict]
})


FORMATS = {}
def register_hook(name, schema, parser):
    FORMATS[name] = {
        'schema': schema,
        'parser': parser
    }


def get_data_path(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', path)


def error(message):
    print(message, file=sys.stderr)


def load_devices_json(path='devices.json'):
    with open(path, 'r') as file:
        devices = file.read()
        return json.loads(devices)


def parse_meshviewer(data, domains_to_exclude=None):
    return list(filter(
        lambda n:
        "domain" not in n or n["domain"] not in domains_to_exclude,
        data['nodes']
    ))


def parse_nodes_json_v1(data, *kwargs):
    out = []
    for k, n in data['nodes'].items():
        model = n.get("nodeinfo", {}).get("hardware", {}).get("model", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


def parse_nodes_json_v2(data, *kwargs):
    out = []
    for n in data['nodes']:
        if type(n) is str:
            continue
        model = n.get("nodeinfo", {}).get("hardware", {}).get("model", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


def parse_alfred(data, *kwargs):
    out = []
    for key in data:
        n = data[key]
        model = n.get("hardware", {}).get("model", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


def parse_franken_extended_routerlist(data, *kwargs):
    out = []
    for node in data["nodes"]:
        model = node.get("hardware", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


register_hook('meshviewer', SCHEMA_MESHVIEWER, parse_meshviewer)
register_hook('nodes.json v1', SCHEMA_NODESJSONV1, parse_nodes_json_v1)
register_hook('nodes.json v2', SCHEMA_NODESJSONV2, parse_nodes_json_v2)
register_hook('alfred', SCHEMA_ALFRED, parse_alfred)
register_hook('franken extended routerlist', SCHEMA_FRANKEN_EXTENDED_ROUTERLIST, parse_franken_extended_routerlist)


def download(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as ex:
        error(f"Exception caught while fetching {url}\n{ex}")
        return None

    if response.status_code != 200:
        error(f"Unexpected status code {response.status_code} while fetching {url}")
        return None

    return response


def load(url, ignore_domains=None):
    if not ignore_domains:
        ignore_domains = list()

    response = download(url)
    if not response:
        return None

    data = response.json()

    for name, format in FORMATS.items():
        try:
            format['schema'](data)
            return format['parser'](data, ignore_domains)
        except Invalid as ex:
            pass

    return None


def get_device_information(model_information, device):
    for dev in model_information:
        if dev["name"] in device:
            return dev["price"], dev["legacy"]
    return None, None


def gather_information(model_information, nodes):
    model_data = {}

    for node in nodes:
        if "model" not in node:
            # Gateway
            continue
        if node["model"] not in model_data:
            model_data[node["model"]] = {"count": 0, "total": -1}
        model_data[node["model"]]["count"] += 1

    # Calculate loss
    for model in model_data.keys():
        price, is_legacy = get_device_information(model_information, model)

        if not is_legacy:
            continue

        if price is None:
            continue

        model_data[model]["total"] = model_data[model]["count"] * price

    output_list = [{"model": model,
                    "count": model_data[model]["count"],
                    "total": model_data[model]["total"]} for model in model_data.keys()]

    return sorted(output_list, key=lambda k: k['total'], reverse=True)

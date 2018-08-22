import json
import os
import requests
import sys

_ROOT = os.path.abspath(os.path.dirname(__file__))
_timeout = 1


def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)


def error(message):
    print(message, file=sys.stderr)


def load_devices_json(path='devices.json'):
    with open(path, 'r') as file:
        devices = file.read()
        return json.loads(devices)


def load_meshviewer_json(url):
    try:
        res = requests.get(url, timeout=_timeout)
    except:
        error("error while fetching " + url)
        return []

    if res.status_code is not 200:
        error("status_code (load_meshviewer_json) " + str(res.status_code))
        return []

    data = res.json()

    if 'updated_at' not in data and 'timestamp' not in data:
        error("no updated_at")
        # this is not a valid nodelist.json file
        return []

    return data['nodes']


def load_nodes_json_v1(data):
    out = []
    for k, n in data['nodes'].items():
        error(n.get("nodeinfo", {}).get("hardware", None))
        model = n.get("nodeinfo", {}).get("hardware", {}).get("model", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


def load_nodes_json_v2(data):
    out = []
    for n in data['nodes']:
        if type(n) is str:
            continue
        error(n.get("nodeinfo", {}).get("hardware", None))
        model = n.get("nodeinfo", {}).get("hardware", {}).get("model", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


def load_nodes_json(url):
    try:
        res = requests.get(url, timeout=_timeout)
    except:
        error("error while fetching " + url)
        return []

    if res.status_code is not 200:
        error("status_code (load_nodes_json) " + str(res.status_code))
        return []

    data = res.json()

    if 'timestamp' not in data or 'version' not in data:
        # this is not a valid nodes.json file
        return []

    if data['version'] is 1:
        return load_nodes_json_v1(data)
    elif data['version'] is 2:
        return load_nodes_json_v2(data)


def load_alfred_json(url):
    try:
        res = requests.get(url, timeout=_timeout)
    except:
        error("error while fetching " + url)
        return []

    if res.status_code is not 200:
        error("status_code (load_nodes_json) " + str(res.status_code))
        return []

    data = res.json()

    if 'timestamp' in data or 'version' in data:
        # this is not a valid alfred.json file
        return []

    out = []
    for key in data:
        n = data[key]
        error(n.get("hardware", None))
        model = n.get("hardware", {}).get("model", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


def load_franken(url):
    try:
        res = requests.get(url, timeout=_timeout)
    except:
        error("error while fetching " + url)
        return []

    if res.status_code is not 200:
        error("status_code (load_nodes_json) " + str(res.status_code))
        return []

    data = res.json()

    out = []
    for node in data["nodes"]:
        model = node.get("hardware", None)
        if model is None:
            continue
        out.append({"model": model})

    return out


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

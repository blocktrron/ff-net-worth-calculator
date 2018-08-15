import json
import os
import requests
import sys

_ROOT = os.path.abspath(os.path.dirname(__file__))
_timeout = 0.1


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

    if 'timestamp' not in data:
        # this is not a valid nodes.json file
        return []

    if data['version'] != 2:
        # v1 not supported
        return []

    out = []
    for n in data['nodes']:
        error(n.get("nodeinfo", {}).get("hardware", None))
        model = n.get("nodeinfo", {}).get("hardware", {}).get("model", None)
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

import argparse
import json
import os

import requests


def load_devices_json(path='devices.json'):
    with open(path, 'r') as file:
        devices = file.read()
        return json.loads(devices)


def load_meshviewer_json(url):
    res = requests.get(url)

    if res.status_code is not 200:
        return None

    return res.json()['nodes']


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


def print_information(community_information):
    total_loss = 0

    for model in community_information:
        if model["total"] == -1:
            continue

        total_loss += model["total"]

        print("{model} - Device count: {count} - Loss: {total_loss}€".format(model=model["model"],
                                                                                  count=model["count"],
                                                                                  total_loss=model["total"]))

    print("Total loss:  {loss}€".format(loss=total_loss))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate net-worth of a Freifunk community')
    parser.add_argument('meshviewer_json_url', metavar='URL', type=str, nargs=1, help='meshviewer.json URL')
    args = parser.parse_args()

    model_information = load_devices_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       "devices.json"))
    meshviewer_json = load_meshviewer_json(args.meshviewer_json_url[0])
    community_information = gather_information(model_information, meshviewer_json)

    print_information(community_information)

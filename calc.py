#! /usr/bin/env python3
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


def load_nodes_json(url):
    res = requests.get(url)

    if res.status_code is not 200:
        return None

    out = []
    for n in res.json()['nodes']:
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


def print_information(community_information, print_output=True):
    total_loss = 0
    data = {'models': {}, 'loss': 0}

    for model in community_information:
        if model["total"] == -1:
            continue

        total_loss += model["total"]
        data['models'][model["model"]] = {'count': model["count"], 'loss': model["total"]}

        if print_output:
            print("{model} - Device count: {count} - Loss: {total_loss}€".format(
                model=model["model"],
                count=model["count"],
                total_loss=model["total"]
            ))

    if print_output:
        print("Total loss:  {loss}€".format(loss=total_loss))
    else:
        data['loss'] = total_loss
        print(json.dumps(data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate net-worth of a Freifunk community')
    parser.add_argument('--meshviewer-json', help='meshviewer.json URL', action="append")
    parser.add_argument('--nodes-json', help='nodes.json URL', action="append")
    parser.add_argument('--output-json', help='Stats as JSON', action='store_true')
    args = parser.parse_args()

    model_information = load_devices_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       "devices.json"))
    meshviewer_json = []
    if args.meshviewer_json is not None:
        for url in args.meshviewer_json:
            meshviewer_json += load_meshviewer_json(url)
    elif args.nodes_json is not None:
        for url in args.nodes_json:
            meshviewer_json += load_nodes_json(url)
    else:
        exit(1)
    community_information = gather_information(model_information, meshviewer_json)

    print_information(community_information, not args.output_json)

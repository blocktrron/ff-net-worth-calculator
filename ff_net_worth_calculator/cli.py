import argparse
from ff_net_worth_calculator import *


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


def run():
    parser = argparse.ArgumentParser(description='Calculate net-worth of a Freifunk community')
    parser.add_argument('--alfred-json', help='alfred.json URL', action="append")
    parser.add_argument('--meshviewer-json', help='meshviewer.json URL', action="append")
    parser.add_argument('--nodes-json', help='nodes.json URL', action="append")
    parser.add_argument('--franken', help='Franken URL', action="append")
    parser.add_argument('--output-json', help='Stats as JSON', action='store_true')
    parser.add_argument('--exclude-domain', help='Domains to exclude for calculation', action="append")
    args = parser.parse_args()

    meshviewer_json = []
    if args.meshviewer_json is not None:
        for url in args.meshviewer_json:
            meshviewer_json += load_meshviewer_json(url, args.exclude_domain or None)
    elif args.nodes_json is not None:
        for url in args.nodes_json:
            meshviewer_json += load_nodes_json(url)
    elif args.alfred_json is not None:
        for url in args.alfred_json:
            meshviewer_json += load_alfred_json(url)
    elif args.franken is not None:
        for url in args.franken:
            meshviewer_json += load_franken(url)
    else:
        parser.print_help()
        exit(1)

    model_information = load_devices_json(get_data_path('devices.json'))
    community_information = gather_information(model_information, meshviewer_json)

    print_information(community_information, not args.output_json)

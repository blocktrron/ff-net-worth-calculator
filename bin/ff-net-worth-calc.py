#!/usr/bin/env python3

import argparse
from ff_net_worth_calculator import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate net-worth of a Freifunk community')
    parser.add_argument('--meshviewer-json', help='meshviewer.json URL', action="append")
    parser.add_argument('--nodes-json', help='nodes.json URL', action="append")
    parser.add_argument('--output-json', help='Stats as JSON', action='store_true')
    args = parser.parse_args()

    meshviewer_json = []
    if args.meshviewer_json is not None:
        for url in args.meshviewer_json:
            meshviewer_json += load_meshviewer_json(url)
    elif args.nodes_json is not None:
        for url in args.nodes_json:
            meshviewer_json += load_nodes_json(url)
    else:
        parser.print_help()
        exit(1)

    model_information = load_devices_json(get_data_path('devices.json'))
    community_information = gather_information(model_information, meshviewer_json)

    print_information(community_information, not args.output_json)

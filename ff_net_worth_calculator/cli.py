import argparse
import sys
from ff_net_worth_calculator import *


def print_information(url, community_information, print_output=True):
    total_loss = 0
    data = {'models': {}, 'loss': 0}

    print(f"Evaluation of {url}")

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
    parser.add_argument('--url', help='URL to evaluate')
    parser.add_argument('--output-json', help='Stats as JSON', action='store_true')
    parser.add_argument('--exclude-domain', help='Domains to exclude for calculation', action="append")
    args = parser.parse_args()

    if args.url:
        result = load(args.url, args.exclude_domain)
    else:
        parser.print_help()
        sys.exit(1)

    if not result:
        print("No nodes found", file=sys.stderr)
        sys.exit(2)

    model_information = load_devices_json(get_data_path('devices.json'))
    community_information = gather_information(model_information, result)

    print_information(args.url, community_information, not args.output_json)

import ff_net_worth_calculator as nwc
import json


with open("communities.json") as handle:
    communities = json.load(handle)

for community, urls in communities.items():
    print(community)
    for url in urls:
        print(url)
        nwc.load(url)

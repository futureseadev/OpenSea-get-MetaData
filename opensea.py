import requests
import csv
import time


def get_leaves(item, key=None):
    if isinstance(item, dict):
        leaves = []
        for i in item.keys():
            leaves.extend(get_leaves(item[i], i))
        return leaves
    elif isinstance(item, list):
        leaves = []
        for i in item:
            leaves.extend(get_leaves(i, key))
        return leaves
    else:
        return [(key, item)]


def main():
    output_file = time.strftime("%Y%m%d-%H%M%S") + ".csv"
    s = requests.Session()

    HEADER = {
        "Referer": "https://opensea.io/",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "X-API-KEY": "2f6f419a083c46de9d83ce3dbe7db601"
    }

    opensea_url = "https://api.opensea.io/api/v1/assets"

    offset = 0
    try:
        write_header = True
        while True:
            querystring = {
                "asset_contract_address": "0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d",
                "order_direction": "desc",
                "offset": offset, "limit": "50"}
            r = s.get(opensea_url, headers=HEADER, params=querystring)
            if r.status_code == 200:
                result = r.json()
                if result != {}:
                    last_results = []
                    data = result["assets"]
                    for asset in data:
                        metadata = {}
                        metadata["name"] = asset["name"]
                        metadata["image"] = asset["image_original_url"]
                        assets = sorted(asset["traits"], key=lambda k: k['trait_type'])
                        for idx, trait in enumerate(assets):
                            metadata["attributes" + str(idx)] = {}
                            metadata["attributes" + str(idx)]["trait_type"] = trait["trait_type"]
                            metadata["attributes" + str(idx)]["value"] = trait["value"]
                            try:
                                metadata["attributes" + str(idx)]["max_value"] = trait["max_value"]
                            except:
                                pass
                        # metadata["attributes"] = asset["traits"]
                        last_results.append(metadata)

                    with open(output_file, 'a', newline='', encoding="utf8") as f_output:
                        for result in last_results:
                            csv_output = csv.writer(f_output)

                            leaf_entries = get_leaves(result)

                            if write_header:
                                csv_output.writerow([k for k, v in leaf_entries])
                                write_header = False

                            csv_output.writerow([v for k, v in leaf_entries])

                else:
                    break
                offset = offset + 50
                # print(result)
                # print("done!")
            else:
                print("get error id")
                break
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()

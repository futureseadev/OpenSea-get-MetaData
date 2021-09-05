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
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "www.niftyriver.io",
        "Referer": "https://www.niftyriver.io/rarity/0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile":"?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }
    rarity_url = "https://www.niftyriver.io/api/platforms/collection/0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d/rarity-details/"
    all_count = 0
    try:
        r = s.get(rarity_url, headers=HEADER)
        if r.status_code == 200:
            result = r.json()
            all_count = result["minted_count"]

        else:
            print("get error eventID")
            # break
    except Exception as e:
        print(str(e))
    get_url = "https://www.niftyriver.io/api/platforms/collection/0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d/rarity/"

    offset = 0
    p_size = 0
    page = 1
    try:
        write_header = True
        while p_size < all_count:
            querystring = {
                            "page_size": 50,
                            "page": page
                            }
            r = s.get(get_url, headers=HEADER, params=querystring)
            if r.status_code == 200:
                result = r.json()
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
                print("get error eventID")
                break
            p_size = p_size + 50
            page = page + 1
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()

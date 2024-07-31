import os
import requests

FOLDER = "./nsis/"


def get_date(hash) -> str:
    url = "https://mb-api.abuse.ch/api/v1/"
    data = {
        "query": "get_info",
        "hash": hash,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        json_response = response.json()
        try:
            first_seen = json_response["data"][0]["first_seen"]
        except KeyError:
            return "None"
        first_seen_date = first_seen.split(" ")[0].replace("-", "_")

        return first_seen_date
    else:
        return "None"


for category in os.listdir(FOLDER):
    for sample_folder in os.listdir(FOLDER + category):
        if (
            "2024_" not in sample_folder
            and "." not in sample_folder
            and "None_" not in sample_folder
        ):
            date = get_date(sample_folder)
            os.system(
                rf"mv {FOLDER + category}/{sample_folder} {FOLDER + category}/{date + '_' + sample_folder}"
            )
            print(date + "_" + sample_folder)

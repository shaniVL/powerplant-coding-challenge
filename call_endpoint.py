import sys
import json
import requests

url = "http://127.0.0.1:8888/productionplan"

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = json.load(f)
    response = requests.post(url, json.dumps(data))
    print(json.dumps(response.json(), indent=2))
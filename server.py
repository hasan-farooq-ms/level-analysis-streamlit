from collections import Counter
from flask import Flask, request, jsonify
import json


app = Flask(__name__)

# second row shop items
valid_skus = [
    "com.gamebrain.hexasort.tinyhexpack",
    "com.gamebrain.hexasort.minihexpack",
    "com.gamebrain.hexasort.hexvaultpack",
    "com.gamebrain.hexasort.grandhexpack",
    "com.gamebrain.hexasort.megahexpack",
]


def parse_json_strings(obj):
    """
    Recursively parses any string fields that are actually JSON objects or arrays.
    Works for dicts and lists.
    """
    if isinstance(obj, dict):
        parsed = {}
        for key, value in obj.items():
            if isinstance(value, str):
                try:
                    value_parsed = json.loads(value)
                    parsed[key] = parse_json_strings(value_parsed)
                except json.JSONDecodeError:
                    parsed[key] = value
            else:
                parsed[key] = parse_json_strings(value)
        return parsed

    elif isinstance(obj, list):
        return [parse_json_strings(item) for item in obj]

    else:
        return obj

def find_top_valid_sku(purchase_records, valid_skus):
    filtered_skus = [record["SkuId"] for record in purchase_records if record.get("SkuId") in valid_skus]

    if not filtered_skus:
        return "com.gamebrain.hexasort.tinyhexpack"

    sku_counts = Counter(filtered_skus)
    most_common_sku, _ = sku_counts.most_common(1)[0]

    return most_common_sku



@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(force=True)
    parsed_data = parse_json_strings(data)

    user_id = parsed_data.get("UserId")
    user_state = parsed_data.get("UserState")
    user_analytics = parsed_data.get("Analytics")
    user_purchases = parsed_data.get("IAPRecords", {})

    all_purchase_records = user_purchases.get("IAPRecordBook", {}).get("Records", [])
    shop_item = find_top_valid_sku(all_purchase_records, valid_skus)

    if not all_purchase_records:
        result = [shop_item]
    elif len(all_purchase_records) == 1:
        result = [shop_item]
    else:
        print("-"*20)
        print("Total Purchases Made:", len(all_purchase_records))
        print("-"*20)
        result = [shop_item]

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5004)


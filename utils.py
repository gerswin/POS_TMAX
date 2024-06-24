import json
from datetime import datetime
import pytz

def build_response(body: dict, status_code=200, cors_headers="*", cors_origin="*", content_type="application/json"):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Headers": cors_headers
        },
        "body": json.dumps(body, default=str, sort_keys=True, indent=4)
    }


def build_success_response(data, model, status_code=200, cors_headers="*", cors_origin="*",
                           content_type="application/json"):
    if type(data) == list:
        r = []
        for item in data:
            if "id" in item.keys():
                r.append(
                    {"id": item["id"], "type": model, "attributes": {k: v for k, v in item.items() if k not in ["id"]}})
            else:
                r.append(
                    {"id": "", "type": model, "attributes": {k: v for k, v in item.items() if k not in ["id"]}})

        body = {"data": r}
        return build_response(body, status_code, cors_headers, cors_origin, content_type)
    if type(data) == dict:
        id = ""
        if model == "Ani":
            id = data.get("nuip", "")
        if "id" in data:
            id = data.get("id")

        body = {"data": {"id": id, "type": model, "attributes": data}}
        return build_response(body, status_code, cors_headers, cors_origin, content_type)





caracas_time_zone = pytz.timezone("America/Caracas")
timeInNewYork = datetime.now(caracas_time_zone)
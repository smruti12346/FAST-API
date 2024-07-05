import requests
import xmltodict
import json

USPS_USER_ID = "YOUR_USPS_USER_ID"  # Replace with your USPS User ID


def json_to_xml(json_obj):
    """Convert a JSON object to an XML string."""
    xml_str = xmltodict.unparse(json_obj, pretty=True)
    return xml_str


def xml_to_json(xml_str):
    """Convert an XML string to a JSON string."""
    try:
        dict_data = xmltodict.parse(xml_str)
        json_data = json.dumps(dict_data, indent=4)
        return json_data
    except Exception as e:
        return str(e)


# def json_to_xml(json_obj, line_padding=""):
#     """Convert a JSON object to an XML string."""

#     def to_xml(json_obj, line_padding):
#         """Helper function to convert JSON to XML."""
#         result_list = []

#         if isinstance(json_obj, dict):
#             for tag_name in json_obj:
#                 sub_obj = json_obj[tag_name]
#                 result_list.append("%s<%s>" % (line_padding, tag_name))
#                 result_list.append(to_xml(sub_obj, "\t" + line_padding))
#                 result_list.append("%s</%s>" % (line_padding, tag_name))

#         elif isinstance(json_obj, list):
#             for sub_obj in json_obj:
#                 result_list.append(to_xml(sub_obj, line_padding))

#         else:
#             result_list.append("%s%s" % (line_padding, json_obj))

#         return "\n".join(result_list)

#     return to_xml(json_obj, line_padding)


def get_usps_shipping_rate(json_request):
    try:
        url = "http://production.shippingapis.com/ShippingAPI.dll"
        api = "Verify"

        # Convert JSON request to XML
        xml_request = json_to_xml(json_request)

        response = requests.get(url, params={"API": api, "XML": xml_request})

        if response.status_code == 200:
            # Convert XML response to JSON
            response_dict = xmltodict.parse(response.text)
            # response_json = json.dumps(response_dict, indent=4)
            return {"data": response_dict, "status": "success"}
        else:
            return {
                "message": response.text,
                "status_code": response.status_code,
                "status": "error",
            }
    except Exception as e:
        return {"message": str(e), "status": "error"}


# # Example JSON request
# json_request = {
#     "AddressValidateRequest": {
#         "@USERID": "XXXXXX",
#         "Revision": "1",
#         "Address": {
#             "Address1": "Suite 6100",
#             "Address2": "185 Berry St",
#             "City": "San Francisco",
#             "State": "CA",
#             "Zip5": "94556",
#             "Zip4": "",
#         },
#     }
# }

# # Get the shipping rate
# response_json = get_usps_shipping_rate(json_request)
# print(response_json)

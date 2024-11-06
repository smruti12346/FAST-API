from db import db
from lxml import etree
import requests
import json

from services import shippingService


collection = db["shipping"]


def login_and_get_token():

    shippinggetway = shippingService.view_by_shipping_company_name("Veracore")

    if len(shippinggetway["data"]) > 0:
        shippinggetway = shippinggetway["data"][0]

        # Define the URL
        url = f"https://{shippinggetway['domain_url']}/VeraCore/Public.Api/api/Login"

        # Define the JSON payload
        payload = {
            "userName": shippinggetway["user_id"],
            "password": shippinggetway["password"],
            "systemId": shippinggetway["api_key"],
        }

        # Define the headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            # Send the POST request
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an error if the request was not successful

            # Parse and return the JSON response
            response = response.json()
            response["status"] = "success"
            response["domain_url"] = shippinggetway["domain_url"]
            return response

        except requests.exceptions.RequestException as e:
            # Handle errors
            return {"status": "fail", "error": str(e)}


def veracore_order_fulfill(product_id, quantity, unit_price, user_address):
    # print(user_address['Prefix'])

    shippinggetway = shippingService.view_by_shipping_company_name("Veracore")

    if len(shippinggetway["data"]) > 0:
        shippinggetway = shippinggetway["data"][0]

        # Convert the order_data dictionary to XML format, including ShipTo details
        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Header>
                <AuthenticationHeader xmlns="http://omscom/">
                    <Username>{shippinggetway['user_id']}</Username>
                    <Password>{shippinggetway['password']}</Password>
                </AuthenticationHeader>
            </soap:Header>
            <soap:Body>
                <AddOrder xmlns="http://omscom/">
                    <order>
                        <OrderedBy>
                            <Prefix>{user_address['Prefix']}</Prefix>
                            <FirstName>{user_address['FirstName']}</FirstName>
                            <LastName>{user_address['LastName']}</LastName>
                            <Address1>{user_address['Address1']}</Address1>
                            <City>{user_address['City']}</City>
                            <State>{user_address['State']}</State>
                            <PostalCode>{user_address['PostalCode']}</PostalCode>
                            <Country>{user_address['Country']}</Country>
                            <Phone>{user_address['Phone']}</Phone>
                            <Email>{user_address['Email']}</Email>
                        </OrderedBy>
                        <ShipTo>
                            <OrderShipTo>
                                <Flag>OrderedBy</Flag>
                                <Key>1</Key>
                            </OrderShipTo>
                        </ShipTo>
                        <Offers>
                            <OfferOrdered>
                                <Offer>
                                    <Header>
                                        <ID>{product_id}</ID>
                                    </Header>
                                </Offer>
                                <Quantity>{quantity}</Quantity>
                                <UnitPrice>{unit_price}</UnitPrice>
                                <OrderShipTo>
                                    <Key>1</Key>
                                </OrderShipTo>
                            </OfferOrdered>
                        </Offers>
                    </order>
                </AddOrder>
            </soap:Body>
        </soap:Envelope>"""

        # Define SOAP endpoint URL and headers
        url = f"https://{shippinggetway['domain_url']}/pmomsws/oms.asmx"
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://omscom/AddOrder",
        }

        # Send the SOAP request
        response = requests.post(url, data=envelope.encode("utf-8"), headers=headers)

        # Check for a successful response
        if response.status_code == 200:
            # Parse the XML response
            root = etree.fromstring(response.content)
            namespace = {
                "soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "ns": "http://omscom/",
            }
            order_seq_id = root.find(".//ns:OrderSeqID", namespaces=namespace).text
            order_id = root.find(".//ns:OrderID", namespaces=namespace).text

            # Return the response as JSON
            return {
                "OrderSeqID": order_seq_id,
                "OrderID": order_id,
                "status": "success",
            }

        else:
            # Handle errors
            return {
                "error": "Failed to send order",
                "status_code": response.status_code,
                "status": "fail",
                "message": response.text,
            }

    return {"message": "Veracore not activate", "status": "veracore not activate"}

def get_veracore_product_details(product_id):
    try:
        veracoredetails = login_and_get_token()

        url = f"https://{veracoredetails['domain_url']}/VeraCore/Public.Api/api/GetInventory?offerIds={product_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer " + veracoredetails["Token"],
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {"data": response.json()["Inventory"], "status": "success"}

    except requests.exceptions.RequestException as e:
        return {"status": "fail", "error": str(e)}


def get_veracore_tracking_details(product_id):
    try:
        ShippingServiceDetails = {}
        AdminShipingDetails = shippingService.view_by_status(1)
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            ShippingServiceDetails = AdminShipingDetails["data"][0]


        veracoredetails = login_and_get_token()

        url = f"https://{veracoredetails['domain_url']}/VeraCore/Public.Api/api/GetPackages?request.ordersIds={product_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer " + veracoredetails["Token"],
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response = response.json()


        if response["ShippingUnits"] != None:
            result = {}
            result["postage_label_url"] = None
            result["billing_type"] = ShippingServiceDetails['shipping_company_name']
            result["carrier"] = response["ShippingUnits"][0]["Shipping"]['FreightCarrier']
            result["carrier_account_id"] = ShippingServiceDetails['user_id']
            result["currency"] = ShippingServiceDetails['currency']
            result["retail_rate"] = None
            result["tracking_url"] = response["ShippingUnits"][0]["Shipping"]['TrackingLink']

            return {
                "data": result,
                "status": "success",
            }
        else:
            return {"data": {}, "status": "error"}
    

    except requests.exceptions.RequestException as e:
        return {"status": "fail", "error": str(e)}

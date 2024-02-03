import requests
from helpers import Api, Parser
import json

FORTNITE_SHOP_URL = "https://fortnite-api.com/v2/shop/br/combined"
    
def main() -> None:
    api = Api()
    print("Fortnite Item Purchaser: Made by hzh.")
    print(f"Open this url while you are logged into your account and obtain the code\n{api.URL}\n")
    
    while True:
        code = input("Input the code here: ")
        if len(code) == 32:
            break
        else:
            print("Invalid code!\n")

    body = api.grant_body(code) # getting the header that needs the code for auth
    # using code to obtain accessToken and other data
    response = requests.post(url=api.URL2, headers=api.headers, data=body)
    response_data = json.loads(response.content.decode("utf-8"))
    checkError(response_data)

    accessToken = response_data["access_token"]
    account_id = response_data["account_id"]
    username = response_data["displayName"]
    expires_in = response_data["expires_in"]
    api_header = api.grant_token(accessToken) # obtaining new header for auth

    print(f"\nWelcome {username}, token expires in {expires_in}\n")

    # obtaining the item shop data and printing it out
    response = requests.get(url=FORTNITE_SHOP_URL)
    itemShop = json.loads(response.content.decode("utf-8"))
    parser = Parser(itemShop)
    parsed_shop = parser.parse_shop()
    for index, item in enumerate(parsed_shop, start=1):
        name = item["name"].split()
        try: name.remove("[VIRTUAL]1")
        except ValueError: pass
        name = [elem for elem in name if elem != 1 and elem != "1" and elem != "x"]
        name = " ".join(name[:-3])
        price = item["price"]
        print(f"{index}. {name}\nPrice: {price} Vbucks\n")

    while True:
        item_number = input("Input the number of the item you want to purchase: ")
        if checkNumber(item_number, parsed_shop):
            selected_item = parsed_shop[int(item_number) - 1]
            offerid = selected_item["offerid"]
            price = selected_item["price"]
            break
        else:
            print("Invalid item number!\n")
    
    payload = {
        "offerId": offerid,
        "purchaseQuantity": 1,
        "currency": "MtxCurrency",
        "expectedTotalPrice": price,
        "gameContext": "",
        "currencySubType": ""
    }
    json_header = {"Content-Type": "application/json"}
    api_header_with_json = {**json_header, **api_header}

    # purchasing item
    response = requests.post(url=api.grant_operationUrl("PurchaseCatalogEntry", account_id, "common_core"), headers=api_header_with_json, json=payload)
    response_data = json.loads(response.content.decode("utf-8"))
    checkError(response_data)

    while True:
        choice = input("Do you want to cancel purchase? [y]/[n]: ")
        if choice == "y":
            last_purchased = response_data["profileChanges"][0]["profile"]["stats"]["attributes"]["mtx_purchase_history"]["purchases"][-1]
            purchase_id = last_purchased["purchaseId"]
            last_offerid = last_purchased["offerId"]
            if offerid == last_offerid:
                payload = {
                    "purchaseId": purchase_id,
                    "quickReturn": True
                }
                response = requests.post(url=api.grant_operationUrl("RefundMtxPurchase", account_id, "common_core"), headers=api_header_with_json, json=payload)
                response_data = json.loads(response.content.decode("utf-8"))
                print(response_data)
                checkError(response_data)
                break
        elif choice == "n":
            break
        else:
            print("Invalid choice!\n")

    # killing access token for no ratelimiting
    response = requests.delete(url=api.KILL_AUTH_URL + accessToken, headers=api_header)
    if response.content == b"":
        print("accessToken killed")
    else:
        print("Could not kill access token: ", end="")
        response_data = json.loads(response.content.decode("utf-8"))
        checkError(response_data)

def checkError(response_data: dict) -> None:
    if "errorCode" in response_data:
        err = response_data["errorMessage"]
        print(f"Error with request: {err}")
        exit(-1)

def checkNumber(number: str, itemShop: list) -> bool:
    if number.isdigit():
        number = int(number)
        if 1 < number <= len(itemShop):
            return True
        else: 
            return False
    else:
        return False

if __name__ == "__main__":
   main()
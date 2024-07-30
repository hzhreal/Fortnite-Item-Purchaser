import requests
import json
from helpers import Api, Parser

FORTNITE_SHOP_URL = "https://fortnite-api.com/v2/shop/br/combined"
    
def main() -> None:
    api = Api()
    print("Fortnite Item Purchaser: Made by hzh.")
    print(f"Open this url while you are logged into your account and obtain the code.\n{api.URL}\n")
    
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
    checkError(response_data, [])

    accessToken = response_data["access_token"]
    account_id = response_data["account_id"]
    username = response_data["displayName"]
    expires_in = response_data["expires_in"]
    api_header = api.grant_token(accessToken) # obtaining new header for auth

    print(f"Welcome {username}, token expires in {expires_in}\n")

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
        item["name"] = name
        print(f"{index}. {name}\nPrice: {price} Vbucks\n")

    # Make header to send json content
    json_header = {"Content-Type": "application/json"}
    api_header_with_json = {**json_header, **api_header}

    # Obtain vbucks data
    vbucks_balance = obtain_vbucks_bal(api, account_id, api_header_with_json)
    print(f"You have: {vbucks_balance} Vbucks available.\n")

    # Input user to purchase item and cancel purchase right after, user can do this as long as wanted. However, token might expire.
    while True:
        answer = input("Do you want to purchase an item? [y/n]: ")
        if answer.lower() == "y":
            purchase_prompt(api, account_id, api_header_with_json, api_header, accessToken, parsed_shop)
        elif answer.lower() == "n":
            break
        else:
            print("Invalid answer!\n")
    
    # killing access token for no ratelimiting
    kill_accessToken(api, accessToken, api_header)

def purchase_prompt(api: Api, account_id: str, api_header_with_json: dict, api_header: dict, accessToken: str, parsed_shop: list) -> None:
    def cancel_purchase(purchase_id: str) -> dict:
        payload = {
                    "purchaseId": purchase_id,
                    "quickReturn": True
                }
        response = requests.post(url=api.grant_operationUrl("RefundMtxPurchase", account_id, "common_core"), headers=api_header_with_json, json=payload)
        response_data = json.loads(response.content.decode("utf-8"))
        checkError(response_data, [api, accessToken, api_header])
        return response_data

    while True:
        item_number = input("Input the number of the item you want to purchase: ")
        if checkNumber(item_number, parsed_shop):
            selected_item = parsed_shop[int(item_number) - 1]
            offerid = selected_item["offerid"]
            price = selected_item["price"]
            name = selected_item["name"]
            break
        else:
            print("Invalid item number!\n")
    
    purchase_payload = {
        "offerId": offerid,
        "purchaseQuantity": 1,
        "currency": "MtxCurrency",
        "expectedTotalPrice": price,
        "gameContext": "",
        "currencySubType": ""
    }

    response = requests.post(url=api.grant_operationUrl("PurchaseCatalogEntry", account_id, "common_core"), headers=api_header_with_json, json=purchase_payload)
    response_data = json.loads(response.content.decode("utf-8"))
    checkError(response_data, [api, accessToken, api_header])
    print(f"Purchased {name}")

    while True:
        choice = input("\nDo you want to cancel purchase? [y]/[n]: ")
        if choice.lower() == "y":
            purchases = response_data["profileChanges"][0]["profile"]["stats"]["attributes"]["mtx_purchase_history"]["purchases"]
            last_purchase_id = purchases[-1]["purchaseId"]
            last_offerid = purchases[-1]["offerId"]
            if offerid == last_offerid:
                response_data = cancel_purchase(last_purchase_id)
                print(f"Cancelled purchase of {name}")
                break
            else:
                for purchase in response_data["profileChanges"][0]["profile"]["stats"]["attributes"]["mtx_purchase_history"]["purchases"]:
                    purchase_id = purchase["purchaseId"]
                    if purchase["offerId"] == offerid:
                        response_data = cancel_purchase(purchase_id)
                        print(f"Cancelled purchase of {name}")
                        break
                break
        elif choice.lower() == "n":
            break
        else:
            print("Invalid choice!\n")

    vbucks_balance = api.calculate_vbucks(response_data)
    print(f"\nYou have {vbucks_balance} Vbucks left.\n")

def checkNumber(number: str, itemShop: list) -> bool:
        if number.isdigit():
            number = int(number)
            if 1 < number <= len(itemShop):
                return True
            else: 
                return False
        else:
            return False
    
def obtain_vbucks_bal(api: Api, account_id: str, api_header_with_json: dict) -> int:
    response = requests.post(url=api.grant_operationUrl("QueryProfile", account_id, "common_core"), headers=api_header_with_json, json={})
    profile_data = json.loads(response.content.decode("utf-8"))
    return api.calculate_vbucks(profile_data)
    
def kill_accessToken(api: Api, accessToken: str, api_header: dict) -> None:
    response = requests.delete(url=api.KILL_AUTH_URL + accessToken, headers=api_header)
    if response.content == b"":
        print("accessToken killed")
    else:
        print("Could not kill access token, ", end="")
        response_data = json.loads(response.content.decode("utf-8"))
        checkError(response_data, [])

def checkError(response_data: dict, kill_token: list) -> None:
    if "errorCode" in response_data:
        err = response_data["errorMessage"]
        print(f"Error with request: {err}") 
        if len(kill_token) == 3:
            kill_accessToken(kill_token[0], kill_token[1], kill_token[2])
        exit(-1)  

if __name__ == "__main__":
   main()

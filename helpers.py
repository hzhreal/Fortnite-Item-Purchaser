from base64 import b64encode

class Api:
    def __init__(self) -> None:
        self.FORTNITE_PC_CLIENT_ID = "ec684b8c687f479fadea3cb2ad83f5c6"
        self.FORTNITE_PC_SECRET = "e1f31c211f28413186262d37a13fc84d"
        self.URL = f"https://www.epicgames.com/id/api/redirect?clientId={self.FORTNITE_PC_CLIENT_ID}&responseType=code"
        self.URL2 = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
        self.IDS_ENCODED = b64encode((self.FORTNITE_PC_CLIENT_ID + ":" + self.FORTNITE_PC_SECRET).encode("utf-8")).decode("utf-8")
        self.KILL_AUTH_URL = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/sessions/kill/"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {self.IDS_ENCODED}"
        } 

    @staticmethod
    def grant_body(code: str) -> dict:
        body = {
            "grant_type": "authorization_code",
            "code": code
        }

        return body
    
    @staticmethod 
    def grant_token(accessToken: str) -> dict:
        code_header = {
            "Authorization": f"bearer {accessToken}"
        }
        
        return code_header

    @staticmethod
    def grant_operationUrl(operation: str, account_id: str, profile_id: str) -> str:
        return f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{account_id}/client/{operation}?profileId={profile_id}&rvn=-1"

class Parser:
    def __init__(self, itemShop: dict) -> None:
        self.itemShop = itemShop

    def parse_shop(self) -> list:
        parsed_shop = []
        if self.itemShop["status"] != 200:
            print("Error with the item shop data.")
            exit(-1)

        shops = [self.itemShop["data"]["featured"], self.itemShop["data"]["daily"]]
        for tab in shops:
            if tab is not None:
                for entry in tab["entries"]:
                    item_data = {
                        "name": entry["devName"],
                        "price": entry["finalPrice"],
                        "offerid": entry["offerId"] 
                    }
                    parsed_shop.append(item_data)
        return parsed_shop
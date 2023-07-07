from fastapi import FastAPI
import uvicorn
import httpx
import json
from typing import List
from fastapi import Query

# eBay API credentials
APP_ID = 'EllieLin-gptplugi-PRD-796122c6d-803dfcef'
CERT_ID = 'PRD-96122c6d2c5b-ffc5-4883-868a-5181'
CAMPAIGN_ID = 5338995640  # Your eBay Campaign ID

app = FastAPI()


@app.get("/.well-known/ai-plugin.json")
async def read_manifest():
    with open('./manifest.json', 'r') as file:
        data = json.load(file)
    return data


@app.get("/search")
async def search_ebay(query: str, color: str = None, size: str = None, brand: str = None, max_price: float = None, entries_per_page: int = 10, page_number: int = 1, top_rated_seller: bool = False):
    url = 'https://svcs.ebay.com/services/search/FindingService/v1'
    params = {
        'OPERATION-NAME': 'findItemsAdvanced',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': APP_ID,
        'RESPONSE-DATA-FORMAT': 'JSON',
        'REST-PAYLOAD': '',
        'keywords': query,
        'paginationInput.entriesPerPage': entries_per_page,
        'paginationInput.pageNumber': page_number
    }
    if max_price is not None:
        params['itemFilter(0).name'] = 'MaxPrice'
        params['itemFilter(0).value'] = str(max_price)
    if top_rated_seller:
        params['itemFilter(1).name'] = 'TopRatedSellerOnly'
        params['itemFilter(1).value'] = 'true'
    if color is not None:
        params['aspectFilter(0).aspectName'] = 'Color'
        params['aspectFilter(0).aspectValueName'] = color
    if size is not None:
        params['aspectFilter(1).aspectName'] = 'Size'
        params['aspectFilter(1).aspectValueName'] = size
    if brand is not None:
        params['aspectFilter(2).aspectName'] = 'Brand'
        params['aspectFilter(2).aspectValueName'] = brand
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    data = response.json()
    items = data['findItemsAdvancedResponse'][0]['searchResult'][0]['item']

    # Generate eBay affiliate link for each item
    for item in items:
        item_id = item['itemId'][0]
        item['viewItemURL'] = f"https://rover.ebay.com/rover/1/711-53200-19255-0/1?ff3=2&toolid=10044&campid={CAMPAIGN_ID}&customid=&lgeo=1&vectorid=229466&item={item_id}"

    return items

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
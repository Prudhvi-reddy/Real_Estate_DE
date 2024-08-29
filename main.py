import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

SBR_WS_CDP = 'wss://brd-customer-hl_516250ae-zone-real_estate:8j45zl1javmq@brd.superproxy.io:9222'
BASE_URL = "https://www.redfin.com"
LOCATION = "Orlando"

async def run(pw):
    print('Connecting to Scraping Browser...')
    browser = await pw.chromium.connect_over_cdp(SBR_WS_CDP)
    try:
        page = await browser.new_page()
        print('Connected! Navigating to {BASE_URL}')
        await page.goto(BASE_URL)
   
   
   
    # Fill  search bar with location
        await page.fill('input[name="searchInputBox"]', LOCATION)
        await page.keyboard.press("Enter")
        print("waiting for search results..........")
        await page.wait_for_load_state("load")

        content = await page.inner_html('div[data-rf-test-id="photos-view"]')

        soup = BeautifulSoup(content, "html.parser")

        for idx, div in enumerate(soup.find_all("div", class_ = "HomeCardContainer flex justify-center")):
            data = {}
        
            address = div.find(class_="bp-Homecard__Address flex align-center color-text-primary font-body-xsmall-compact").text
            price = div.find(class_='bp-Homecard__Price--value').text
            Link = div.find('a')['href']
        
            data.update({
                "address": address,
                "price":price,
                "link": BASE_URL + Link
            })

            print(data)
            break


        print('Navigated! Scraping page content...')
        # html = await page.content()
        # print(html)
    finally:
        await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == '__main__':
    asyncio.run(main())
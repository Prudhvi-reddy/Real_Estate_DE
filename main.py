import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.redfin.com"
LOCATION = "Orlando"

async def run(pw):
    print('Launching browser...')
    browser = await pw.chromium.launch(headless=False)  # Launch the browser in non-headless mode
    try:
        page = await browser.new_page()
        print(f'Navigating to {BASE_URL}')
        await page.goto(BASE_URL)
   
        # Fill search bar with location
        await page.fill('input[name="searchInputBox"]', LOCATION)
        await page.keyboard.press("Enter")
        print("Waiting for search results...")
        await page.wait_for_load_state("load")


        content = await page.inner_html('div[data-rf-test-id="photos-view"]')

        soup = BeautifulSoup(content, "html.parser")

        for idx, div in enumerate(soup.find_all("div", class_="HomeCardContainer flex justify-center")):
            data = {}
        
            address = div.find(class_="bp-Homecard__Address flex align-center color-text-primary font-body-xsmall-compact").text
            price = div.find(class_='bp-Homecard__Price--value').text
            link = div.find('a')['href']
        
            data.update({
                "address": address,
                "price": price,
                "link": BASE_URL + link
            })

            print(data)
            break

        print('Navigated! Scraping page content...')
    finally:
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':
    asyncio.run(main())

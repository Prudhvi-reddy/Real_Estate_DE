import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.redfin.com"
LOCATION = "Orlando"


def extract_picture(picture_section):
    picture_sources = []
    for picture in picture_section.find_all("span"):
        for img in span.find_all("img"):
            pic_url = img.get("src")
            picture_sources.append(pic_url)

    return picture_sources


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
            link = div.find('a')['href']
            data = {
                "address": div.find(class_="bp-Homecard__Address flex align-center color-text-primary font-body-xsmall-compact").text,
                "price": div.find(class_='bp-Homecard__Price--value').text,
                "link": BASE_URL + link
            }
        
            #go to the listing page
            print("Navigating to the lsiting page ", link)
            await page.goto(data['link'])
            await page.wait_for_load_state("load")

            # content = await page.inner_html('div[class="detailsContent"]')
            content = await page.inner_html('div.detailsContent')
            soup = BeautifulSoup(content, "html.parser")

            picture_section = soup.find("div", {data-rf-test-id:"mediaBrowser"})
            pictures = extract_picture(picture_section)
            data['pictures'] = pictures





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

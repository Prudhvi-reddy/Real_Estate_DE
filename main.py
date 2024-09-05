import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

BASE_URL = "https://www.redfin.com"
LOCATION = "Orlando"

USER_AGENTS = {
    "chromium": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    ],
    "firefox": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
    ],
    "webkit": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.3 Safari/602.3.12"
    ]
}

def extract_picture(picture_section):
    picture_sources = []
    for picture in picture_section.find_all("span"):
        for img in picture.find_all("img"):
            pic_url = img.get("src")
            picture_sources.append(pic_url)
    return picture_sources

async def retry_async(func, retries=3, delay=2, *args, **kwargs):
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except PlaywrightTimeoutError as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

async def run(pw):
    browsers = ['chromium', 'firefox', 'webkit']
    browser_type = random.choice(browsers)
    
    print(f'Selected Browser: {browser_type}')
    user_agent = random.choice(USER_AGENTS[browser_type])
    
    print(f'Launching {browser_type} with User-Agent: {user_agent}')
    browser = await pw[browser_type].launch(headless=False)

    try:
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        print(f'Navigating to {BASE_URL} with User-Agent: {user_agent}')

        await retry_async(page.goto, retries=3, delay=2, url=BASE_URL)

        # Fill search bar with location
        await asyncio.sleep(random.uniform(1, 3))
        await page.fill('input[name="searchInputBox"]', LOCATION)
        await page.keyboard.press("Enter")
        print("Waiting for search results...")

        await retry_async(page.wait_for_load_state, retries=3, delay=2, state="load")

        content = await page.inner_html('div[data-rf-test-id="photos-view"]')
        soup = BeautifulSoup(content, "html.parser")

        for idx, div in enumerate(soup.find_all("div", class_="HomeCardContainer flex justify-center")):
            link = div.find('a')['href']
            data = {
                "address": div.find(class_="bp-Homecard__Address flex align-center color-text-primary font-body-xsmall-compact").text,
                "price": div.find(class_='bp-Homecard__Price--value').text,
                "link": BASE_URL + link
            }
        
            # Change browser and user agent for each listing page visit
            browser_type = random.choice(browsers)
            user_agent = random.choice(USER_AGENTS[browser_type])
            
            print(f'Navigating to the listing page {BASE_URL + link} with {browser_type} and User-Agent: {user_agent}')
            
            await context.close()  # Close previous context
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()
            
            await asyncio.sleep(random.uniform(2, 4))
            await retry_async(page.goto, retries=3, delay=2, url=data['link'])
            await retry_async(page.wait_for_load_state, retries=3, delay=2, state="load")

            content = await page.inner_html('div.detailsContent')
            soup = BeautifulSoup(content, "html.parser")

            data['pictures'] = extract_picture(soup.find("div", {"data-rf-test-id": "mediaBrowser"}))
            data['beds'] = soup.find("div", {"data-rf-test-id": "abp-beds"}).text
            data['baths'] = soup.find("div", {"data-rf-test-id": "abp-baths"}).text
            data['sqft'] = soup.find("div", {"data-rf-test-id": "abp-sqFt"}).text

            
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

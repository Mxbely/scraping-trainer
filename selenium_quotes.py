import csv
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str] | str


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    bio: str


quotes_dict = dict()
authors = list()


def wait_for(driver, by, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def wait_for_all(driver, by, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, locator))
    )


def move_to_element(driver: webdriver.Chrome, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)


def get_quotes(driver: webdriver.Chrome):
    quotes = driver.find_elements(By.CLASS_NAME, "quote")
    return quotes


def parse_single_quote(quote):
    text = quote.text
    author = quote.find_element(By.CLASS_NAME, "author").text
    tags = quote.find_element(By.CLASS_NAME, "tags").text.split(" ")
    tags = tags[1:]
    return Quote(text, author, tags)


def parse_single_author(driver):
    name = driver.find_element(By.CLASS_NAME, "author-title").text
    name = name.replace("-", " ")
    born_date = driver.find_element(By.CLASS_NAME, "author-born-date").text
    born_location = driver.find_element(By.CLASS_NAME, "author-born-location").text
    bio = driver.find_element(By.CLASS_NAME, "author-description").text
    return Author(name, born_date, born_location, bio)


def parse_all_objects(driver):
    wait_for_all(driver, By.CLASS_NAME, "quote")
    quotes = get_quotes(driver)
    for quote in quotes:
        quote_ = parse_single_quote(quote)
        if quote_.author not in quotes_dict:
            quotes_dict[quote_.author] = list()
        quotes_dict[quote_.author].append(quote_)

        author_page = quote.find_element(By.TAG_NAME, "a")
        move_to_element(driver, author_page)
        print(author_page.get_attribute("href"))
        author_page.click()
        wait_for(driver, By.CLASS_NAME, "author-title")

        author = parse_single_author(driver)
        if author not in authors:
            authors.append(author)

        driver.back()
        wait_for(driver, By.CLASS_NAME, "quote")


def go_next(driver, next_button):
    elem = next_button.find_element(By.TAG_NAME, "a")
    print(elem.text)
    move_to_element(driver, elem)
    elem.click()
    wait_for(driver, By.CLASS_NAME, "quote")


def main():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )  # приховати webdriver
    # options.add_argument("--start-maximized")  # як звичайний користувач
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    with webdriver.Chrome(
        options=options,
    ) as driver:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                });
            """
            },
        )

        driver.get(BASE_URL)
        wait_for(driver, By.CLASS_NAME, "quote")
        while True:
            parse_all_objects(driver)
            next = driver.find_elements(By.CLASS_NAME, "next")
            if next:
                next_button = next[0]
                go_next(driver, next_button)
            else:
                break


if __name__ == "__main__":
    main()
    print(f"Quotes: {len(quotes_dict)}")
    print(f"Authors: {len(authors)}")

    # for author_name, quotes in quotes_dict.items():
    #     print(f"Author: {author_name} quotes: {len(quotes)}")

    with open("quotes.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Author", "Born date", "Born location", "Bio", "Quote", "Tags"]
        )
        for author in authors:
            quotes = quotes_dict[author.name]
            for quote in quotes:
                writer.writerow(
                    [
                        author.name,
                        author.born_date,
                        author.born_location,
                        f"{author.bio[:20]}...",
                        f"{quote.text[:20]}...",
                        quote.tags,
                    ]
                )

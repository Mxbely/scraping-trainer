import csv
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import requests
from LxmlSoup import LxmlSoup

base_url = "https://books.toscrape.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
}
stars_to_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
filename = "books.csv"


@dataclass
class Book:
    title: str
    price: str
    stars: int
    description: str
    upc: str
    product_type: str
    price_excl_tax: str
    price_incl_tax: str
    tax: str
    availability: str
    number_reviews: str


def write_to_csv(books):
    books = [asdict(book) for book in books]
    if books:
        if os.path.exists(filename):
            os.remove(filename)
        with open("books.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=books[0].keys())
            writer.writeheader()
            writer.writerows(books)


def parse_one_book(link):
    res = requests.get(link, headers=headers)
    html = res.text
    soup = LxmlSoup(html)
    product_page = soup.find("article", class_="product_page")
    product_main = product_page.find("div", class_="product_main")
    title = product_main.find("h1").text()
    price = product_main.find("p", class_="price_color").text()
    stars_attr = (
        product_main.find("p", class_="star-rating").attribute("class").split(" ")[1]
    )
    stars = stars_to_number[stars_attr]
    description = product_page.find("p").text()
    product_info = product_page.find("table", class_="table table-striped")

    table_rows = product_info.find_all("tr")
    upc = table_rows[0].find("td").text()
    product_type = table_rows[1].find("td").text()
    price_excl_tax = table_rows[2].find("td").text()
    price_incl_tax = table_rows[3].find("td").text()
    tax = table_rows[4].find("td").text()
    availability = table_rows[5].find("td").text()
    number_reviews = table_rows[6].find("td").text()

    book = Book(
        title=title,
        price=price,
        stars=stars,
        description=description,
        upc=upc,
        product_type=product_type,
        price_excl_tax=price_excl_tax,
        price_incl_tax=price_incl_tax,
        tax=tax,
        availability=availability,
        number_reviews=number_reviews,
    )
    return book


def parse_books(books):

    links = list()
    for book in books:
        lin = book.find("a").attribute("href")
        if "catalogue" not in lin:
            lin = "catalogue/" + lin
        links.append(base_url + lin)

    with ThreadPoolExecutor() as executor:
        res = list(executor.map(parse_one_book, links))
    return list(res)


results = list()


def parse_page(soup: LxmlSoup):
    global results
    books = soup.find_all("article", class_="product_pod")
    books = parse_books(books)
    results.extend(books)
    next_attr = soup.find("li", class_="next")
    if next_attr:
        next = next_attr.find("a").attribute("href")
        if "catalogue" not in next:
            next = "catalogue/" + next
        next_url = base_url + next
        print(f"Next page: {next_url}")
        res = requests.get(next_url, headers=headers)
        html = res.text
        soup = LxmlSoup(html)
        parse_page(soup)


def main():
    res = requests.get(base_url, headers=headers)
    html = res.text
    soup = LxmlSoup(html)
    parse_page(soup)
    write_to_csv(results)


if __name__ == "__main__":
    main()

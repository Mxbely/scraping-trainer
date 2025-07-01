import csv

import requests
from LxmlSoup import LxmlSoup

url = "https://www.scrapethissite.com/pages/simple/"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
}

res = requests.get(url, headers=headers)
html = res.text
soup = LxmlSoup(html)

country_info = soup.find_all("div", class_="country")

for country in country_info:
    title = country.find("h3", class_="country-name").text()
    info = country.find("div", class_="country-info")
    capital = info.find("span", class_="country-capital").text()
    country_population = info.find("span", class_="country-population").text()
    country_area = info.find("span", class_="country-area").text()


with open("countries.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Capital", "Population", "Area"])
    for country in country_info:
        title = country.find("h3", class_="country-name").text()
        info = country.find("div", class_="country-info")
        capital = info.find("span", class_="country-capital").text()
        country_population = info.find("span", class_="country-population").text()
        country_area = info.find("span", class_="country-area").text()
        writer.writerow([title, capital, country_population, country_area])

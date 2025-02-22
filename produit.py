from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import sqlite3


conn = sqlite3.connect('products_data.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS products')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        product_name TEXT,
        price REAL
    )
''')

conn.commit()

def insert_data(platform, product_name, price):
    cursor.execute('INSERT INTO products (platform, product_name, price) VALUES (?, ?, ?)', (platform, product_name, price))
    conn.commit()


def scrape_amazon(search_term):
    chrome_options = Options()

    # If an error occurs during scraping, try commenting out this line of code.
    chrome_options.add_argument('--headless') 
    
    chrome_options.add_argument('--disable-gpu') 
    browser = webdriver.Chrome(service=ChromeService(), options=chrome_options)
    browser.get("https://www.amazon.fr/")

    wait = WebDriverWait(browser, 20)
    wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
    search_box = browser.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.ID, "search")))

    search_results_html = browser.page_source
    browser.quit()

    soup = BeautifulSoup(search_results_html, 'html.parser')

    adholder_regex = re.compile(r'\bAdHolder\b')
    class_regex = re.compile(r'\bsg-col-\d+-of-\d+\s.*?\bs-result-item\b')
    result_items = soup.find_all('div', class_=class_regex)

    for result_item in result_items:
        class_list = result_item.get('class', [])
        if not any(adholder_regex.search(class_name) for class_name in class_list):
            product_name_element = result_item.select_one('h2.a-size-base-plus span')
            product_name = product_name_element.text.strip() if product_name_element else "N/A"

            price_element = result_item.select_one('div[data-cy="price-recipe"] span.a-offscreen')
            price = price_element.text.strip().replace('€', '').replace(',', '.').replace('\xa0', '').replace('\u202f', '') if price_element else "N/A"
            if price and price != 'N/A':
                price_numeric = float(price)
            else:
                price_numeric = 0

            if product_name != "N/A" and price !="N/A":
                insert_data("Amazon", product_name, price_numeric)
    print("Amazon crawled success")

def scrape_ebay(search_term):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu') 
    browser = webdriver.Chrome(service=ChromeService(), options=chrome_options)
    browser.get("https://www.ebay.fr/")

    search_box = browser.find_element(By.ID, "gh-ac")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, "srp-river-results")))

    checkbox_xpath = "//input[@aria-label='Neuf']"
    neuf_checkbox = browser.find_element(By.XPATH, checkbox_xpath)

    if not neuf_checkbox.is_selected():
        neuf_checkbox.click()

    wait.until(EC.presence_of_element_located((By.ID, "srp-river-results")))

    search_results_html = browser.page_source
    browser.quit()

    soup = BeautifulSoup(search_results_html, 'html.parser')

    listings = soup.find_all('li', {'id': lambda x: x and x.startswith('item')})

    for listing in listings:
        product_name = listing.find('div', class_='s-item__info').find('a', class_='s-item__link').get_text(strip=True)

        price_span = listing.find('span', class_='s-item__price')
        product_price = price_span.get_text(strip=True) if price_span else None

        shipping_span = listing.find('span', class_='s-item__shipping')
        shipping_cost = shipping_span.get_text(strip=True) if shipping_span else "+0 EUR (livraison)"

        tax_span = listing.find('span', class_='s-item__dynamic')
        tax_info = tax_span.get_text(strip=True) if tax_span else "+ EUR0,00 de TVA"

        try:
            product_price_numeric = float(product_price.replace('EUR', '').replace('\xa0', '').replace(',', '.')) if product_price else 0
        except ValueError:
            continue
        if "livraison" not in shipping_cost:
            shipping_cost_numeric = 0
        else:
            match = re.search(r'[-+]?\d*\.\d+|\d+', shipping_cost.replace(',', '.'))
            shipping_cost_numeric = float(match[0]) if match else 0
        if "TVA" not in tax_info:
            tax_info_numeric = 0
        else:  
            match = re.search(r'[-+]?\d*\.\d+|\d+', tax_info.replace(',', '.'))
            tax_info_numeric = float(match[0]) if match else 0
        total_numeric = product_price_numeric + shipping_cost_numeric + tax_info_numeric

        insert_data("eBay", product_name, total_numeric)
    print("Ebay crawled success")

search_term = input("Produits: ")
min_price = float(input("Min prix(EUR): "))
max_price = float(input("Max prix(EUR): "))

scrape_amazon(search_term)
scrape_ebay(search_term)

cursor.execute("SELECT * FROM products WHERE price >= ? AND price <= ? ORDER BY price ASC", (min_price, max_price))
rows = cursor.fetchall()
if not rows:
    print("\nNon produit trouve")
else:
    print("\nProduit conforme")
    for row in rows:
        print(f"Plateforme: {row[1]}")
        print(f"Product Name: {row[2]}")
        print(f"Product Price: {row[3]}")
        print("------")

conn.close()
# Product Price Scraper

This Python script scrapes product prices from **Amazon France** and **eBay France** based on a user-defined search term and price range. The results are stored in a local SQLite database and filtered according to the specified price range.

## Features

- Scrape product names and prices from Amazon.fr and eBay.fr.
- Filter results based on minimum and maximum price.
- Store data in an SQLite database.
- Display matching products sorted by price.

## Requirements

- Python 3.x

### Python Libraries

Install the required Python packages using pip:

```bash
pip install selenium beautifulsoup4
```

## Usage

1. **Run the script:**

```bash
python3 produit.py
```

2. **Enter inputs when prompted:**

- `Produits:` → Enter the product you want to search (e.g., `iPhone`).
- `Min prix(EUR):` → Enter the minimum price (e.g., `100`).
- `Max prix(EUR):` → Enter the maximum price (e.g., `1000`).

3. **View results:**

The script will display products from Amazon and eBay within the specified price range, sorted by price.

## Database

- The script creates a SQLite database named `products_data.db`.
- Product data is stored in the `products` table with the following fields:
  - `id`: Primary key
  - `platform`: Source platform (Amazon or eBay)
  - `product_name`: Name of the product
  - `price`: Product price (in EUR)

## Notes

- The script uses a **headless Chrome browser** for scraping.
- **Web page structure changes** on Amazon or eBay may affect the scraper’s functionality.
- Ensure your **internet connection** is stable while running the script.

## License

This project is for educational purposes only. Please respect the terms of service of the websites you scrape.


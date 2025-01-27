# Google Maps Data Scraper 📍

![Google Maps Scraper](https://img.shields.io/badge/Google%20Maps-Scraper-blue?style=for-the-badge&logo=googlemaps)

Google Maps Data Scraper is a powerful Python-based tool developed by [Rituraj200000](https://github.com/Rituraj200000) to extract business details like names, ratings, reviews, addresses, phone numbers, websites, and more directly from Google Maps. This project is designed to help marketers, researchers, and data enthusiasts collect accurate and structured data efficiently.

---

## 🌟 Features
- **High-Speed Scraping**: Extract critical business data from Google Maps in real time.
- **Duplicate Data Avoidance**: Automatically skips duplicates to maintain clean datasets.
- **Email Extraction**: Scrapes emails from linked websites asynchronously for enhanced outreach capabilities.
- **Custom Search**: Input a business type and location (e.g., "restaurants in New York") or provide a Google Maps URL.
- **SEO-Ready Data**: Outputs CSV files optimized for digital marketing, research, or data analytics.
- **Error Resilience**: Built with robust error handling for uninterrupted scraping sessions.

---

## 🔧 Technologies Used
- **Python**: Core programming language.
- **Selenium**: Browser automation for Google Maps interaction.
- **Pandas**: Data handling and CSV file management.
- **Httpx**: Asynchronous HTTP client for email scraping.
- **Regex**: Pattern matching to extract emails accurately.
- **Asyncio**: Ensures fast and efficient execution.

---

## 🛠️ Installation
### Prerequisites
1. Install **Python 3.8+** on your system.
2. Install **Google Chrome** and **ChromeDriver** (ensure the ChromeDriver version matches your Chrome version).

### Install the Dependencies:
```bash
pip install -r requirements.txt
```

### Update ChromeDriver if Needed:
- Visit [ChromeDriver Download Page](https://sites.google.com/chromium.org/driver/) and download the appropriate version.
- Replace the existing ChromeDriver in your system path with the updated one.

---

## 🚀 Running the Scraper
### **Google Maps Scraper**:
```bash
python gmaps_scraper.py
```
- Choose to input a search query (e.g., `"hotels in Los Angeles"`) or a direct Google Maps URL.

### **Email Scraper**:
```bash
python email_scraper.py
```
- Provide the `gmaps_data.csv` file to extract emails from listed websites.

### Find Your Results in the CSV Files:
- `gmaps_data.csv`: Contains the extracted business data from Google Maps.
- `gmaps_data_with_emails.csv`: Enhanced data with scraped email addresses.

---

## 🔍 Example Use Case
```bash
python gmaps_scraper.py
# Input: "cafes in San Francisco"
# Output: Detailed list of cafes with ratings, reviews, addresses, and more!
```

---

## 💡 Use Cases
- **SEO and Digital Marketing**: Build business directories and targeted email lists.
- **Market Research**: Analyze competitors and understand market dynamics.
- **Data Analytics**: Feed structured data into analytics tools or AI models.

---

## ⚠️ Disclaimer
This tool is for **educational purposes only**. Scraping Google Maps may violate its [Terms of Service](https://www.google.com/intl/en/policies/terms/). Use responsibly and comply with local laws and regulations.

---

## 🤝 Contributing
Contributions are welcome! Follow these steps to contribute:
1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/my-new-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/my-new-feature`.
5. Open a Pull Request.

---

## ⭐ Support
If you find this project helpful, please consider giving it a ⭐ on [GitHub](https://github.com/Rituraj200000/googlemapscraper). Your support helps us grow and improve!

---

## 🔗 Connect with Me
- **GitHub**: [Rituraj200000](https://github.com/Rituraj200000)

---

### Tags
`google-maps-scraper` `python-web-scraper` `business-data-extractor` `selenium-scraper` `email-scraper` `data-collection` `seo-marketing`

---

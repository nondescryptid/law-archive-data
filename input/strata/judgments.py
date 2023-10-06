import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import json 
"""
Schema: 
title: 
date: "03 JAN 2023" 
pdf-url:
pdf-content: 
"""
BASE_URL = "https://www.stratatb.gov.sg"
URL = "https://www.stratatb.gov.sg/news-and-judgments/judgments/"

judgment_arr = []
# Get URL contents \
def get_data(url): 
    return requests.get(url).text

def extract_all_pages(url):
    """
    :param url - URL of the target PDF 
    """
    res = requests.get(url)
    pdf_text = []
    with io.BytesIO(res.content) as data:
        reader = PdfReader(data)
        num_pages = len(reader.pages)
        for page in range(num_pages):
            page_content = reader.pages[page].extract_text()
            pdf_text.append(page_content)
    # Joining at the end is preferred over repeatedly concatenating strings
    return ''.join(pdf_text)

# def parse_judgments()
html_text = get_data(URL)
soup = BeautifulSoup(html_text, 'html.parser')
judgments = soup.find_all("div", class_="resource-card-element")

for judgment in judgments: 
    judgment_dict = {}
    title = judgment.select("h5")[0].get_text().replace('â\x80\x93', '-').strip("...")
    # Concatenation with base URL is needed because the site uses relative links
    judgment_dict["title"] = title
    pdf_url = BASE_URL + judgment.find("a", href=True)["href"]
    judgment_dict["pdf-url"] = pdf_url
    date = judgment.find("small", class_="is-inline").get_text()
    # Get judgment PDF 
    judgment_dict["date"] = date
    try: 
        pdf_content = extract_all_pages(pdf_url)
    except: 
        pdf_content = "Could not extract PDF"
    judgment_dict["pdf-content"] = pdf_content
    judgment_arr.append(judgment_dict)


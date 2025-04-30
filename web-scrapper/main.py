from playwright.sync_api import sync_playwright
import json
from datetime import datetime as dt
from pathlib import Path
import requests
import base64
import os

def encode_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
    return encoded_string

def get_file_size(file_path):
    return os.path.getsize(file_path)

def process_pdf(file_path):
    file_size = get_file_size(file_path)

    size_limit = 5 * 1024 * 1024  # 5 MB

    if file_size > size_limit:
        print("PDF is too large to base64 encode. Using the URL instead.")
        return file_path
    else:
        encoded_pdf = encode_pdf(file_path)
        print("PDF encoded successfully.")
        return encoded_pdf

FILE_PATH = "NeoCity-Data/Neocity_Academy.json"
PDF_PATH = "NeoCity-Data/School_Profile_NEOC.pdf"

os.makedirs(os.path.dirname("NeoCity-Data/"), exist_ok=True)

if Path(FILE_PATH).exists():
    with open(FILE_PATH, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
else:   
    data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.osceolaschools.net/neoc")

    page.get_by_role("link", name="About").hover()

    #Mission School and Facts
    page.locator("#navs-835").click()
    for i in range(2):
        inner_html = page.locator(".Secondary_Color_Box").nth(i).inner_html()
        parts = inner_html.split("<br>")
        statement_t = parts[0].split("<strong>")[-1].split("</strong>")[0]
        statement = parts[1].strip()

        new_entry = {
            "source": {
                "site": "NeoCity Academy",
                "url": "https://www.osceolaschools.net/neoc",  # replace with actual page URL
                "scraped_at": dt.now().isoformat()
            },
            "content": {
                "type": "Mission & Vision Statement",
                "title": statement_t,
                "text": statement
            }
        }

        data.append(new_entry)

    page.get_by_role("link", name="School Profile", exact=True).click()
    schoolProfile_pdf = page.url

    response = requests.get(schoolProfile_pdf)
    if Path(PDF_PATH).exists():
        os.remove(PDF_PATH)
        with open(PDF_PATH, "wb") as f:
            f.write(response.content)
    else:
        with open(PDF_PATH, "wb") as f:
            f.write(response.content)

    new_entry = {
        "source": {
            "site": "NeoCity Academy",
            "url": "https://www.osceolaschools.net/neoc",
            "scraped_at": dt.now().isoformat()
        },
        "content": [
            {
                "type": "school_profile_pdf",
                "title": "School Profile PDF",
                "pdf_url": "https://www.osceolaschools.net/cms/lib/FL50000609/Centricity/Domain/835/2024-25%20School%20Profile%20NEOC.pdf",
                "pdf_base64": process_pdf(PDF_PATH)
            }
        ]
    }

    data.append(new_entry)

    page.goto("https://www.osceolaschools.net/domain/835")

    page.get_by_role("link", name="Fast Facts", exact=True).click()

    items = []
    for i in range(4):
        fast_facts_list = page.locator(".ui-article-description span span li").nth(i)
        fast_facts_text = fast_facts_list.text_content().strip()

        link = None

        a = fast_facts_list.locator("a")
        if a.count() > 0:
            link = a.get_attribute("href")
            try:
                link = fast_facts_list.locator("a").get_attribute("href")
            except:
                pass
        else:
            pass

        if link:
            fast_facts_text += f" (Source: {link})"

        items.append(fast_facts_text)

    new_entry = {
        "source": {
            "site": "NeoCity Academy",
            "url": "https://www.osceolaschools.net/neoc",
            "scraped_at": dt.now().isoformat()
        },
        "content": {
            "type": "Fast Facts",
            "title": "Fast Facts",
            "text": items
        }
    }

    #AI Pathway
    page.get_by_role("link", name="Academics and Clubs").hover()

    #Ai Department
    page.locator("#navs-5563").click()
    ai_heading = page.locator(".ui-article-description span span h2").nth(0).text_content()
    ai_paragraph = page.locator(".ui-article-description span span p").nth(0).text_content()

    ai_classes = []
    count = 3

    for i in range(2):
        page.locator(".content-accordion-toggle").nth(i).click()

        for j in range(count):
            ai_class_name = page.locator(".ui-article.active span").nth(j).text_content()
            ai_class_desc = page.locator(".ui-article.active p").nth(j).text_content()

            ai_classes.append({
                "class": ai_class_name,
                "description": ai_class_desc
            })

        count -= 1
        page.locator(".content-accordion-toggle").nth(i).click()

    new_entry = {
        "source": {
            "site": "NeoCity Academy",
            "url": "https://www.osceolaschools.net/neoc",
            "scraped_at": dt.now().isoformat()
        },
        "content": {
            "type": "AI Pathway",
            "title": ai_heading,
            "pathway_description": ai_paragraph,
            "classes": ai_classes
        }
    }

    data.append(new_entry)
    
    with open(FILE_PATH, "a", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    input("Press Enter to close...")
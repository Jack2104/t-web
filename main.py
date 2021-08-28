import os
import requests
from rich.console import Console
from bs4 import BeautifulSoup

TAG_STYLES = {
    "p": "%s\n\n",
    "h1": "[bold underline]## %s ##[/]\n",
    "h2": "[bold underline]%s[/]\n",
    "h3": "[bold]%s[/]\n",
    "h4": "[italic underline]%s[/]\n",
    "h5": "[italic]%s[/]\n",
    "h6": "%s\n",
    "aside": "[dim]%s[/]\n\n",
    "li": " [yellow]• %s[/]\n\n",
    "code": "%s\n\n",
    "a": "[#3b9dff underline](%i) %s[/]",
}
console = Console(highlight=False)

page_links = []


def display_page(url):
    global page_links

    def parse_tag(tag):
        if tag.name in TAG_STYLES:
            if tag.name == "a":
                page_links.append(tag.get("href"))
                return TAG_STYLES["a"] % (len(page_links), tag.text) + "\n\n"

            return TAG_STYLES[tag.name] % tag.text

        return ""

    os.system("clear")

    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "lxml")
    except:
        print("[red]This page cannot be displayed.[/]")
        return

    body = soup.body  # Every website should have this tag
    page_content = ""

    for tag in body.find_all():
        try:
            page_content += parse_tag(tag)
        except:
            pass

    console.print(page_content)


if __name__ == "__main__":
    os.system("clear")

    query = input("Search: ")
    search_terms = query.split()

    # For now, only supports urls (not organic searches)
    url = query.join(search_terms)

    display_page(url)

# Test URL 1: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-down
# Test URL 2: http://motherfuckingwebsite.com
# Test URL 3: https://perfectmotherfuckingwebsite.com
# Test URL 4: http://txti.es/dj8g2

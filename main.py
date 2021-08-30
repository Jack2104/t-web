import os
import requests
from rich.console import Console
from bs4 import BeautifulSoup

list_tags = ["li", "dt", "dd"]
TAG_STYLES = {
    "p": "%s\n\n",
    "h1": "[#ffffff bold underline]## %s ##[/]\n",
    "h2": "[#ffffff bold underline]%s[/]\n",
    "h3": "[#ffffff bold]%s[/]\n",
    "h4": "[#ffffff italic underline]%s[/]\n",
    "h5": "[#ffffff italic]%s[/]\n",
    "h6": "%s\n",
    "aside": "[dim]%s[/]\n\n",
    "li": " [yellow]• %s[/]\n",
    "code": "%s\n\n",
    "a": "[#3b9dff underline](%i) %s[/]",
}
console = Console(highlight=False)

page_links = []


def display_page(url):
    global page_links

    def parse_tag(tag):
        # This will occur if the link is standalone (i.e. not in-line)
        if tag.name == "a":
            page_links.append(tag.get("href"))
            return TAG_STYLES["a"] % (len(page_links), tag.text) + "\n\n"

        tag_content = ""
        hypertext = []
        # We only want the top-level children
        children = tag.find_all(recusive=False)

        # Get all of the in-line links (<a> tags)
        if tag.name in TAG_STYLES and children:
            # tag.find_all is used because we want this to get every child using recursive=True
            for child_tag in tag.find_all():
                if child_tag.name == "a":
                    hypertext.append(child_tag.text)
                    page_links.append(child_tag.get("href"))

        if tag.name in TAG_STYLES:
            tag_content = TAG_STYLES[tag.name] % tag.text

            # Loop through every in-line link, re-format it, then add it back in to the content
            for index in range(len(hypertext)):
                # Get the number of the current link (note: not the index in page_links)
                link_number = len(page_links) - len(hypertext) + index + 1
                new_link = TAG_STYLES["a"] % (link_number, hypertext[index])

                tag_content = tag_content.replace(hypertext[index], new_link)
        elif children:
            # Recursively call this function to parse all of the children
            for index in range(len(children)):
                child_tag = children[index]
                tag_content += parse_tag(child_tag)

                # Add two newlines if the child is the final list item
                if child_tag.name in list_tags and index == len(children) - 1:
                    tag_content += "\n"

        return tag_content

    os.system("clear")

    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "lxml")
    except:
        print("[red]This page cannot be displayed.[/]")
        return

    body = soup.body  # Every website should have this tag
    page_content = ""

    for tag in body.find_all(recursive=False):
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
# Test URL 4: http://txti.es/dj8g2 (edit with code fml13)

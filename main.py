import json
import os
import requests
from rich.console import Console
import sys

from abc import ABC, abstractmethod
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
history = []


class Page(ABC):  # Create an abstract class
    @abstractmethod
    def __init__(self):
        self.page_links = []

    @abstractmethod
    def get_page_content(self):
        pass

    def display_page(self):
        os.system("clear")

        page_content = self.get_page_content()
        console.print(page_content)


class WebPage(Page):
    def __init__(self, url):
        super().__init__()

        self.url = url

        if len(history) == 0 or history[-1] != url:
            history.append(url)

    def parse_tag(self, tag):
        # This will occur if the link is standalone (i.e. not in-line)
        if tag.name == "a":
            self.page_links.append(tag.get("href"))
            return TAG_STYLES["a"] % (len(self.page_links), tag.text) + "\n\n"

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
                    self.page_links.append(child_tag.get("href"))

        if tag.name in TAG_STYLES:
            tag_content = TAG_STYLES[tag.name] % tag.text

            # Loop through every in-line link, re-format it, then add it back in to the content
            for index in range(len(hypertext)):
                # Get the number of the current link (note: not the index in page_links)
                link_number = len(self.page_links) - len(hypertext) + index + 1
                new_link = TAG_STYLES["a"] % (link_number, hypertext[index])

                tag_content = tag_content.replace(hypertext[index], new_link)
        elif children:
            # Recursively call this function to parse all of the children
            for index in range(len(children)):
                child_tag = children[index]
                tag_content += self.parse_tag(child_tag)

                # Add two newlines if the child is the final list item
                if child_tag.name in list_tags and index == len(children) - 1:
                    tag_content += "\n"

        return tag_content

    def get_page_content(self):
        try:
            request = requests.get(self.url)
            soup = BeautifulSoup(request.text, "lxml")
        except:
            return "[red]This page cannot be displayed.[/]"

        body = soup.body  # Every website should have this tag
        content = ""

        for tag in body.find_all(recursive=False):
            try:
                content += self.parse_tag(tag)
            except:
                pass

        return content


class BookmarksPage(Page):
    def __init__(self):
        super().__init__()

        for bookmark in bookmarks:
            self.page_links = bookmark["url"]

    def format_bookmark(self, bookmark, bookmark_number):
        return f"[green]({bookmark_number}) {bookmark['name']}[/] [#3b9dff]\n{bookmark['url']}[/]"

    def get_page_content(self):
        content = TAG_STYLES["h1"] % "Bookmarks"

        for index in range(len(bookmarks)):
            bookmark = bookmarks[index]
            content += self.format_bookmark(bookmark, index + 1)

            if index < len(bookmarks) - 1:
                content += "\n\n"

        if len(bookmarks) == 0:
            content = "[green]You don't have any bookmarks yet! Try adding one with the -nb command[/]"

        return content


class HistoryPage(Page):
    def __init__(self):
        super().__init__()
        self.page_links = history

    def get_page_content(self):
        content = TAG_STYLES["h1"] % "History"

        for index in range(len(history)):
            link = history[index]
            content += f"[#3b9dff]({index + 1}) {link}[/]"

            if index < len(history) - 1:
                content += "\n\n"

        return content


def get_bookmarks():
    if not os.path.exists("./bookmarks.json"):
        with open("bookmarks.json", "w+") as json_file:
            json.dump([], json_file)
            return []

    with open("bookmarks.json") as json_file:
        return json.load(json_file)


if __name__ == "__main__":
    bookmarks = get_bookmarks()

    os.system("clear")

    # Create an event loop, of sorts
    while True:
        query = input("Search: ")
        search_terms = query.split()

        if search_terms[0] == "-nb" and len(search_terms) >= 3:
            bookmark_url = search_terms[1]
            bookmark_name = " ".join(search_terms[2:])

            bookmark = {
                "url": bookmark_url,
                "name": bookmark_name
            }

            bookmarks.append(bookmark)

            with open("bookmarks.json", "w+") as json_file:
                json.dump(bookmarks, json_file)

        elif search_terms[0] == "-sb" and len(search_terms) == 1:
            bookmarks_page = BookmarksPage()
            bookmarks_page.display_page()
            print()

        elif search_terms[0] == "-sh" and len(search_terms) == 1:
            history_page = HistoryPage()
            history_page.display_page()
            print()

        elif search_terms[0] == "-q" and len(search_terms) == 1:
            sys.exit()

        else:
            # For now, only supports urls (not organic searches)
            url = query.join(search_terms)

            web_page = WebPage(url)
            web_page.display_page()
            print()

# Test URL 1: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-down
# Test URL 2: http://motherfuckingwebsite.com
# Test URL 3: https://perfectmotherfuckingwebsite.com
# Test URL 4: http://txti.es/dj8g2 (edit with code fml13)

import logging
import re
from typing import Optional, Union

import requests
from bs4 import BeautifulSoup, element, PageElement
from steamship import DocTag, TagKind, SteamshipError
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag

WIKIPEDIA_URL_REGEX = "https:\/\/[A-Za-z]+\.wikipedia\.org\/wiki\/.+"


def validate_wikipedia_url(url: Optional[str]) -> str:
    if url is None:
        raise SteamshipError(
            message=f"Missing the `url` field in your FileImportPluginInput request.")

    if not re.match(WIKIPEDIA_URL_REGEX, url.lower().strip()):
        raise SteamshipError(
            message=f"The provided `url` field did not appear to match the format https://LANGUAGE.wikipedia.org/wiki/TOPIC. Got url: {url}")

    return url


def fetch_url(url: str) -> str:
    page = requests.get(url)
    return page.content.decode("utf-8")


def element_to_block(elem: Union[PageElement, BeautifulSoup]) -> Optional[Block.CreateRequest]:
    tag_name = DocTag.from_html_tag(elem.name)
    if tag_name is None:
        return None

    # Special case for Wikipedia: Bail out if we're in a Wikipedia Headline
    headline = elem.select_one('.mw-headline')
    if headline:
        text = headline.getText()
        return Block.CreateRequest(
            text=text,
            tags=[
                Tag.CreateRequest(kind=TagKind.doc, name=tag_name)
            ]
        )

    value = None
    if tag_name == DocTag.link:
        try:
            value = {"href": elem["href"]}
        except:
            pass

    ret = Block.CreateRequest(text = "", tags = [
        Tag.CreateRequest(kind=TagKind.doc, name=tag_name, value=value)
    ])

    # Anything else we have to pursue a recursive strategy, piecing together the text while we tag
    # interior elements such as <B>, <A>, <SPAN>, <UL><LI><UL><LI>.., etc..
    for child in elem.children:
        if child is not None:
            # It's a string; append to the running string
            if type(child) == element.NavigableString:
                ret.text += child.text
            # It's an element, we need to recurse in!
            else:
                block = element_to_block(child)
                if block is None or not block.text.strip():
                    continue
                offset = len(ret.text)
                for tag in block.tags:
                    if tag.startIdx is not None:
                        tag.startIdx += offset
                    else:
                        tag.startIdx = offset

                    if tag.endIdx is not None:
                        tag.endIdx += offset
                    else:
                        tag.endIdx = offset + len(block.text)
                    ret.tags.append(tag)
                ret.text += block.text

    return ret


def parse_html(html: str) -> File.CreateRequest:
    soup = BeautifulSoup(html, 'html.parser')

    blocks = []

    # Get the header
    try:
        heading = soup.find(id='firstHeading')
        blocks.append(element_to_block(heading))
    except:
        logging.error("Unable to get #firstHeading object")

    # Get each paragraph
    try:
        main_body = soup.select_one(".mw-parser-output")
        for child in main_body:
            if child and hasattr(child, "name"):
                name = getattr(child, "name")
                if name and name.lower() in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'ul']:
                    blocks.append(element_to_block(child))
    except Exception as e:
        logging.error("Unable to iterate over `.mw-parser-output p` list")
        logging.error(e)

    blocks = list(filter(lambda block: block is not None, blocks))

    return File.CreateRequest(
        blocks=blocks
    )

def get_text(block: Block.CreateRequest, tag: Tag.CreateRequest) -> str:
    startIdx = tag.startIdx or 0
    endIdx = tag.endIdx or len(block.text)
    return block.text[startIdx:endIdx]
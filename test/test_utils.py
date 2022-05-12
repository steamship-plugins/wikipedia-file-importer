import pytest
from steamship import DocTag

__copyright__ = "Steamship"
__license__ = "MIT"

from src.utils import validate_wikipedia_url, fetch_url, element_to_block, get_text
from bs4 import BeautifulSoup


def test_wikipedia_urls():
    goods = [
        "https://en.wikipedia.org/wiki/Ocelot",
        "https://en.wikipedia.org/wiki/Honey_badger",
        "https://en.wikipedia.org/wiki/Honey_badger/unlikely_subpage?has_care=no",
        "https://en.wikipedia.org/wiki/Honey_badger?has_care=no",
        "https://zh.wikipedia.org/wiki/豹貓",
    ]
    for good in goods:
        assert (good == validate_wikipedia_url(good))

    bads = [
        "http://en.wikipedia.org/wiki/Ocelot",
        "https://google.com/wiki/Where_Is_Google_Reader",
        "Slytherin"
    ]

    for bad in bads:
        with pytest.raises(Exception) as e_info:
            validate_wikipedia_url(bad)


def test_fetch_url():
    url = "https://en.wikipedia.org/wiki/Ocelot"
    html = fetch_url(url)
    assert ("</html>" in html)


def test_parse_header():
    text = "Hi There"
    html = BeautifulSoup(f"""<h1>{text}</h1>""", 'html.parser').select_one('h1')
    block = element_to_block(html)
    assert (block.text == text)
    assert (block.tags[0].name == DocTag.h1)


def test_parse_para():
    text = "Hi There"
    html = BeautifulSoup(f"""<p>{text}</p>""", 'html.parser').select_one('p')
    block = element_to_block(html)
    assert (block.text == text)
    assert (block.tags[0].name == DocTag.paragraph)


def test_parse_para_with_link():
    html = BeautifulSoup(f"""<p>This is a <a href="#">link</a></p>""", 'html.parser').select_one('p')
    block = element_to_block(html)
    assert (block.text == "This is a link")
    assert (len(block.tags) == 2)
    # The first is the paragraph
    assert (block.tags[0].name == DocTag.paragraph)
    assert (block.tags[0].startIdx == None)
    assert (block.tags[0].endIdx == None)
    # The second is the link
    assert (block.tags[1].name == DocTag.link)
    assert (block.tags[1].startIdx == 10)
    assert (block.tags[1].endIdx == 14)
    assert (block.tags[1].value == {"href": "#"})
    assert (get_text(block, block.tags[1]) == "link")


def test_parse_para_with_b_and_i():
    html = BeautifulSoup(f"""<p>This is <b>bold and <i>italic</i></b>.</p>""", 'html.parser').select_one('p')
    block = element_to_block(html)
    assert (block.text == "This is bold and italic.")
    assert (len(block.tags) == 3)
    # The first is the paragraph
    assert (block.tags[0].name == DocTag.paragraph)
    assert (block.tags[0].startIdx == None)
    assert (block.tags[0].endIdx == None)
    # The second is the bold
    assert (block.tags[1].name == DocTag.strong)
    assert (get_text(block, block.tags[1]) == "bold and italic")
    # The third is the italic
    assert (block.tags[2].name == DocTag.emph)
    assert (get_text(block, block.tags[2]) == "italic")


def test_parse_ul_li():
    html = BeautifulSoup(f"""<p>I have a list: <ul><li>one</li> <li>two</li></ul>. That's it..</p>""",
                         'html.parser').select_one('p')
    block = element_to_block(html)
    assert (block.text == "I have a list: one two. That's it..")
    assert (len(block.tags) == 4)

    assert (block.tags[0].name == DocTag.paragraph)
    assert (block.tags[0].startIdx == None)
    assert (block.tags[0].endIdx == None)

    assert (block.tags[1].name == DocTag.list)
    assert (get_text(block, block.tags[1]) == "one two")

    assert (block.tags[2].name == DocTag.list_item)
    assert (get_text(block, block.tags[2]) == "one")

    assert (block.tags[3].name == DocTag.list_item)
    assert (get_text(block, block.tags[3]) == "two")


def test_parse_ul_li():
    html = BeautifulSoup(
        f"""<p>I have a list: <ul><li>one <ul>Inner: <li>Thing</li></ul></li> <li>two</li></ul>. That's it..</p>""",
        'html.parser').select_one('p')
    block = element_to_block(html)
    assert (block.text == "I have a list: one Inner: Thing two. That's it..")
    assert (len(block.tags) == 6)

    assert (block.tags[0].name == DocTag.paragraph)
    assert (block.tags[0].startIdx == None)
    assert (block.tags[0].endIdx == None)

    assert (block.tags[1].name == DocTag.list)
    assert (get_text(block, block.tags[1]) == "one Inner: Thing two")

    assert (block.tags[2].name == DocTag.list_item)
    assert (get_text(block, block.tags[2]) == "one Inner: Thing")

    assert (block.tags[3].name == DocTag.list)
    assert (get_text(block, block.tags[3]) == "Inner: Thing")

    assert (block.tags[4].name == DocTag.list_item)
    assert (get_text(block, block.tags[4]) == "Thing")

    assert (block.tags[5].name == DocTag.list_item)
    assert (get_text(block, block.tags[5]) == "two")

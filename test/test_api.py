import base64
import json
import os
import logging

from steamship import MimeTypes, File, DocTag

__copyright__ = "Steamship"
__license__ = "MIT"

from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput

from steamship.plugin.service import PluginRequest

from src.api import WikipediaFileImporterPlugin
from src.utils import parse_html, get_text


def _base64_decode(base64_message: str) -> str:
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('utf8')


def _read_test_file(filename: str) -> str:
    folder = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(folder, '..', 'test_data', filename), 'r') as f:
        return f.read()


def test_saved_marmot():
    html = _read_test_file('marmot.html')
    file = parse_html(html)
    assert (file.blocks is not None)
    assert (len(file.blocks) == 26)

    # This is just a mini test that we're grabbing links we know ought to be there
    has_prairie_dog_link = False
    for block in file.blocks:
        for tag in block.tags:
            if get_text(block, tag) == "prairie dog":
                has_prairie_dog_link = True
    assert(has_prairie_dog_link == True)


def test_live_marmot():
    importer = WikipediaFileImporterPlugin()
    request = PluginRequest(data=FileImportPluginInput(url="https://en.wikipedia.org/wiki/Ocelot"))
    response = importer.run(request)

    assert(response.data.mimeType == MimeTypes.STEAMSHIP_BLOCK_JSON)
    decoded = _base64_decode(response.data.data)
    file_create_request_dict = json.loads(decoded)
    cr = File.CreateRequest.from_dict(file_create_request_dict)

    assert (cr.blocks is not None)
    has_ocelot_title = False
    for block in cr.blocks:
        for tag in block.tags:
            if tag.name == DocTag.h1:
                print(tag)
                if get_text(block, tag) == "Ocelot":
                    has_ocelot_title = True
    assert(has_ocelot_title == True)


"""Wikipedia File Importer Plugin.
"""

from steamship import MimeTypes
from steamship.app import App, Response, post, create_handler
from steamship.base.error import SteamshipError
from steamship.plugin.file_importer import FileImporter
from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest

from src.utils import validate_wikipedia_url, fetch_url, parse_html

WIKIPEDIA_URL_REGEX = "https:\/\/[A-Za-z]+\.wikipedia\.org\/wiki\/.+"


class WikipediaFileImporterPlugin(FileImporter, App):
    """"Imports Wikipedia pages as Steamship Block Format."""

    def run(self, request: PluginRequest[FileImportPluginInput]) -> Response[RawDataPluginOutput]:
        """Performs the file import or returns a detailed error explaining what went wrong."""

        # Check to make sure the user provided a URL to identify what it is they want imported.
        if request.data is None:
            raise SteamshipError(
                message=f"Missing the wrapped FileImportPluginInput request object. Got request: {request}")

        url = validate_wikipedia_url(request.data.url)
        html = fetch_url(url)
        file = parse_html(html)

        return Response(data=RawDataPluginOutput(
            json=file,
            mime_type=MimeTypes.STEAMSHIP_BLOCK_JSON
        ))

    @post('/import_file')
    def import_file(self, **kwargs) -> Response[RawDataPluginOutput]:
        """HTTP endpoint for our plugin.

        When deployed and instantiated in a Space, this endpoint will be served at:

        https://{username}.steamship.run/{space_id}/{plugin_instance_id}/import_file

        When adapting this template, you can almost always leave the below code unchanged.
        """
        request = FileImporter.parse_request(request=kwargs)
        return self.run(request)


handler = create_handler(WikipediaFileImporterPlugin)

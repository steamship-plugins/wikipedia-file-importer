# Steamship Wikipedia File Importer Plugin

This project contains a File Importer Plugin that will fetch a WikiPedia page by URL and return that page in Steamship Block Format.

## Usage

This plugin is auto-deployed to Steamship and available via handle: `wikipedia-file-importer`

Here is a complete example of using it:

```
from steamship import Steamship
from steamship.data.file import File
from steamship.data.plugin_instance import PluginInstance

# Create your ~/steamship.json credential file by installing the Steamship CLI and running `ship login`
client = Steamship()   

# Create an instance of this plugin. 
plugin_instance = PluginInstance.create(client, plugin_handle="wikipedia-file-importer")

# Import a new file into Steamship using this importer
url = "https://en.wikipedia.org/wiki/Marmot"
task = File.create(client=client, url=url, plugin_instance=plugin_instance)

```

## Tagging Strategy

This importer uses knowledge of the Wikipedia page structure to extract Steamship Block Format content. It includes
the title and the body of the page. Each major paragraph or list in the body is returned as a new block. Within
those blocks, each link, bold/italic/underline span element, sub-list, and the broader block type are tagged.

Whereas the input HTML elements are **nested**, the output Steamship Block structure is **linear**, with **overlapping tags**. 
The nesting of the HTML could be recovered, if one wished, by reasoning about the overlapping tags.

The following diagram illustrates this approach to tagging:

![Diagram of Tagging Strategy](doc/tagging-strategy.png)

## Developing

We recommend using a Python virtual environments for development.
To set one up, run the following command from this directory:

**Your first time**, create the virtual environment with:

```bash
python3 -m venv .venv
```

**Each time**, activate your virtual environment with:

```bash
source .venv/bin/activate
```

**Your first time**, install the required dependencies with:

```bash
python -m pip install -r requirements.dev.txt
python -m pip install -r requirements.txt
```

### Code Structure

All the code for this plugin is located in the `src/api.py` file:

* The `FileImporterPlugin` class
* The `/import_file` endpoint

### Testing

Tests are located in the `test/test_api.py` file. You can run them with:

```bash
pytest
```

We have provided sample data in the `test_data/` folder.

### Deploying

Deploy this project to Steamship as a new plugin of your own with:

```bash
ship deploy
```

### Sharing

Please share what you've built with hello@steamship.com!

We would love take a look, hear your suggestions, help where we can, and share what you've made with the community.
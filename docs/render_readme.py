# import argparse
import json
import logging
import os
import re

from jinja2 import Environment, FileSystemLoader
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import GoogleProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_config(config_file: str) -> dict:
    # TODO: Resolve paths here
    with open(config_file, mode="r", encoding="utf-8") as file:
        return json.loads(file.read())


def render_library_contents(
    packages_dir: str,
    packages: list[str],
    templates_dir: str,
    rendered_filename: str,
) -> None:
    """Render the Documentation for Python Modules to a File

    Args:
        packages_dir (str): Base directory to search for modules.
        packages (list[str]): Packages to search for modules.
        templates_dir (str): Directory containing the template files.
        rendered_filename (str): File to render the library contents to.
    """
    output_path = os.path.join(templates_dir, rendered_filename)
    session = PydocMarkdown(
        loaders=[
            PythonLoader(packages=packages, encoding="utf-8"),
        ],
        processors=[
            FilterProcessor(
                expression="not name.startswith('_') and default()",
                documented_only=True,
                exclude_private=True,
                exclude_special=True,
                do_not_filter_modules=True,
                skip_empty_modules=True,
            ),
            GoogleProcessor(),
            CrossrefProcessor(),
        ],
        renderer=MarkdownRenderer(
            filename=output_path,
            encoding="utf-8",
            code_headers=True,
            add_method_class_prefix=True,
            add_member_class_prefix=True,
            signature_code_block=True,
            render_typehint_in_data_header=True,
            toc_maxdepth=3,
        ),
    )
    context = Context(packages_dir)
    session.init(context)
    session.ensure_initialized()
    modules = session.load_modules()
    session.process(modules)
    # session.run_hooks("post-render")
    session.render(modules, run_hooks=True)

    # TODO: Fix these "hacks"

    # Read the original
    with open(output_path, mode="r", encoding="utf-8") as file:
        rendered_contents = file.read()

    # Fix some missing highlighting in the `**Returns**` sections
    rendered_contents = re.sub(
        r"\*\*Returns\*\*:\n\n  ([a-zA-Z0-9_, \|\[\]]+): ",
        r"**Returns**:\n\n- `\1` - ",
        rendered_contents,
    )

    # Condense 3 or more newlines to 2
    rendered_contents = re.sub(r"\n{3,}", "\n\n", rendered_contents)

    # Write the corrected contents
    with open(output_path, mode="w", encoding="utf-8") as file:
        file.write(rendered_contents)


def main() -> None:  # config_file: str, template_file: str, output_file: str, replace: bool) -> None:
    # Load the config
    with open("config.json", mode="r", encoding="utf-8") as file:
        config = json.loads(file.read())

    # Generate the library documentation
    render_library_contents(
        packages_dir=config["packages_dir"],
        packages=config["packages"],
        templates_dir=config["templates_dir"],
        rendered_filename=config["rendered_filename"],
    )

    # Render the markdown readme
    # TODO: Move this to a separate function?
    loader = FileSystemLoader(config["templates_dir"])
    environment = Environment(loader=loader, auto_reload=False)
    template = environment.get_template(config["main_template"])
    rendered = template.render(**config["template_data"])
    with open(config["output_file"], mode="w", encoding="utf-8") as file:
        file.write(rendered)


if __name__ == "__main__":
    # TODO: Implement argparse here
    main()

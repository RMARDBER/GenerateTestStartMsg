import os
import re
import sys


def get_app_dir():
    """Return the folder that contains the script or packaged executable."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    """Return the folder that contains bundled app resources."""
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS

        internal_dir = os.path.join(os.path.dirname(sys.executable), "_internal")
        if os.path.isdir(internal_dir):
            return internal_dir

        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_dir()
RESOURCE_DIR = get_resource_dir()
OUTPUT_DIR = os.path.join(APP_DIR, "outputs")


def first_existing_path(candidates):
    """Return the first existing path from candidates, or the first candidate."""
    for path in candidates:
        if os.path.exists(path):
            return path

    return candidates[0]


MAPPING_PATH = first_existing_path(
    [
        os.path.join(APP_DIR, "inputs", "mappings.txt"),
        os.path.join(APP_DIR, "_internal", "inputs", "mappings.txt"),
        os.path.join(RESOURCE_DIR, "inputs", "mappings.txt"),
        os.path.join(APP_DIR, "mappings.txt"),
        os.path.join(APP_DIR, "_internal", "mappings.txt"),
        os.path.join(RESOURCE_DIR, "mappings.txt"),
    ]
)

TEMPLATES_DIR = first_existing_path(
    [
        os.path.join(APP_DIR, "inputs", "templates"),
        os.path.join(APP_DIR, "_internal", "inputs", "templates"),
        os.path.join(RESOURCE_DIR, "inputs", "templates"),
        os.path.join(APP_DIR, "templates"),
        os.path.join(APP_DIR, "_internal", "templates"),
        os.path.join(RESOURCE_DIR, "templates"),
    ]
)

def load_mappings(file_path=MAPPING_PATH):
    """Read key:value pairs from a text file into a dictionary.

    Expected line format:
        key: value

    Blank lines and lines starting with '#' are ignored.
    """
    mappings = {}

    with open(file_path, "r", encoding="utf-8") as mapping_file:
        for line_number, raw_line in enumerate(mapping_file, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                raise ValueError(
                    f"Invalid mapping at line {line_number}: {raw_line.rstrip()}"
                )

            key, value = line.split(":", 1)
            mappings[key.strip()] = value.strip()

    return mappings


def list_templates(templates_dir=TEMPLATES_DIR):
    return sorted(
        [f for f in os.listdir(templates_dir) if f.lower().endswith(".txt")]
    )


def render_template_with_mappings(template_path, mappings):
    """Replace {{key}} placeholders in a template with values from mappings.

    Any placeholder without a matching key is kept as-is.
    """
    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    placeholder_pattern = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

    def replace_placeholder(match):
        key = match.group(1)
        return str(mappings.get(key, match.group(0)))

    return placeholder_pattern.sub(replace_placeholder, template_content)


def render_template_to_file(template_path, output_path, mappings):
    """Render template markdown with mappings and write it to output_path."""
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    rendered_content = render_template_with_mappings(template_path, mappings)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(rendered_content)

    return output_path


def main():
    try:
        templates = list_templates()
    except FileNotFoundError:
        print(f"Templates folder not found: {TEMPLATES_DIR}")
        return

    try:
        mappings = load_mappings()
    except FileNotFoundError:
        print(f"Mappings file not found: {MAPPING_PATH}")
        return

    # print(templates)
    # print(mappings)

    for template in templates:
        template_path = os.path.join(TEMPLATES_DIR, template)
        output_name = f"{os.path.splitext(template)[0].partition('_template')[0]}_rendered.txt"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        render_template_to_file(template_path, output_path, mappings)
        print(f"Rendered {template} to {output_path}")


if __name__ == "__main__":
    main()
import os
import re

MAPPING_PATH = "mappings.txt"
TEMPLATES_DIR = "templates/"
OUTPUT_DIR = "outputs/"

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
    rendered_content = render_template_with_mappings(template_path, mappings)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(rendered_content)

    return output_path




print(list_templates())
print(load_mappings())

templates = list_templates()
mappings = load_mappings()

for template in templates:
    template_path = os.path.join(TEMPLATES_DIR, template)
    output_path = os.path.join(OUTPUT_DIR, f"rendered_{template[0:-13]}.txt")
    render_template_to_file(template_path, output_path, mappings)
    print(f"Rendered {template} to {output_path}")
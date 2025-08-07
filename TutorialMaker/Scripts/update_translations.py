import json
import os
import argparse
import re
import xml.dom.minidom as minidom
from xml.etree import ElementTree as ET

def parse_filename_language(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    match = re.match(r"(.+)_([a-z]{2}(?:-[A-Z]{2})?)$", base)
    if match:
        context = match.group(1)
        language = match.group(2)
    else:
        context = base
        language = "en-US"
    return context, language

def load_existing_translations(ts_path):
    if not os.path.exists(ts_path):
        return {}
    tree = ET.parse(ts_path)
    root = tree.getroot()
    translations = {}
    for context in root.findall("context"):
        for message in context.findall("message"):
            source = message.find("source").text
            translation = message.find("translation").text
            translations[source] = translation or ""
    return translations

def convert_json_to_ts(json_path, ts_output_path=None, preserve_existing=True):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    context_name, language = parse_filename_language(json_path)
    if ts_output_path is None:
        ts_output_path = os.path.splitext(json_path)[0] + f"_{language}.ts"

    existing_translations = load_existing_translations(ts_output_path) if preserve_existing else {}

    ts = ET.Element('TS', version="2.1", language=language)
    context = ET.SubElement(ts, 'context')
    name = ET.SubElement(context, 'name')
    name.text = context_name

    def add_messages(d):
        for key, value in d.items():
            if isinstance(value, dict):
                add_messages(value)
            elif isinstance(value, str):
                message = ET.SubElement(context, 'message')
                source = ET.SubElement(message, 'source')
                source.text = key
                translation = ET.SubElement(message, 'translation')
                translation.text = existing_translations.get(key, value)

    add_messages(data)

    rough_string = ET.tostring(ts, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    with open(ts_output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"[OK]: {ts_output_path}")

def convert_folder(folder_path, overwrite=False):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            json_path = os.path.join(folder_path, filename)
            convert_json_to_ts(json_path, preserve_existing=not overwrite)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON to Qt .ts converter with correct indentation and folder support")
    parser.add_argument("input", help="JSON file or folder containing JSON files")
    parser.add_argument("--overwrite", action="store_true", help="Ignore existing translations and overwrite everything")
    parser.add_argument("--output", help="(optional) Custom output path for single file")
    args = parser.parse_args()

    if os.path.isdir(args.input):
        convert_folder(args.input, overwrite=args.overwrite)
    else:
        convert_json_to_ts(args.input, args.output, preserve_existing=not args.overwrite)

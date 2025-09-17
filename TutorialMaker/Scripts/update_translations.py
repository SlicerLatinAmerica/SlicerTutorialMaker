import json
import os
import argparse
import re
import tempfile
import subprocess
import xml.etree.ElementTree as ET

# ------------------------
# Parsing Utilities
# ------------------------
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

# ------------------------
# JSON -> temporary .cpp
# ------------------------
def json_to_temp_cpp(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    lines.append('#include <QObject>\n\n')
    lines.append('class Dummy : public QObject {\n')
    lines.append('    Q_OBJECT\n')
    lines.append('public:\n')
    lines.append('    void dummy() {\n')

    def add_lines(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = f"{path}.{k}" if path else k
                add_lines(v, new_path)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_path = f"{path}[{i}]"
                add_lines(v, new_path)
        elif isinstance(obj, str):
            safe_text = obj.replace('"', '\\"')
            # Include comment with path for easier debugging:
            lines.append(f'        // {path}\n')
            lines.append(f'        tr("{safe_text}");\n')

    add_lines(data)

    lines.append('    }\n')
    lines.append('};\n')

    fd, temp_path = tempfile.mkstemp(suffix=".cpp", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as tmp:
        tmp.writelines(lines)

    print(f"Temporary C++ file created: {temp_path}")
    return temp_path

# ------------------------
# Run lupdate
# ------------------------
def run_lupdate(temp_cpp, ts_output, lupdate_path="lupdate"):
    cmd = [lupdate_path, temp_cpp, "-ts", ts_output, "-locations", "none"]
    subprocess.run(cmd, check=True)
    print(f"[OK] TS file generated: {ts_output}")

# ------------------------
# TS -> JSON
# ------------------------
def set_value_by_path(data, path, value):
    parts = re.split(r'\.(?![^\[]*\])', path)
    current = data
    for i, part in enumerate(parts):
        list_match = re.match(r'(.+)\[(\d+)\]$', part)
        if list_match:
            key, idx = list_match.groups()
            idx = int(idx)
            if key not in current:
                current[key] = []
            while len(current[key]) <= idx:
                current[key].append(None)
            if i == len(parts) - 1:
                current[key][idx] = value
            else:
                if current[key][idx] is None:
                    current[key][idx] = {}
                current = current[key][idx]
        else:
            if i == len(parts) - 1:
                current[part] = value
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]

def ts_to_json(ts_path, json_output):
    tree = ET.parse(ts_path)
    root = tree.getroot()
    result = {}

    for context in root.findall("context"):
        for message in context.findall("message"):
            path_elem = message.find("extracomment")
            source_elem = message.find("source")
            translation_elem = message.find("translation")

            if path_elem is None or source_elem is None:
                continue

            path = path_elem.text
            translation = translation_elem.text if translation_elem is not None else source_elem.text
            set_value_by_path(result, path, translation)

    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON file reconstructed: {json_output}")

# ------------------------
# Main CLI
# ------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert between JSON and TS translation files for Slicer")
    parser.add_argument("mode", choices=["json2ts", "ts2json"], help="Conversion mode")
    parser.add_argument("input", help="Input file (JSON or TS)")
    parser.add_argument("--output", help="Output file (TS or JSON)")
    parser.add_argument("--lupdate", help="Path to lupdate (only for json2ts)", default="lupdate")
    args = parser.parse_args()

    input_dir = os.path.dirname(os.path.abspath(args.input))
    input_base = os.path.basename(args.input)
    context, lang = parse_filename_language(args.input)

    if args.mode == "json2ts":
        if not args.output:
            base_name = os.path.splitext(input_base)[0]
            output_filename = f"{base_name}_{lang}.ts"
        else:
            output_filename = os.path.basename(args.output)

        args.output = os.path.join(input_dir, output_filename)

        temp_cpp = json_to_temp_cpp(args.input)
        run_lupdate(temp_cpp, args.output, args.lupdate)
        os.remove(temp_cpp)

    elif args.mode == "ts2json":
        if not args.output:
            output_filename = f"{lang}_{input_base}"
            output_filename = os.path.splitext(output_filename)[0] + "_translated.json"
        else:
            output_filename = os.path.basename(args.output)

        args.output = os.path.join(input_dir, output_filename)

        ts_to_json(args.input, args.output)

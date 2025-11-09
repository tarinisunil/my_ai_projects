from lxml import etree
import json
import traceback

def save_output_to_file(output, filename="analysis_output_debug.json"):
    """Save analysis output to a JSON file for debugging."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if isinstance(output, str):
                f.write(output)  # Write raw string if it's not already JSON-encoded
            else:
                json.dump(output, f, indent=4, ensure_ascii=False)
        print(f"[DEBUG] Saved analysis_output to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save analysis_output to file: {e}")
        traceback.print_exc()
        

def generate_dita_files(analysis_output):
    """Generate DITA XML files from Ollama’s inferred structure, with debug tracing."""
    print("[DEBUG] Starting DITA file generation")
    try:
        if not analysis_output:
            print("[ERROR] Analysis output is empty or None!")
        elif isinstance(analysis_output, str):
            print("[DEBUG] analysis_output is a string; attempting to parse JSON...")
            try:
                analysis_output = json.loads(analysis_output)
                print(f"[DEBUG] Parsed JSON successfully. Number of topics: {len(analysis_output)}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON decode error: {e}")
        else:
            print(f"[DEBUG] analysis_output is already a list or dict. Type: {type(analysis_output)}")

        dita_files = {}

        for idx, topic in enumerate(analysis_output):
            print(f"[DEBUG] Processing topic {idx+1}/{len(analysis_output)}: {topic.get('title', 'UNKNOWN')}")
            try:
                topic_title = topic.get("title", "Untitled_Topic").strip()
                topic_id = topic_title.replace(" ", "_")
                topic_type = topic.get("type", "concept")

                print(f"    [INFO] Creating topic: id='{topic_id}', type='{topic_type}'")

                root = etree.Element("topic", {"id": topic_id, "type": topic_type})
                title = etree.SubElement(root, "title")
                title.text = topic_title

                body = etree.SubElement(root, "body")
                elements = topic.get("body", [])
                print(f"    [INFO] Body contains {len(elements)} elements")

                for e_idx, element in enumerate(elements):
                    print(f"        [DEBUG] Element {e_idx+1}/{len(elements)}: {element}")
                    etype = element.get("element")

                    if etype == "p":
                        p = etree.SubElement(body, "p")
                        p.text = element.get("text", "")
                    elif etype == "step":
                        step = etree.SubElement(body, "step")
                        step.text = element.get("text", "")
                    elif etype == "table":
                        table = etree.SubElement(body, "table")
                        for r_idx, row in enumerate(element.get("rows", [])):
                            row_el = etree.SubElement(table, "row")
                            for c_idx, cell in enumerate(row):
                                cell_el = etree.SubElement(row_el, "entry")
                                cell_el.text = cell
                                print(f"            [DEBUG] Table cell ({r_idx},{c_idx}) = {cell}")
                    else:
                        print(f"        [WARN] Unknown element type: {etype}")

                dita_filename = f"{topic_id}.dita"
                dita_xml = etree.tostring(root, pretty_print=True, encoding="utf-8")
                dita_files[dita_filename] = dita_xml

                print(f"[SUCCESS] Generated DITA topic: {dita_filename} ({len(dita_xml)} bytes)")

            except Exception as inner_err:
                print(f"[ERROR] Failed to process topic '{topic.get('title', 'UNKNOWN')}'")
                traceback.print_exc()

        print(f"[DEBUG] DITA file generation complete. Total topics: {len(dita_files)}")
        return dita_files

    except Exception as e:
        print("[FATAL] Failed in generate_dita_files()")
        traceback.print_exc()
        raise e

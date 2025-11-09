from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import re

OLLAMA_HOST = "http://10.42.37.169:11434"

llm = OllamaLLM(base_url=OLLAMA_HOST, model="gemma3")

def save_to_file(data, filename):
    """Helper function to save content or response to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if isinstance(data, str):
                f.write(data)  # Write raw string if it's not JSON-encoded
            else:
                json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[DEBUG] Saved data to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save data to {filename}: {e}")

def clean_json_response(text: str):
    """
    Cleans Ollama / LLM output so that only valid JSON remains.
    Strips ```json ... ``` wrappers, leading 'json', and whitespace.
    """
    if not isinstance(text, str):
        return text  # already parsed
    
    # Remove markdown code block fences or 'json' prefix
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"^json", "", cleaned.strip(), flags=re.IGNORECASE)
    
    # Now we should have only the JSON array or object
    print(cleaned)
    return cleaned.strip()

def analyze_with_ollama(content):
    """Send parsed content to Ollama for intelligent analysis"""
      
    template = """
You are a technical documentation expert. 
You receive a parsed Word document as JSON, with headings, paragraphs, and tables.

Your task:
1. Identify distinct DITA topics and infer their types:
   - concept (explains)
   - task (procedure)
   - reference (data or tables)
2. Organize content hierarchically under those topics.
3. Detect reusable fragments:
   - warnings, cautions, notes
   - repeated product names or constants
4. Output a JSON array like this:
[
  {{
    "title": "...",
    "type": "task",
    "body": [
        {{"element": "p", "text": "..."}},
        {{"element": "step", "text": "..."}},
        {{"element": "table", "rows": [["col1","col2"],["val1","val2"]]}}
    ],
    "reusables": ["warning about X"]
  }}
]

Document JSON:
{content}
"""
    prompt = PromptTemplate(template=template, input_variables=["content"])
    chain = prompt | llm
    response = chain.invoke({"content": content})
    cleaned = clean_json_response(response)
    save_to_file(cleaned, "ollama_response_debug.json")
    return cleaned

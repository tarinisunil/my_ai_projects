from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import json

from word_parser import parse_word_doc
from dita_generator import generate_dita_files
from aem_uploader import upload_to_aem
from ollama_analyze import analyze_with_ollama


app = FastAPI(title="Ollama DITA Converter MCP Server")

AEM_URL = "http://no1010042073107:8080/content/dam/mytest"
AEM_USER = "admin"
AEM_PASS = "admin"
    
@app.post("/convert-to-dita/")
async def convert_to_dita(file: UploadFile):
    
    """Accept Word doc, infer structure with Ollama, generate DITA, upload to AEM."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        parsed = parse_word_doc(tmp_path)
        print("Parsed structure:", parsed[:3])  # Debug
        
        analysis = analyze_with_ollama(json.dumps(parsed))
        print("Ollama inference complete.")
        
        print("Calling generate dita file")
        dita_files = generate_dita_files(analysis)
        results = upload_to_aem(AEM_URL, AEM_USER, AEM_PASS, dita_files)

        return JSONResponse({"status": "success", "uploaded": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

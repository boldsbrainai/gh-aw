import os
import json
import urllib.request
from pathlib import Path
import time
import sys

TOKEN = "local-secure-token"
URL = "http://localhost:1188/translate"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def translate_chunk(text):
    if not text.strip():
        return text
    data = json.dumps({
        "text": text,
        "target_lang": "PT"
    }).encode("utf-8")
    
    req = urllib.request.Request(URL, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if res_data.get("code") == 200:
                return res_data.get("data", "")
            else:
                return text
    except Exception:
        return text

def chunk_and_translate(content, max_len=3000):
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_len = 0
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            
        current_chunk.append(line)
        current_len += len(line) + 1
        
        if current_len >= max_len and not in_code_block:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_len = 0
            
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
        
    translated_chunks = []
    for chunk in chunks:
        if in_code_block and chunk.startswith('```'): 
             translated_chunks.append(chunk)
             continue
             
        t = translate_chunk(chunk)
        translated_chunks.append(t if t else chunk)
        time.sleep(0.1) # small delay to prevent overwhelming the local API
        
    return '\n'.join(translated_chunks)

def main():
    md_files = []
    for path in Path('.').rglob('*.md'):
        if '.pt-br.md' not in path.name:
            md_files.append(path)
            
    total = len(md_files)
    print(f"Iniciando tradução de {total} arquivos Markdown em background...")
    sys.stdout.flush()
    
    success_count = 0
    fail_count = 0
    
    for i, path in enumerate(md_files):
        new_path = path.with_name(f"{path.stem}.pt-br.md")
        if new_path.exists():
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            translated = chunk_and_translate(content)
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(translated)
            
            success_count += 1
        except Exception:
            fail_count += 1
            
        if (i + 1) % 50 == 0:
            print(f"Progresso: {i + 1}/{total} concluídos.")
            sys.stdout.flush()
            
    print(f"Processamento concluído: {success_count} sucessos, {fail_count} falhas.")

if __name__ == "__main__":
    main()

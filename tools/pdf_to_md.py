import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print('PyMuPDF not installed. Installing...')
    import subprocess, shlex
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMuPDF'])
    import fitz

def pdf_to_md(pdf_path, md_path):
    doc = fitz.open(pdf_path)
    text_parts = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text_parts.append(text)
    full_text = "\n\n".join(text_parts)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f'Converted {pdf_path} -> {md_path}')

def main(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(dirpath, filename)
                md_filename = os.path.splitext(filename)[0] + '.md'
                md_path = os.path.join(dirpath, md_filename)
                if os.path.exists(md_path):
                    print(f'Skipping existing {md_path}')
                    continue
                pdf_to_md(pdf_path, md_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = os.getcwd()
    main(root)

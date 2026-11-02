import os
import docx

docx_files = [f for f in os.listdir('.') if f.endswith('.docx')]
doc_path = docx_files[0]
doc = docx.Document(doc_path)

with open('doc_dump.txt', 'w', encoding='utf-8') as f:
    f.write(f"=== INSPECTING: {doc_path} ===\n\n")
    f.write("=== PARAGRAPHS ===\n")
    for i, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        if txt:
            f.write(f"P{i:03d} [{p.style.name}]: {txt}\n")
    
    f.write("\n=== TABLES ===\n")
    for t_idx, table in enumerate(doc.tables):
        f.write(f"\n--- TABLE {t_idx} ({len(table.rows)} rows x {len(table.columns)} cols) ---\n")
        for r_idx, row in enumerate(table.rows):
            cells_text = [c.text.strip().replace('\n', ' ') for c in row.cells]
            f.write(f"  Row {r_idx:02d}: {cells_text}\n")

print("Dump completed to doc_dump.txt")

import re
import docx
from typing import List, Dict, Any

class DocumentChunk:
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

def process_document(docx_path: str) -> List[DocumentChunk]:
    """
    Parses a DOCX file and extracts chunks based on logical structure 
    (Module -> Task -> Subtask). Groups text within a subtask/task into a single chunk.
    """
    doc = docx.Document(docx_path)
    chunks = []
    
    current_module = "Unknown Module"
    current_task = ""
    current_subtask = ""
    
    current_text_block = []
    
    def finalize_chunk():
        if current_text_block:
            text = "\n".join(current_text_block).strip()
            if text:
                metadata = {
                    "module": current_module,
                    "task": current_task,
                    "subtask": current_subtask
                }
                chunks.append(DocumentChunk(text=text, metadata=metadata))
            current_text_block.clear()

    from docx.oxml.text.paragraph import CT_P
    from docx.oxml.table import CT_Tbl
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    def iter_block_items(parent):
        for child in parent.element.body:
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            para = block
            style_name = para.style.name if para.style else ""
            text = para.text.strip()
            
            if not text:
                if 'graphicData' in para._p.xml:
                    text = "[Screenshot placeholder]"
                else:
                    continue
                    
            if style_name.startswith('Heading 1'):
                finalize_chunk()
                current_module = text
                current_task = ""
                current_subtask = ""
            elif style_name.startswith('Heading 2'):
                finalize_chunk()
                current_task = text
                current_subtask = ""
            elif style_name.startswith('Heading 3'):
                finalize_chunk()
                current_subtask = text
            else:
                current_text_block.append(text)
        elif isinstance(block, Table):
            table = block
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_data:
                    current_text_block.append(" | ".join(row_data))
                    
    # Finalize the last chunk
    finalize_chunk()
    
    return chunks

if __name__ == "__main__":
    # Test the processor
    chunks = process_document("../data/eVitals_User_Guide_v25_HTA.docx")
    for c in chunks[:5]:
        print(f"Meta: {c.metadata}")
        print(f"Text: {c.text[:100]}...\n")

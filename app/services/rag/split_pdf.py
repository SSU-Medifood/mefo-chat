import fitz
import os

def split_pdf(input_file: str, batch_size: int = 10) -> list:
    doc = fitz.open(input_file)
    num_pages = len(doc)
    split_files = []

    for start in range(0, num_pages, batch_size):
        end = min(start + batch_size, num_pages)
        split_file = f"{os.path.splitext(input_file)[0]}_{start}_{end - 1}.pdf"
        split_doc = fitz.open()
        split_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
        split_doc.save(split_file)
        split_doc.close()
        split_files.append(split_file)

    doc.close()
    return split_files
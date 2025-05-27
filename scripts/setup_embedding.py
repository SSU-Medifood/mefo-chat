import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.rag.markdown_converter import get_requestId, save_markdown
from app.services.rag.split_pdf import split_pdf
from app.services.rag.rag_service import initialize_chroma_from_markdown


pdf_path = "data/함께해요_당뇨병_관리!_(2024).pdf"
md_output_dir = "data/markdown_chunks"
os.makedirs(md_output_dir, exist_ok=True)

# 1. PDF → 10페이지씩 분할
split_files = split_pdf(pdf_path, batch_size=10)
'''
split_files = sorted([
    os.path.join("data", fname)
    for fname in os.listdir("data")
    if fname.startswith("2025년도_대사증후군_건강실천안내서_") and fname.endswith(".pdf")
])
'''

# 2. 각 분할 PDF → 비동기 요청 → Markdown 저장
markdown_paths = []
for split_file in split_files:
    try:
        print(f"\n🚀 변환 요청 중: {split_file}")
        request_id = get_requestId(split_file)
        md_path = os.path.join(md_output_dir, os.path.basename(split_file).replace(".pdf", ".md"))
        save_markdown(request_id, md_path)
        markdown_paths.append(md_path)
    except Exception as e:
        print(f"❌ {split_file} 처리 실패: {str(e)}")

# 3. 모든 Markdown 파일을 하나로 합쳐서 임베딩
merged_md_path = "data/2025_merged.md"
with open(merged_md_path, "w", encoding="utf-8") as out_file:
    for md_file in markdown_paths:
        with open(md_file, "r", encoding="utf-8") as f:
            out_file.write(f.read())
            out_file.write("\n\n")

# 4. 임베딩 실행
initialize_chroma_from_markdown(merged_md_path)
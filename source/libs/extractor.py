import os, sys
import json
import httpx
import asyncio
from loguru import logger

path_this = os.path.dirname(os.path.abspath(__file__))
path_project = os.path.dirname(os.path.join(path_this, '..'))
path_root = os.path.dirname(os.path.join(path_this, '../..'))
sys.path.extend([path_root, path_project, path_this])

from config import settings

# ============================================================================
# DOCLING EXTRACTOR
# ============================================================================

class DoclingExtractor:
    """Handles document extraction using Docling API."""
    
    def __init__(self):
        self.api_url = settings.DOCLING_BASE_URL
    
    async def extract_source_async(
        self,
        doc_url: str = None,
        generate_picture_images: bool = False
    ) -> str:
        """Extract text from a document using the new Docling API asynchronously."""
        try:
            payload = {
                "options": {
                    "from_formats": [
                        "docx", "pptx", "html", "image", "pdf",
                        "asciidoc", "md", "csv", "xlsx", "xml_uspto",
                        "xml_jats", "mets_gbs", "json_docling", "audio"
                    ],
                    "to_formats": ["md"],
                    "image_export_mode": "placeholder",
                    "do_ocr": True,
                    "force_ocr": False,
                    "ocr_engine": "easyocr",
                    "ocr_lang": [],
                    "pdf_backend": "pypdfium2",
                    "table_mode": "accurate",
                    "table_cell_matching": True,
                    "pipeline": "standard",
                    "page_range": [1, 9223372036854776000],
                    "document_timeout": 604800,
                    "abort_on_error": True,
                    "do_table_structure": True,
                    "include_images": generate_picture_images,
                    "images_scale": 2,
                    "md_page_break_placeholder": "<!-- page-break -->",
                    "do_code_enrichment": False,
                    "do_formula_enrichment": False,
                    "do_picture_classification": False,
                    "do_picture_description": False
                },
                "sources": [
                    {
                        "url": doc_url,
                        "kind": "url"
                    }
                ],
                "target": {"kind": "inbody"}
            }
            
            async with httpx.AsyncClient(timeout=3600) as client:
                response = await client.post(
                    f"{self.api_url}/v1/convert/source/async",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                extraction_content = result.get("document", {}).get("md_content", "")
                
                if not extraction_content:
                    logger.warning("Document extraction returned no data.")
                    return ""
                
                logger.info(f"Successfully extracted document from {doc_url}")
                return extraction_content

        except (httpx.HTTPError, httpx.RequestError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Document extraction failed for {doc_url}: {e}")
            raise

    async def extract_file_async(
        self,
        doc_file: str = None,
    ) -> str:
        """Extract text from a document using the Docling API asynchronously."""
        try:
            payload = {
                "to_formats": ["md", "json", "html"],
                "image_export_mode": "placeholder",
                "ocr": False,
                "abort_on_error": False,
                "md_page_break_placeholder": "<!-- page-break -->",
            }

            with open(doc_file, "rb") as f:
                files = {"files": (os.path.basename(doc_file), f, "application/pdf")}

                async with httpx.AsyncClient(timeout=3600) as client:
                    # Step 1: Submit file for async conversion
                    response = await client.post(
                        f"{self.api_url}/v1/convert/file/async",
                        data=payload,
                        files=files
                    )
                    response.raise_for_status()
                    task = response.json()
                    logger.info(f"Submitted task: {task}")

                    # Step 2: Poll until completion
                    while task["task_status"] not in ("success", "failure"):
                        await asyncio.sleep(2)  # async sleep
                        response = await client.get(
                            f"{self.api_url}/v1/status/poll/{task['task_id']}"
                        )
                        response.raise_for_status()
                        task = response.json()
                        logger.info(
                            f"Polling... status={task['task_status']} "
                            f"position={task.get('task_position')}"
                        )

                    # Step 3: Verify task completion
                    if task["task_status"] != "success":
                        logger.error(f"Task failed with status: {task['task_status']}")
                        return ""

                    logger.info(f"Task completed successfully: {task['task_id']}")

                    # Step 4: Fetch final result
                    result_resp = await client.get(
                        f"{self.api_url}/v1/result/{task['task_id']}"
                    )
                    result_resp.raise_for_status()
                    result = result_resp.json()

                    document = result.get("document", {})
                    assert "md_content" in document and document["md_content"], "Missing md_content"
                    assert "html_content" in document and document["html_content"], "Missing html_content"
                    assert "json_content" in document and document["json_content"], "Missing json_content"
                    assert document["json_content"].get("schema_name") == "DoclingDocument", "Invalid schema"

                    logger.info("Document extraction successful.")
                    return document["md_content"]

        except (httpx.HTTPError, httpx.RequestError, json.JSONDecodeError, ValueError, AssertionError) as e:
            logger.error(f"Document extraction failed for {doc_file}: {e}")
            raise

if __name__ == "__main__":
    import asyncio

    async def main():
        extractor = DoclingExtractor()
        start_time = asyncio.get_event_loop().time()
        content = await extractor.extract_file_async(
            # doc_file="/home/rifqi/multiagent/book-evaluator-and-fact-checking-agent/source/documents/munzir,+07+Lintang,+Saiful,+Yusron.pdf"
            # doc_file="/home/rifqi/multiagent/book-evaluator-and-fact-checking-agent/source/documents/PROPAM POLRI.pdf"
            doc_file="/home/rifqi/multiagent/book-evaluator-and-fact-checking-agent/source/documents/Transformasi Ekonomi Daerah 2025-2045 v1.pdf"
        )
        end_time = asyncio.get_event_loop().time()
        print(content)
        print(f"Extraction took {end_time - start_time:.2f} seconds")

    asyncio.run(main())
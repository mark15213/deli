
import os
import requests
import tarfile
import shutil
import logging
from pathlib import Path
import io
import fitz  # PyMuPDF
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Static images directory - consistent with pdf_extractor.py behavior
STATIC_IMAGES_DIR = Path(__file__).parent.parent.parent / "static" / "images"

class ArxivExtractor:
    """
    Service to extract figures from arXiv LaTeX source files.
    """
    
    def process_arxiv_paper(self, arxiv_id: str) -> List[str]:
        """
        Main entry point: Download source, extract figures, convert PDFs to PNG,
        and return list of local paths (relative static URLs).
        
        Args:
            arxiv_id: The arXiv ID (e.g. "2602.00919")
            
        Returns:
            List of relative URL paths to the extracted images.
        """
        logger.info(f"Starting arXiv source extraction for {arxiv_id}")
        
        # Temp dir for extraction
        temp_dir = Path(__file__).parent.parent.parent / "data" / "temp_source" / arxiv_id
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Download Source
        if not self._download_source(arxiv_id, temp_dir):
            logger.warning(f"Failed to download/extract source for {arxiv_id}")
            return []
            
        # 2. Extract & Convert
        # We will save final images directly to the static folder used by the app
        # Format: static/images/{arxiv_id}/...
        final_output_dir = STATIC_IMAGES_DIR / arxiv_id
        final_output_dir.mkdir(parents=True, exist_ok=True)
        
        relative_urls = self._extract_and_convert_images(temp_dir, final_output_dir, arxiv_id)
        
        # Cleanup temp
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return relative_urls

    def _download_source(self, arxiv_id: str, output_dir: Path) -> bool:
        """Download and extract arXiv source tarball."""
        url = f"https://arxiv.org/e-print/{arxiv_id}"
        logger.info(f"Downloading source from {url}...")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                logger.warning(f"arXiv source download failed: {response.status_code}")
                return False
            
            # Check if it's a tar file
            try:
                with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
                    tar.extractall(path=output_dir)
                    logger.info(f"Extracted source to {output_dir}")
                return True
            except tarfile.ReadError:
                # Fallback: maybe it's just a PDF? If so, source extraction isn't useful here.
                logger.warning("Downloaded content is not a valid tar.gz file.")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading source: {e}")
            return False

    def _convert_pdf_to_png(self, pdf_path: Path, output_path: Path) -> bool:
        """Convert a single page PDF to PNG."""
        try:
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                page = doc[0] 
                # Use high DPI for quality
                pix = page.get_pixmap(dpi=300) 
                pix.save(output_path)
                doc.close()
                return True
        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {e}")
        return False

    def _extract_and_convert_images(self, source_dir: Path, output_dir: Path, source_id: str) -> List[str]:
        """
        Scan source dir for PDF figures, convert to PNG, and save to output dir.
        Returns list of relative URLs.
        """
        saved_paths = []
        extracted_count = 0
        
        # Recursive walk
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                
                # Only process PDF figures as per requirement
                if ext == '.pdf':
                    file_path = Path(root) / file
                    
                    # Size heuristic: skip likely full papers (> 5MB)
                    if file_path.stat().st_size > 5 * 1024 * 1024:
                        logger.debug(f"Skipping large PDF (likely paper): {file}")
                        continue
                    
                    # Convert to PNG
                    base_name = os.path.splitext(file)[0]
                    # Create a unique name to avoid flattening collisions? 
                    # For now assume filenames are unique enough or just use flat name
                    png_filename = f"{base_name}.png"
                    dest_path = output_dir / png_filename
                    
                    if self._convert_pdf_to_png(file_path, dest_path):
                        # Construct relative URL for frontend
                        # Assuming static is served at /static
                        relative_url = f"/static/images/{source_id}/{png_filename}"
                        saved_paths.append(relative_url)
                        extracted_count += 1
                        logger.debug(f"Converted figure: {png_filename}")
        
        logger.info(f"Extracted {extracted_count} figures from arXiv source")
        return saved_paths

# Singleton
arxiv_extractor = ArxivExtractor()

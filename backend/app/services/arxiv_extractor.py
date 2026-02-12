
import os
import re
import requests
import tarfile
import shutil
import logging
from pathlib import Path
import io
import fitz  # PyMuPDF
from typing import List, Optional, Set

# Configure logging
logger = logging.getLogger(__name__)

# Static images directory - uses settings.storage_dir for env-aware path
from app.core.config import get_settings
_settings = get_settings()
STATIC_IMAGES_DIR = Path(_settings.storage_dir) / "images"

# Supported image extensions
IMAGE_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}

class ArxivExtractor:
    """
    Service to extract figures from arXiv LaTeX source files.
    Parses LaTeX \includegraphics references to extract only figures
    actually used in the paper.
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
            response = requests.get(url, stream=True, timeout=60)
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

    def _parse_referenced_figures(self, source_dir: Path) -> Set[str]:
        """
        Parse all .tex files to find \\includegraphics references.
        Returns a set of referenced image paths (relative to source_dir).
        Skips commented-out lines.
        """
        referenced = set()
        # Regex to match \includegraphics[...]{path} or \includegraphics{path}
        pattern = re.compile(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}')
        
        for tex_file in source_dir.rglob("*.tex"):
            try:
                content = tex_file.read_text(encoding='utf-8', errors='ignore')
                for line in content.splitlines():
                    stripped = line.strip()
                    # Skip commented-out lines
                    if stripped.startswith('%'):
                        continue
                    for match in pattern.finditer(line):
                        ref_path = match.group(1).strip()
                        referenced.add(ref_path)
            except Exception as e:
                logger.warning(f"Failed to parse {tex_file}: {e}")
        
        logger.info(f"Found {len(referenced)} \\includegraphics references in LaTeX source: {referenced}")
        return referenced

    def _is_referenced(self, file_path: Path, source_dir: Path, referenced: Set[str]) -> bool:
        """
        Check if a file matches any LaTeX \\includegraphics reference.
        LaTeX references may omit the file extension, so we check both
        with and without extension.
        """
        # Get relative path from source dir
        try:
            rel_path = file_path.relative_to(source_dir)
        except ValueError:
            rel_path = Path(file_path.name)
        
        rel_str = str(rel_path)
        rel_no_ext = str(rel_path.with_suffix(''))
        
        for ref in referenced:
            # Normalize: remove leading ./ if present
            ref_clean = ref.lstrip('./')
            ref_no_ext = str(Path(ref_clean).with_suffix(''))
            
            # Match with extension
            if rel_str == ref_clean:
                return True
            # Match without extension (LaTeX often omits extensions)
            if rel_no_ext == ref_no_ext:
                return True
        
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

    def _copy_raster_image(self, src_path: Path, dest_path: Path) -> bool:
        """Copy a raster image (PNG/JPEG) to the output directory."""
        try:
            shutil.copy2(src_path, dest_path)
            return True
        except Exception as e:
            logger.error(f"Failed to copy {src_path}: {e}")
        return False

    def _extract_and_convert_images(self, source_dir: Path, output_dir: Path, source_id: str) -> List[str]:
        """
        Scan source dir for image files, filter by LaTeX references,
        convert/copy to output dir. Returns list of relative URLs.
        """
        saved_paths = []
        extracted_count = 0
        
        # Parse LaTeX references for smart filtering
        referenced = self._parse_referenced_figures(source_dir)
        use_latex_filter = len(referenced) > 0
        
        if use_latex_filter:
            logger.info(f"Using LaTeX-based filtering: {len(referenced)} referenced figures")
        else:
            logger.info("No LaTeX files found, extracting all image files with size heuristic")
        
        # Track used filenames to avoid collisions from nested dirs
        used_filenames = set()
        
        # Recursive walk
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                
                if ext not in IMAGE_EXTENSIONS:
                    continue
                    
                file_path = Path(root) / file
                
                # Size heuristic: skip very large files (> 5MB, likely full papers or raw photos)
                if file_path.stat().st_size > 5 * 1024 * 1024:
                    logger.debug(f"Skipping large file ({file_path.stat().st_size} bytes): {file}")
                    continue
                
                # LaTeX filter: only extract referenced figures
                if use_latex_filter and not self._is_referenced(file_path, source_dir, referenced):
                    logger.debug(f"Skipping unreferenced file: {file}")
                    continue
                
                # Determine output filename (handle collisions)
                base_name = os.path.splitext(file)[0]
                # For PDFs, always convert to PNG
                out_ext = ".png" if ext == '.pdf' else ext
                out_filename = f"{base_name}{out_ext}"
                
                # Handle filename collisions by prepending parent dir
                if out_filename in used_filenames:
                    rel_parent = Path(root).relative_to(source_dir)
                    safe_parent = str(rel_parent).replace("/", "_").replace("\\", "_")
                    out_filename = f"{safe_parent}_{base_name}{out_ext}"
                
                used_filenames.add(out_filename)
                dest_path = output_dir / out_filename
                
                # Convert/copy based on format
                if ext == '.pdf':
                    success = self._convert_pdf_to_png(file_path, dest_path)
                else:
                    success = self._copy_raster_image(file_path, dest_path)
                
                if success:
                    relative_url = f"/static/images/{source_id}/{out_filename}"
                    saved_paths.append(relative_url)
                    extracted_count += 1
                    logger.debug(f"Extracted figure: {out_filename}")
        
        logger.info(f"Extracted {extracted_count} figures from arXiv source")
        return saved_paths

# Singleton
arxiv_extractor = ArxivExtractor()

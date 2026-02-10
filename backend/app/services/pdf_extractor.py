"""
PDF Figure Extraction Service

Extracts images/figures from PDF documents using PyMuPDF (fitz).
"""
import os
import logging
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
import io
import requests
import tarfile
import shutil
import tempfile

logger = logging.getLogger(__name__)

# Minimum image dimensions to filter out icons/logos
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100

# Static images directory
STATIC_IMAGES_DIR = Path(__file__).parent.parent.parent / "static" / "images"


@dataclass
class ExtractedFigure:
    """Represents an extracted figure from a PDF."""
    index: int
    page_num: int
    image_bytes: bytes
    width: int
    height: int
    format: str  # 'png', 'jpeg', etc.
    caption: Optional[str] = None


def extract_figures_from_pdf(pdf_bytes: bytes, min_width: int = MIN_IMAGE_WIDTH, min_height: int = MIN_IMAGE_HEIGHT) -> List[ExtractedFigure]:
    """
    Extract all significant figures/images from a PDF.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        min_width: Minimum width to include (filters icons)
        min_height: Minimum height to include (filters icons)
        
    Returns:
        List of ExtractedFigure objects
    """
    figures = []
    figure_index = 0
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                try:
                    # Use Pixmap for better colorspace handling (e.g., CMYK -> RGB)
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Convert CMYK to RGB if needed
                    if pix.n - pix.alpha > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    width, height = pix.width, pix.height
                    
                    # Filter small images (icons, logos)
                    if width < min_width or height < min_height:
                        logger.debug(f"Skipping small image ({width}x{height}) on page {page_num}")
                        pix = None  # Free memory
                        continue
                    
                    # Get image bytes (PNG format)
                    image_bytes = pix.tobytes("png")
                    image_ext = "png"
                    
                    pix = None  # Free memory
                    
                    figures.append(ExtractedFigure(
                        index=figure_index,
                        page_num=page_num + 1,  # 1-indexed
                        image_bytes=image_bytes,
                        width=width,
                        height=height,
                        format=image_ext,
                    ))
                    figure_index += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} on page {page_num}: {e}")
                    continue
        
        doc.close()
        logger.info(f"Extracted {len(figures)} figures from PDF")
        
    except Exception as e:
        logger.error(f"Failed to process PDF: {e}")
        raise
    
    return figures


def save_figures_to_local(source_id: str, figures: List[ExtractedFigure]) -> List[str]:
    """
    Save extracted figures to local static directory.
    
    Args:
        source_id: UUID of the source (used as folder name)
        figures: List of extracted figures
        
    Returns:
        List of relative URL paths (e.g., ["/static/images/{source_id}/fig_0.png", ...])
    """
    # Create directory for this source
    source_dir = STATIC_IMAGES_DIR / str(source_id)
    source_dir.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    
    for fig in figures:
        if fig.caption:
            # simple sanitization just in case
            safe_name = Path(fig.caption).stem
            filename = f"{safe_name}.{fig.format}"
        else:
            filename = f"fig_{fig.index}.{fig.format}"
            
        file_path = source_dir / filename
        
        try:
            with open(file_path, "wb") as f:
                f.write(fig.image_bytes)
            
            # Return relative URL path
            relative_url = f"/static/images/{source_id}/{filename}"
            saved_paths.append(relative_url)
            logger.debug(f"Saved figure {fig.index} to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save figure {fig.index}: {e}")
            continue
    
    logger.info(f"Saved {len(saved_paths)} figures for source {source_id}")
    return saved_paths


import requests
import tarfile
import shutil
import tempfile

def extract_figures_from_arxiv_source(arxiv_id: str) -> List[ExtractedFigure]:
    """
    Download Arxiv source, extract figures (PDFs), and convert to PNG.
    """
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    logger.info(f"Downloading source from {url}...")
    
    figures = []
    figure_index = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source"
        source_dir.mkdir()
        
        try:
            # Download
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                logger.error(f"Failed to download Arxiv source: {response.status_code}")
                return []
                
            # Extract
            try:
                # Try opening as tar.gz
                with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
                    tar.extractall(path=source_dir)
            except tarfile.ReadError:
                logger.warning("Arxiv source is not a valid tar.gz. Might be a single file or unavailable.")
                return []
            
            # Walk and find PDFs
            # Logic adapted from user's test script
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        file_path = Path(root) / file
                        
                        # Skip large files (likely the main paper)
                        if file_path.stat().st_size > 5 * 1024 * 1024:
                            logger.info(f"Skipping large PDF (likely full paper): {file}")
                            continue

                        try:
                            # Convert first page of PDF figure to PNG
                            doc = fitz.open(file_path)
                            if len(doc) > 0:
                                page = doc[0]
                                pix = page.get_pixmap(dpi=300)
                                image_bytes = pix.tobytes("png")
                                
                                figures.append(ExtractedFigure(
                                    index=figure_index,
                                    page_num=1, # Figure files usually 1 page
                                    image_bytes=image_bytes,
                                    width=pix.width,
                                    height=pix.height,
                                    format="png",
                                    caption=file # Use filename as caption/id
                                ))
                                figure_index += 1
                                doc.close()
                        except Exception as e:
                            logger.warning(f"Failed to convert figure PDF {file}: {e}")
                            continue

        except Exception as e:
            logger.error(f"Error extracting figures from Arxiv source: {e}")
    
    logger.info(f"Extracted {len(figures)} figures from Arxiv source {arxiv_id}")
    return figures

def get_figure_info_for_prompt(figures: List[ExtractedFigure]) -> str:
    """
    Generate a text description of figures for LLM prompt.
    
    Args:
        figures: List of extracted figures
        
    Returns:
        Formatted string describing each figure
    """
    if not figures:
        return "No figures extracted from PDF."
    
    lines = []
    for fig in figures:
        desc = f"- Figure {fig.index}: Size {fig.width}x{fig.height}px"
        if fig.caption:
            desc += f" (Filename: {fig.caption})"
        lines.append(desc)
    
    return "\n".join(lines)


def optimize_images_for_gemini(figures: List[ExtractedFigure], max_dim: int = 1024) -> List[bytes]:
    """
    Optimizes images for Gemini API:
    - Resize max dimension to 1024px
    - Convert to JPEG (efficient token usage)
    - Return list of image bytes
    """
    optimized_images = []
    
    for fig in figures:
        try:
            img = Image.open(io.BytesIO(fig.image_bytes))
            
            # Convert RGBA/P to RGB for JPEG
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            # Resize if needed
            width, height = img.size
            if width > max_dim or height > max_dim:
                ratio = min(max_dim / width, max_dim / height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
            # Save as JPEG
            out_io = io.BytesIO()
            img.save(out_io, format='JPEG', quality=85)
            optimized_images.append(out_io.getvalue())
            
        except Exception as e:
            logger.warning(f"Failed to optimize figure {fig.index}: {e}")
            # Skip failed images or push original specific logic? 
            # For now skip to avoid breaking the batch
            continue
            
    return optimized_images

import logging
import uuid
import subprocess
import pypdfium2 as pdfium
from pathlib import Path
from PIL import Image, ImageChops

from src.config import settings

log = logging.getLogger(__name__)

# Standard preamble for scientific drawing
LATEX_PREAMBLE = r"""
\documentclass[preview, border=1mm]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{tikz}
\usetikzlibrary{decorations.pathmorphing, arrows.meta, positioning, calc, decorations.markings, svg.path, shapes.geometric, quotes}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\usepackage{tkz-base}
\usepackage{tkz-euclide}
\begin{document}
"""

LATEX_POSTAMBLE = r"""
\end{document}
"""

def compile_latex_to_image(latex_code: str, output_format: str = "png", dpi: int = 300) -> Path:
    """
    Compiles LaTeX code to an image (PNG).
    Pipeline: LaTeX Code -> .tex -> .pdf (via lualatex) -> .png (via pypdfium2).
    """
    # 1. Setup paths using our centralized settings
    build_dir = settings.TEMP_BUILD_DIR
    unique_id = uuid.uuid4().hex[:8]
    filename = f"figure_{unique_id}"
    
    source_file = build_dir / f"{filename}.tex"
    pdf_file = build_dir / f"{filename}.pdf"
    final_image_path = build_dir / f"{filename}.{output_format}"

    # 2. Write .tex file
    full_document = LATEX_PREAMBLE + latex_code + LATEX_POSTAMBLE
    source_file.write_text(full_document, encoding='utf-8')

    # 3. Compile to PDF using lualatex
    compile_cmd = [
        "lualatex",
        "--interaction=nonstopmode",
        "--file-line-error",
        f"--output-directory={build_dir}",
        str(source_file)
    ]

    try:
        process = subprocess.run(
            compile_cmd, 
            capture_output=True,
            text=True, 
            check=False, 
            encoding='utf-8', 
            timeout=60
            )
        
        if process.returncode != 0:
            log.error("LaTeX Compilation Failed.")
            raise RuntimeError(f"LaTeX Error:\n{process.stdout}")

        # 4. Convert PDF to Image
        pdf_doc = pdfium.PdfDocument(pdf_file)
        page = pdf_doc[0]
        image_raw = page.render(scale=dpi/72).to_pil()
        
        # 5. Crop whitespace
        image_cropped = _crop_image(image_raw)
        image_cropped.save(final_image_path)
        
        log.info(f"✅ Generated image: {final_image_path.name}")
        return final_image_path

    except FileNotFoundError:
        raise RuntimeError("Command 'lualatex' not found. Please install a LaTeX distribution.")
    except Exception as e:
        log.error(f"Compilation error: {e}")
        raise e
    finally:
        # Cleanup temporary files (keep the final image)
        for f in build_dir.glob(f"{filename}.*"):
            if f.suffix.lower() != f".{output_format}":
                try:
                    f.unlink()
                except OSError:
                    pass

def _crop_image(image: Image.Image, threshold: int = 10) -> Image.Image:
    """Crops white background from the image."""
    bg = Image.new(image.mode, image.size, (255, 255, 255))
    diff = ImageChops.difference(image, bg)
    diff = diff.convert('L')
    bbox = diff.point(lambda x: 255 if x > threshold else 0).getbbox()
    return image.crop(bbox) if bbox else image
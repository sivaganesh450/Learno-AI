"""
OCR Service for extracting text from images with layout preservation
Uses Tesseract with advanced layout analysis to maintain format
"""

from PIL import Image, ImageOps, ImageEnhance
import io
import pandas as pd

# Tesseract for OCR
try:
    import pytesseract
    import platform
    if platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # On Linux (Render/prod), tesseract is expected on PATH at /usr/bin/tesseract
    TESSERACT_AVAILABLE = True
    print("Tesseract OCR initialized")
except Exception:
    TESSERACT_AVAILABLE = False
    print("Tesseract not available")


def preprocess_image(image: Image.Image, aggressive: bool = False) -> Image.Image:
    """Preprocess image for better OCR accuracy"""
    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')
    
    # Resize if small - larger resolutions help OCR
    width, height = image.size
    if width < 600 or height < 200:
        scale = max(600 / width, 200 / height)
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    elif aggressive and width < 1200:
        # More aggressive scaling for difficult images
        scale = 1200 / width
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.5 if aggressive else 2.0)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0 if aggressive else 1.5)
    
    # Apply threshold for clearer text
    threshold = 130 if aggressive else 140
    image = image.point(lambda p: 255 if p > threshold else 0)
    
    # Invert if background is dark
    pixels = list(image.getdata())
    avg_pixel = sum(pixels) / len(pixels)
    if avg_pixel < 128:
        image = ImageOps.invert(image)
    
    return image


def clean_math_text(text: str) -> str:
    """
    Clean and normalize extracted math text with proper symbols
    """
    # Replace common OCR mistakes and convert to readable math symbols
    replacements = {
        # Math operators
        '÷': '/',
        '×': '*',
        '·': '*',
        '•': '*',
        '−': '-',
        '—': '-',
        '–': '-',
        # Superscripts to powers
        '²': '^2',
        '³': '^3',
        '⁴': '^4',
        '⁵': '^5',
        '⁶': '^6',
        '⁷': '^7',
        '⁸': '^8',
        '⁹': '^9',
        '⁰': '^0',
        '¹': '^1',
        # Subscripts
        '₀': '_0',
        '₁': '_1',
        '₂': '_2',
        '₃': '_3',
        '₄': '_4',
        '₅': '_5',
        '₆': '_6',
        '₇': '_7',
        '₈': '_8',
        '₉': '_9',
        # Math symbols
        '√': 'sqrt',
        '∛': 'cbrt',
        'π': 'pi',
        '∞': 'infinity',
        '≠': '!=',
        '≤': '<=',
        '≥': '>=',
        '±': '+/-',
        '∓': '-/+',
        '∑': 'sum',
        '∏': 'product',
        '∫': 'integral',
        '∂': 'd',
        '∅': 'empty',
        '∈': ' in ',
        '∉': ' not in ',
        '⊂': ' subset ',
        '⊃': ' superset ',
        '∪': ' union ',
        '∩': ' intersection ',
        '⟨': '<',
        '⟩': '>',
        # Greek letters - lowercase
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
        'δ': 'delta',
        'ε': 'epsilon',
        'ζ': 'zeta',
        'η': 'eta',
        'θ': 'theta',
        'ι': 'iota',
        'κ': 'kappa',
        'λ': 'lambda',
        'μ': 'mu',
        'ν': 'nu',
        'ξ': 'xi',
        'ο': 'omicron',
        'ρ': 'rho',
        'σ': 'sigma',
        'ς': 'sigma',  # final sigma
        'τ': 'tau',
        'υ': 'upsilon',
        'φ': 'phi',
        'χ': 'chi',
        'ψ': 'psi',
        'ω': 'omega',
        # Greek letters - uppercase
        'Α': 'Alpha',
        'Β': 'Beta',
        'Γ': 'Gamma',
        'Δ': 'Delta',
        'Ε': 'Epsilon',
        'Ζ': 'Zeta',
        'Η': 'Eta',
        'Θ': 'Theta',
        'Ι': 'Iota',
        'Κ': 'Kappa',
        'Λ': 'Lambda',
        'Μ': 'Mu',
        'Ν': 'Nu',
        'Ξ': 'Xi',
        'Ο': 'Omicron',
        'Π': 'Pi',
        'Ρ': 'Rho',
        'Σ': 'Sigma',
        'Τ': 'Tau',
        'Υ': 'Upsilon',
        'Φ': 'Phi',
        'Χ': 'Chi',
        'Ψ': 'Psi',
        'Ω': 'Omega',
        # Quotes
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Fix common OCR misreads (BEFORE general letter-to-symbol confusion)
    import re
    result = result.replace('oomega', 'omega')
    result = result.replace('omegha', 'omega')
    result = result.replace('omega?', 'omega^2')
    result = result.replace('omega2', 'omega^2')
    result = result.replace('omegaZ', 'omega^2')
    result = result.replace('omegaz', 'omega^2')
    result = result.replace('A=|', 'A = |')
    result = result.replace('A=[', 'A = |')
    result = result.replace('|]', '|')
    result = result.replace('omegahere', 'omega, where')
    result = result.replace('whereomega', 'where omega')
    result = result.replace('isone', 'is one')
    
    # Fix common letter-to-symbol confusions (more aggressive)
    result =re.sub(r'\bow\b', 'omega', result)  # standalone "ow" -> "omega"
    result = re.sub(r'\bw\b', 'omega', result)  # standalone "w" -> "omega"
    result = re.sub(r'(?<=[|\s])w(?=[|\s])', 'omega', result)  # "w" between spaces/bars
    
    return result


def smart_format_math(text: str) -> str:
    """
    Intelligently format mathematical text, especially matrices and determinants
    """
    import re
    
    lines = text.split('\n')
    formatted_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Check if this line starts a matrix/determinant
        # Look for pattern: text with = followed by vertical bars or matrix elements
        if '=' in line or 'Evaluate' in line or 'Delta' in line or 'Δ' in line:
            # This is likely the problem statement
            formatted_lines.append(line)
            i += 1
            
            # Check next few lines for matrix structure
            matrix_lines = []
            while i < len(lines) and i < len(lines):
                next_line = lines[i].strip()
                
                # Check if this looks like a matrix row
                # Matrix rows typically have: numbers/variables separated by spaces
                # and might have | symbols or just elements
                if next_line and not any(keyword in next_line.lower() for keyword in ['where', 'given', 'find', 'solve']):
                    # Remove any existing | symbols and split
                    elements = next_line.replace('|', ' ').split()
                    
                    # Check if elements look like matrix entries (alphanumeric, ^, numbers)
                    if elements and len(elements) <= 5 and all(
                        re.match(r'^[a-zA-Z0-9\^_\-\+\*\/]+$', elem) or elem in ['omega', 'alpha', 'beta', 'Delta']
                        for elem in elements
                    ):
                        matrix_lines.append(elements)
                        i += 1
                        if len(matrix_lines) >= 4:  # Max 3x3 matrix + extra safety
                            break
                    else:
                        break
                else:
                    break
            
            # Format matrix if we found one
            if len(matrix_lines) >= 2:  # At least 2 rows for a matrix
                formatted_lines.append('')  # Blank line before matrix
                
                # Calculate column widths
                num_cols = max(len(row) for row in matrix_lines)
                col_widths = [0] * num_cols
                
                for row in matrix_lines:
                    for j, elem in enumerate(row):
                        if j < num_cols:
                            col_widths[j] = max(col_widths[j], len(elem))
                
                # Format each row
                for row in matrix_lines:
                    row_text = '|  '
                    for j, elem in enumerate(row):
                        width = col_widths[j] if j < len(col_widths) else len(elem)
                        row_text += elem.center(width + 2)
                    row_text += '  |'
                    formatted_lines.append(row_text)
                
                formatted_lines.append('')  # Blank line after matrix
        else:
            # Regular line
            formatted_lines.append(line)
            i += 1
    
    result = '\n'.join(formatted_lines)
    
    # Clean up excessive blank lines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    return result.strip()


def extract_with_layout(image: Image.Image) -> str:
    """
    Extract text from image preserving the spatial layout using Tesseract TSV output
    This maintains the original format of matrices, equations, and problem structure
    """
    try:
        # Get data with bounding boxes
        tsv_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
        
        # Filter out empty detections
        tsv_data = tsv_data[tsv_data['conf'] > 20]  # Lower threshold for math symbols
        tsv_data = tsv_data.dropna(subset=['text'])
        tsv_data = tsv_data[tsv_data['text'].str.strip() != '']
        
        if tsv_data.empty:
            return ""
        
        # Sort by vertical position (top to bottom), then horizontal (left to right)
        tsv_data = tsv_data.sort_values(['top', 'left'])
        
        # Group words into lines based on Y-coordinate proximity
        lines = []
        current_line = []
        current_y = None
        y_threshold = 20  # Increased tolerance for matrix rows
        
        for _, row in tsv_data.iterrows():
            word = str(row['text']).strip()
            y_pos = row['top']
            x_pos = row['left']
            width = row['width']
            height = row['height']
            
            # Skip very small detections (noise)
            if width < 5 or height < 5:
                continue
            
            if current_y is None:
                # First word
                current_y = y_pos
                current_line.append({'text': word, 'x': x_pos, 'y': y_pos, 'width': width})
            elif abs(y_pos - current_y) < y_threshold:
                # Same line
                current_line.append({'text': word, 'x': x_pos, 'y': y_pos, 'width': width})
            else:
                # New line
                if current_line:
                    lines.append(current_line)
                current_line = [{'text': word, 'x': x_pos, 'y': y_pos, 'width': width}]
                current_y = y_pos
        
        # Don't forget the last line
        if current_line:
            lines.append(current_line)
        
        # Detect if this is a matrix/determinant structure
        has_vertical_bars = any(
            any(word['text'] in ['|', 'I', 'l'] for word in line)
            for line in lines
        )
        
        # Reconstruct text with proper spacing and structure
        result_lines = []
        
        for line_words in lines:
            if not line_words:
                continue
            
            # Sort words in line by X position
            line_words.sort(key=lambda w: w['x'])
            
            # Check if line contains vertical bars (matrix row)
            has_bars = any(w['text'] in ['|', 'I', 'l'] for w in line_words)
            
            if has_bars and len(line_words) > 2:
                # This is likely a matrix row - format with consistent spacing
                # Remove the vertical bars and focus on content
                content_words = [w for w in line_words if w['text'] not in ['|', 'I', 'l']]
                
                if content_words:
                    # Detect column positions by clustering X coordinates
                    x_positions = [w['x'] for w in content_words]
                    
                    # Simple column detection: group by similar X coords
                    columns = []
                    current_col = [content_words[0]]
                    
                    for i in range(1, len(content_words)):
                        x_gap = content_words[i]['x'] - (current_col[-1]['x'] + current_col[-1]['width'])
                        
                        if x_gap > 30:  # New column
                            columns.append(current_col)
                            current_col = [content_words[i]]
                        else:
                            current_col.append(content_words[i])
                    
                    columns.append(current_col)
                    
                    # Format as matrix row
                    row_text = "|"
                    for col in columns:
                        col_text = " ".join(w['text'] for w in col)
                        row_text += f"  {col_text:^8}"
                    row_text += "  |"
                    
                    result_lines.append(row_text)
            else:
                # Regular text line - build with natural spacing
                line_text = ""
                prev_x_end = None
                
                for word_info in line_words:
                    word = word_info['text']
                    x = word_info['x']
                    
                    if prev_x_end is not None:
                        gap = x - prev_x_end
                        
                        if gap > 40:  # Large gap
                            line_text += "   "
                        elif gap > 15:  # Medium gap
                            line_text += "  "
                        elif gap > 3:  # Normal word spacing
                            line_text += " "
                    
                    line_text += word
                    prev_x_end = x + word_info['width']
                
                result_lines.append(line_text.strip())
        
        return '\n'.join(result_lines)
        
    except Exception as e:
        print(f"Layout extraction error: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_matrix_structure(text: str) -> str:
    """
    Detect and format matrix/determinant structures in the extracted text
    """
    import re
    
    # Look for patterns with vertical bars indicating determinants/matrices
    # Pattern: text containing | symbols with elements between them
    if '|' not in text:
        return text
    
    lines = text.split('\n')
    formatted_lines = []
    in_matrix = False
    matrix_rows = []
    pre_matrix_text = ""
    post_matrix_text = ""
    
    for line in lines:
        # Check if line contains matrix row (has | symbols)
        if '|' in line:
            in_matrix = True
            # Extract content between | symbols
            # Split by | and get non-empty parts
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if parts:
                # Join elements with proper spacing
                matrix_rows.append('| ' + '   '.join(parts) + ' |')
        else:
            if in_matrix and matrix_rows:
                # We've finished collecting matrix rows, format them
                formatted_lines.append(pre_matrix_text)
                formatted_lines.append('')  # Blank line before matrix
                formatted_lines.extend(matrix_rows)
                formatted_lines.append('')  # Blank line after matrix
                matrix_rows = []
                in_matrix = False
                post_matrix_text = line
                formatted_lines.append(line)
            else:
                if not in_matrix and not matrix_rows:
                    pre_matrix_text = line
                    formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
    
    # Handle case where matrix is at the end
    if matrix_rows:
        formatted_lines.append('')
        formatted_lines.extend(matrix_rows)
    
    result = '\n'.join(formatted_lines)
    
    # Clean up multiple blank lines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    return result


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using Tesseract OCR with matrix-aware formatting
    
    Args:
        image_bytes: The image file content as bytes
        
    Returns:
        Extracted text from the image with matrices properly formatted
    """
    if not TESSERACT_AVAILABLE:
        return "OCR not available. Please install Tesseract-OCR."
    
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        original_size = image.size
        print(f"Original image size: {original_size}")
        
        # Convert RGBA to RGB
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        gray_image = image.convert('L')
        best_result = ""
        
        # STRATEGY 1: Use Tesseract with PSM 6 (uniform block) for best overall accuracy
        print("Extracting text with Tesseract PSM 6...")
        try:
            config = '--oem 3 --psm 6'
            text = pytesseract.image_to_string(gray_image, config=config)
            if text and text.strip():
                # Clean and format the text
                cleaned = clean_math_text(text)
                formatted = smart_format_math(cleaned)
                if len(formatted) > 15:
                    best_result = formatted
                    print(f"PSM 6 extracted {len(formatted)} chars")
        except Exception as e:
            print(f"PSM 6 error: {e}")
        
        # STRATEGY 2: Try with preprocessing if poor result
        if len(best_result) < 15:
            print("Trying with enhanced preprocessing...")
            processed = preprocess_image(image, aggressive=False)
            try:
                config = '--oem 3 --psm 6'
                text = pytesseract.image_to_string(processed, config=config)
                if text and text.strip():
                    cleaned = clean_math_text(text)
                    formatted = smart_format_math(cleaned)
                    if len(formatted) > len(best_result):
                        best_result = formatted
                        print(f"Enhanced extraction: {len(formatted)} chars")
            except:
                pass
        
        # STRATEGY 3: Try PSM 4 (single column) as fallback
        if len(best_result) < 15:
            print("Trying PSM 4...")
            try:
                config = '--oem 3 --psm 4'
                text = pytesseract.image_to_string(gray_image, config=config)
                if text and text.strip():
                    cleaned = clean_math_text(text)
                    formatted = smart_format_math(cleaned)
                    if len(formatted) > len(best_result):
                        best_result = formatted
                        print(f"PSM 4 extracted: {len(formatted)} chars")
            except:
                pass
        
        if best_result:
            return best_result
        
        return """Could not extract text clearly from the image.

Please type your math problem directly. For example:
- "Solve x^2 + 5x + 6 = 0"
- "Find derivative of x^3 + 2x^2"
- For determinants:
  Evaluate Delta = 
  | 1      omega   omega^2 |
  | omega  omega^2  1      |
  | omega^2 1      omega   |
  where omega is a cube root of unity."""
        
    except Exception as e:
        print(f"OCR extraction error: {e}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def validate_math_image(image_bytes: bytes) -> bool:
    """
    Validate that the image is suitable for OCR processing
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        width, height = image.size
        if width < 50 or height < 50:
            raise ValueError("Image is too small. Please upload a larger image.")
        
        if width > 4096 or height > 4096:
            raise ValueError("Image is too large. Please upload a smaller image (max 4096x4096).")
        
        if image.format and image.format.lower() not in ['png', 'jpeg', 'jpg', 'gif', 'bmp', 'webp']:
            raise ValueError(f"Unsupported image format: {image.format}")
        
        return True
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")

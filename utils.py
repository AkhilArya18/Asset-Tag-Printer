from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import io

def draw_label(c, x, y, width, height, label_text, barcode_value):
    """
    Draws a single label at the specified coordinates.
    Design:
    - Top: "Property of Aquera" (Bold, Centered)
    - Middle: Barcode (Centered)
    - Bottom: Label Text (Centered)
    """
    c.saveState()
    
    # Text: "Property of Aquera"
    c.setFont("Helvetica-Bold", 8) 
    c.setFillColorRGB(0, 0, 0) # Black text
    
    # Center text horizontally
    title = "Property of Aquera"
    title_width = c.stringWidth(title, "Helvetica-Bold", 8)
    # Moved closer to barcode
    c.drawString(x + (width - title_width) / 2, y + 13 * mm, title)
    
    # Barcode (Middle)
    barcode_height = 4 * mm 
    try:
        barcode = code128.Code128(barcode_value, barHeight=barcode_height, barWidth=0.4)
        
        # Calculate barcode width to center it
        bc_w = barcode.width
        bc_x = x + (width - bc_w) / 2
        bc_y = y + 7 * mm 
        
        barcode.drawOn(c, bc_x, bc_y)
    except Exception:
        pass

    # Text: Label ID (Bottom)
    c.setFont("Helvetica", 8) # Smaller font
    # Using label_text for the human-readable text
    text_width = c.stringWidth(label_text, "Helvetica", 8)
    c.drawString(x + (width - text_width) / 2, y + 3 * mm, label_text)
    
    c.restoreState()

def generate_pdf(items):
    """
    Generates a PDF byte stream from a list of items.
    items: List of dicts {'text': str, 'barcode': str}
    Layout: 3 columns x 10 rows.
    Page Size: A4
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    page_width, page_height = A4
    
    # Grid Configuration
    rows = 10
    cols = 3
    
    # Margins
    left_margin = 5 * mm
    right_margin = 5 * mm
    top_margin = 10 * mm
    bottom_margin = 10 * mm
    
    # Calculate cell size
    available_width = page_width - left_margin - right_margin
    available_height = page_height - top_margin - bottom_margin
    
    col_width = available_width / cols
    row_height = available_height / rows
    
    current_col = 0
    current_row = 0
    
    for item in items:
        # Calculate X and Y
        x = left_margin + (current_col * col_width)
        y = page_height - top_margin - ((current_row + 1) * row_height)
        
        draw_label(c, x, y, col_width, row_height, item['text'], item['barcode'])
        
        # Advance position
        current_col += 1
        if current_col >= cols:
            current_col = 0
            current_row += 1
            
        # Check for new page
        if current_row >= rows:
            c.showPage()
            current_col = 0
            current_row = 0
            
    c.save()
    buffer.seek(0)
    return buffer

def generate_range(start_tag, end_tag):
    """
    Generates a list of tags between start and end.
    Assumes tags end in numbers.
    Example: Aquera00200 -> Aquera00300
    """
    import re
    
    # Split into prefix and number
    match_start = re.match(r"([a-zA-Z]+)(\d+)", start_tag)
    match_end = re.match(r"([a-zA-Z]+)(\d+)", end_tag)
    
    if not match_start or not match_end:
        return [start_tag] # Fallback or error
        
    prefix_start, num_start_str = match_start.groups()
    prefix_end, num_end_str = match_end.groups()
    
    if prefix_start != prefix_end:
        return []

    try:
        start_num = int(num_start_str)
        end_num = int(num_end_str)
        
        # Determine padding length from the input string (e.g. "00200" is len 5)
        # Use the length of the longer string to avoid truncation issues
        zero_fill = max(len(num_start_str), len(num_end_str))
        
        tags = []
        for i in range(start_num, end_num + 1):
            # Format with leading zeros
            tag = f"{prefix_start}{str(i).zfill(zero_fill)}"
            tags.append(tag)
            
        return tags
    except ValueError:
        return []

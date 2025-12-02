import io
import os
import configparser
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader

def create_grid_for_page(page, config):
    """
    Creates a standalone LANDSCAPE PDF overlay with all labels and logo correctly
    oriented for horizontal reading.
    """
    # Get the dimensions of the original PORTRAIT page to define our canvas.
    port_width = float(page.mediabox.width)
    port_height = float(page.mediabox.height)

    # Create a LANDSCAPE canvas by swapping the dimensions.
    width = port_height
    height = port_width
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    # --- 1. Read settings ---
    grid_interval = config.getint('GridSettings', 'grid_spacing')
    line_width = config.getfloat('GridSettings', 'line_width')
    r, g, b = [config.getint('GridColor', c) for c in 'rgb']
    grid_color = Color(r / 255, g / 255, b / 255)

    can.setStrokeColor(grid_color)
    can.setFillColor(grid_color)
    can.setLineWidth(line_width)
    can.setFont("Helvetica", 8)

    # --- 2. Draw Grid and Correctly Oriented Labels ---

    # X-AXIS LABELS (A, B, C...) - Top and Bottom, drawn HORIZONTALLY.
    for x in range(0, int(width), grid_interval):
        if x > 0: can.line(x, 0, x, height)
        label = chr(ord('A') + (x // grid_interval))
        mid_point_x = x + (grid_interval / 2)
        can.drawCentredString(mid_point_x, 10, label)
        can.drawCentredString(mid_point_x, height - 10, label)

    # Y-AXIS LABELS (1, 2, 3...) - Left and Right, drawn HORIZONTALLY.
    for y in range(0, int(height), grid_interval):
        if y > 0: can.line(0, y, width, y)
        label = str((y // grid_interval) + 1)
        mid_point_y = y + (grid_interval / 2)
        
        # --- THIS IS THE FIX ---
        # Draw labels horizontally without rotation.
        can.drawCentredString(15, mid_point_y, label) # Left label
        can.drawCentredString(width - 15, mid_point_y, label) # Right label

    # --- 3. Add the Correctly Oriented (Horizontal) Logo ---
    try:
        logo_path = config.get('Logo', 'logo_path')
        logo_corner = config.get('Logo', 'corner', fallback='top_right')
        logo_height = config.getfloat('Logo', 'height', fallback=30)
        margin = 15

        if logo_path and os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            logo_orig_w, logo_orig_h = logo.getSize()
            aspect = logo_orig_w / logo_orig_h
            logo_width = logo_height * aspect

            if logo_corner == 'bottom_left': x, y = margin, margin
            elif logo_corner == 'bottom_right': x, y = width - logo_width - margin, margin
            elif logo_corner == 'top_left': x, y = margin, height - logo_height - margin
            else: x, y = width - logo_width - margin, height - logo_height - margin
            
            can.drawImage(logo, x, y, width=logo_width, height=logo_height, mask='auto')
    except Exception as e:
        print(f"⚠️  Warning: Could not add logo. Error: {e}")

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def process_pdf_file(input_path, output_path, config):
    """
    Constructs a new landscape PDF by composing the rotated original content and a grid overlay.
    """
    try:
        original_pdf = PdfReader(input_path)
        writer = PdfWriter()

        for page in original_pdf.pages:
            grid_overlay_pdf = create_grid_for_page(page, config)
            land_width = float(page.mediabox.height)
            land_height = float(page.mediabox.width)
            new_page = writer.add_blank_page(width=land_width, height=land_height)
            op = Transformation().rotate(90).translate(tx=land_width, ty=0)
            new_page.merge_transformed_page(page, op)
            new_page.merge_page(grid_overlay_pdf.pages[0])

        with open(output_path, "wb") as f:
            writer.write(f)
        
        print(f"✅ Successfully created '{os.path.basename(output_path)}'")
    except Exception as e:
        print(f"❌ Failed to process '{os.path.basename(input_path)}'. Error: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("❌ Error: `config.ini` not found. Please create it.")
        exit()
    config.read('config.ini')

    input_dir, output_dir = "input", "output"
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input directory '{input_dir}' not found.")
        exit()
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 Starting batch processing of PDFs...")
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_grid.pdf")
            process_pdf_file(input_path, output_path, config)
    print("\n✨ Batch processing complete.")

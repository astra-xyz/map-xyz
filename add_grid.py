import io
import os
import configparser
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader

def create_grid_for_page(page, config):
    """
    Creates a PDF overlay for a page with a grid, coordinates, and a logo,
    using settings from the configuration object.
    """
    # Get page dimensions
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    # --- 1. Read settings from the config object ---
    grid_interval = config.getint('GridSettings', 'grid_spacing')
    line_width = config.getfloat('GridSettings', 'line_width')
    r = config.getint('GridColor', 'r')
    g = config.getint('GridColor', 'g')
    b = config.getint('GridColor', 'b')
    logo_path = config.get('Logo', 'logo_path')
    
    # Create the color object
    grid_color = Color(r/255, g/255, b/255)

    # Set grid style
    can.setStrokeColor(grid_color)
    can.setFillColor(grid_color)
    can.setLineWidth(line_width)
    can.setFont("Helvetica", 8)

    # --- 2. Draw Grid and Dual-Axis Labels ---
    # Vertical lines and labels (Top/Bottom)
    for x in range(0, int(width), grid_interval):
        if x > 0: can.line(x, 0, x, height)
        label = chr(ord('A') + (x // grid_interval))
        can.drawString(x + 5, 5, label)
        can.drawString(x + 5, height - 15, label)

    # Horizontal lines and labels (Left/Right)
    for y in range(0, int(height), grid_interval):
        if y > 0: can.line(0, y, width, y)
        label = str((y // grid_interval) + 1)
        can.drawString(5, y + 5, label)
        can.drawString(width - 20, y + 5, label)

    # --- 3. Add the Logo ---
    if logo_path and os.path.exists(logo_path):
        try:
            # Draw the logo in the bottom-left corner, with a small margin.
            # It's placed at x=5, y=20 to avoid the horizontal grid labels.
            # Using a fixed height and preserveAspectRatio=True is robust.
            logo = ImageReader(logo_path)
            can.drawImage(logo, x=5, y=20, height=30, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"⚠️  Warning: Could not add logo. Error: {e}")
    elif logo_path:
        print(f"⚠️  Warning: Logo file not found at '{logo_path}'.")

    can.save()
    packet.seek(0)
    
    return PdfReader(packet)

def process_pdf_file(input_path, output_path, config):
    """
    Reads an input PDF, adds a configured grid and logo to all pages, and saves it.
    """
    try:
        original_pdf = PdfReader(input_path)
        if not original_pdf.pages:
            print(f"⚠️  Warning: '{os.path.basename(input_path)}' is empty. Skipping.")
            return

        writer = PdfWriter()
        for page in original_pdf.pages:
            grid_overlay_pdf = create_grid_for_page(page, config)
            page.merge_page(grid_overlay_pdf.pages[0])
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)
        
        print(f"✅ Successfully created '{os.path.basename(output_path)}'")

    except Exception as e:
        print(f"❌ Failed to process '{os.path.basename(input_path)}'. Error: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    # --- Read Configuration ---
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("❌ Error: `config.ini` not found. Please create it.")
        exit()
    config.read('config.ini')

    # Define directories
    input_dir = "input"
    output_dir = "output"
    
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input directory '{input_dir}' not found.")
        exit()
        
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 Starting batch processing of PDFs...")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_grid.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Process the file using the loaded configuration
            process_pdf_file(input_path, output_path, config)
            
    print("\n✨ Batch processing complete.")

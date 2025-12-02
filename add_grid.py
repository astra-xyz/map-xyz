import io
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

def create_grid_for_page(page, grid_interval=50, line_width=0.5):
    """
    Creates a PDF overlay for a specific page with a grid and coordinates on all four sides.
    """
    # Get the dimensions from the page's media box
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    # --- 1. Set Custom Grid Color ---
    # Convert RGB (0-255) to a 0-1 scale for reportlab
    grid_color = Color(0/255, 116/255, 166/255)

    # Set grid style
    can.setStrokeColor(grid_color)
    can.setFillColor(grid_color) # Set text color as well
    can.setLineWidth(line_width)
    can.setFont("Helvetica", 8)

    # --- 2. Draw Grid and Dual-Axis Labels ---

    # Draw vertical lines and labels (Top and Bottom)
    for x in range(0, int(width), grid_interval):
        if x > 0:
            can.line(x, 0, x, height)
        
        label = chr(ord('A') + (x // grid_interval))
        # Bottom label
        can.drawString(x + 5, 5, label)
        # Top label
        can.drawString(x + 5, height - 15, label)

    # Draw horizontal lines and labels (Left and Right)
    for y in range(0, int(height), grid_interval):
        if y > 0:
            can.line(0, y, width, y)
            
        label = str((y // grid_interval) + 1)
        # Left label
        can.drawString(5, y + 5, label)
        # Right label
        can.drawString(width - 20, y + 5, label)

    can.save()
    packet.seek(0)
    
    return PdfReader(packet)


def add_grid_to_all_pages(input_pdf, output_pdf, grid_interval=50):
    """
    Reads an input PDF, adds a grid overlay to ALL pages, and saves it to a new file.
    """
    try:
        original_pdf = PdfReader(input_pdf)
        if not original_pdf.pages:
            print(f"Warning: '{input_pdf}' is empty or corrupted. Skipping.")
            return

        writer = PdfWriter()

        for page in original_pdf.pages:
            grid_overlay_pdf = create_grid_for_page(page, grid_interval)
            
            # Merge the grid overlay onto the page
            page.merge_page(grid_overlay_pdf.pages[0])
            writer.add_page(page)

        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        print(f"✅ Successfully created '{output_pdf}' with grids on all pages.")

    except Exception as e:
        print(f"❌ Failed to process '{input_pdf}'. Error: {e}")


# --- Main execution block ---
if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"
    
    os.makedirs(output_dir, exist_ok=True)

    # Set your desired grid size here. 50 is the recommended default for A3.
    grid_spacing = 50
    
    print("Starting batch processing of PDFs...")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_grid.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            add_grid_to_all_pages(input_path, output_path, grid_interval=grid_spacing)
            
    print("\nBatch processing complete.")

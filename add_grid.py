import io
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import grey

def create_grid_for_page(page, grid_interval=50, line_color=grey, line_width=0.5):
    """
    Creates a PDF overlay with a grid and coordinates for a specific page object.
    """
    # Get the dimensions from the page's media box
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    packet = io.BytesIO()
    # Create a new PDF canvas with the same dimensions as the page
    can = canvas.Canvas(packet, pagesize=(width, height))

    # Set grid style
    can.setStrokeColor(line_color)
    can.setLineWidth(line_width)
    can.setFont("Helvetica", 8)

    # Draw vertical lines and labels
    for x in range(0, int(width), grid_interval):
        if x > 0:
            can.line(x, 0, x, height)
        label = chr(ord('A') + (x // grid_interval))
        can.drawString(x + 5, 5, label)

    # Draw horizontal lines and labels
    for y in range(0, int(height), grid_interval):
        if y > 0:
            can.line(0, y, width, y)
        label = str((y // grid_interval) + 1)
        can.drawString(5, y + 5, label)

    can.save()
    packet.seek(0)
    
    # Return the grid as a readable PDF object
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

        # Iterate over all pages in the original PDF
        for page in original_pdf.pages:
            # Create a grid overlay specifically for the current page's dimensions
            grid_overlay_pdf = create_grid_for_page(page, grid_interval)
            
            # Merge the grid overlay onto the page
            # The grid is merged in the background (underneath the original content)
            page.merge_page(grid_overlay_pdf.pages[0])
            
            # Add the modified page to the writer
            writer.add_page(page)

        # Write the final result to the output file
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
            
            # Process the file, adding the grid to all pages
            add_grid_to_all_pages(input_path, output_path, grid_interval=grid_spacing)
            
    print("\nBatch processing complete.")


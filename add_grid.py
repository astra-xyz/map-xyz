import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import grey

def create_grid_overlay(pdf_path, grid_interval=50, line_color=grey, line_width=0.5):
    """
    Creates a PDF overlay with a grid and coordinates.
    """
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    packet = io.BytesIO()
    # Create a new PDF with ReportLab
    can = canvas.Canvas(packet, pagesize=(width, height))

    # Set grid style
    can.setStrokeColor(line_color)
    can.setLineWidth(line_width)
    can.setFont("Helvetica", 8)

    # Draw vertical lines and labels
    for x in range(0, int(width), grid_interval):
        if x > 0:
            can.line(x, 0, x, height)
        # Add letter labels (A, B, C...)
        label = chr(ord('A') + (x // grid_interval))
        can.drawString(x + 2, 5, label)

    # Draw horizontal lines and labels
    for y in range(0, int(height), grid_interval):
        if y > 0:
            can.line(0, y, width, y)
        # Add number labels (1, 2, 3...)
        label = str((y // grid_interval) + 1)
        can.drawString(5, y + 2, label)

    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    
    return PdfReader(packet)


def add_grid_to_pdf(input_pdf, output_pdf, grid_interval=50):
    """
    Reads an input PDF, adds the grid overlay, and saves it to a new file.
    """
    original_pdf = PdfReader(input_pdf)
    grid_overlay_pdf = create_grid_overlay(input_pdf, grid_interval)
    
    writer = PdfWriter()

    # Merge the grid with the first page of the original PDF
    page = original_pdf.pages[0]
    page.merge_page(grid_overlay_pdf.pages[0])
    writer.add_page(page)

    # Add remaining pages from original PDF if they exist
    for i in range(1, len(original_pdf.pages)):
        writer.add_page(original_pdf.pages[i])

    # Write the result to the output file
    with open(output_pdf, "wb") as f:
        writer.write(f)
    
    print(f"Successfully created '{output_pdf}' with a coordinate grid.")


# --- Main execution ---
if __name__ == "__main__":
    input_filename = "plan-ikea-hognoul.pdf"
    output_filename = "plan-with-grid.pdf"
    
    # You can change the grid size by adjusting the interval value
    grid_spacing = 50  # in points (1/72 inch)
    
    add_grid_to_pdf(input_filename, output_filename, grid_interval=grid_spacing)


import json
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Ask user for the input file path
input_file_path = input("Please enter the path of the JSON file: ")

# Open and load the JSON file
with open(input_file_path, 'r') as f:
    data = json.load(f)

# Convert each sub-list into a DataFrame and store in a dictionary
dfs = {k: pd.json_normalize(v) for k, v in data.items()}

# Drop 'rule', 'confidence', and 'fingerprint' columns from each dataframe
for k, df in dfs.items():
    for col in ['rule', 'confidence', 'fingerprint']:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

# Create a buffer for PDF generation
buffer = BytesIO()

# Create a document and set its size
doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

# Style sheet for the Paragraphs
styles = getSampleStyleSheet()

# Story list to hold the table and other elements
story = []

for k, df in dfs.items():
    # Add section title
    title = Paragraph("<u>" + k + "</u>", styles['Heading2'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Convert the dataframe to a list of lists
    table_data = [df.columns.to_list()] + df.values.tolist()

    # Wrap content in each cell within a Paragraph for wrapping
    table_data = [[Paragraph(str(cell), styles['BodyText']) for cell in row] for row in table_data]

    # Set a fixed width for all columns
    num_columns = len(table_data[0])
    total_width = doc.pagesize[0] - 2 * doc.leftMargin  # Subtract margins from total width
    col_widths = [total_width / num_columns for _ in range(num_columns)]

    table = Table(table_data, repeatRows=1, colWidths=col_widths)

    # Add styling to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d3d3d3'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#f5f5f5'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000')
    ])
    table.setStyle(style)

    story.append(table)

# Build the PDF document
doc.build(story)

# Ask user for the output PDF file path
output_pdf_file_path = input("Please enter the path of the output PDF file: ")

# Write the buffer content to a file
with open(output_pdf_file_path, 'wb') as f:
    f.write(buffer.getvalue())

# Close the buffer
buffer.close()

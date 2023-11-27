import pdfplumber


# Path to your PDF file
pdf_path = 'tax_docs/W2_XL_input_clean_1000.pdf'

# Open the PDF
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        # Extract tables from the current page
        tables = page.extract_tables()
    



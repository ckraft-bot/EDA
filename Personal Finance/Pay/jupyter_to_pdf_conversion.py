from nbconvert import PDFExporter
import nbformat

notebook_filename = r'.\Bill History.ipynb'
output_filename = r'.\bill_report.pdf'

with open(notebook_filename) as f:
    notebook_content = nbformat.read(f, as_version=4)

pdf_exporter = PDFExporter()
pdf_data, resources = pdf_exporter.from_notebook_node(notebook_content)

with open(output_filename, 'wb') as f:
    f.write(pdf_data)

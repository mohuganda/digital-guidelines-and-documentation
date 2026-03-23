import opendataloader_pdf

opendataloader_pdf.convert(
    input_path="UCG2023.pdf",
    output_dir="odl_output",
    format="markdown",
    table_method="cluster",
    reading_order="xycut",
    quiet=False
)

print("Done. Check the 'odl_output' folder.")

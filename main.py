import os
import invoiceParser
import fitz
import pandas as pd

# Globals
invoices_dir = os.getcwd() + "/invoices"
pdf_files = [f for f in os.listdir(invoices_dir) if f.lower().endswith(".pdf")]
if not pdf_files:
    raise FileNotFoundError("No PDF files found in the /invoices directory.")
label_path = os.path.join(invoices_dir, pdf_files[0])

def extract_info(pdf_path):
    df = pd.DataFrame(columns=["shipping_address", "sku", "quantity"])
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):

        shipping_address = invoiceParser.extract_label_info(i, page)
        if shipping_address:
            sku, quantity = invoiceParser.extract_sku_info(i, page)
            print(sku, quantity)

            df.loc[len(df)] = {
                "shipping_address": shipping_address,
                "sku": sku,
                "quantity": quantity
            }

    return df


if __name__ == "__main__":
    labels_dataframe = extract_info(label_path)
    labels_dataframe.to_csv("outputs.csv", index=False)
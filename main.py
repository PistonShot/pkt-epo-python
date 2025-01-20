import pdfplumber
import requests
import tempfile
# will extract all header of EVERY TABLE in the document
def extract_table_header(pdf_url):
    extracted_data = []

    try:
        # Download the PDF file from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the PDF to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(response.content)
            temp_file_path = temp_pdf.name  # Store the temporary file path

        # Open the PDF file with pdfplumber
        with pdfplumber.open(temp_file_path) as pdf:
            for page in pdf.pages:
                # Extract tables from the page
                tables = page.extract_tables()
                
                for i in range(len(tables)):
                    temp_dict = {}
                    temp_dict = {"table_id": i , "header":tables[i][0]}
                    extracted_data.append(temp_dict) # tables[i][0] will extract first row = table header of each table

    except requests.RequestException as e:
        print(f"Error downloading the PDF: {e}")
    except Exception as e:
        print(f"Error processing the PDF: {e}")

    finally:
        # Clean up the temporary file
        try:
            import os
            os.remove(temp_file_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up temporary file: {cleanup_error}")

    return extracted_data

def extract_table_data_from_url(pdf_url, table_id, selected_header_index):
    extracted_data = []

    try:
        # Download the PDF file from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the PDF to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(response.content)
            temp_file_path = temp_pdf.name  # Store the temporary file path

        # Open the PDF file with pdfplumber
        with pdfplumber.open(temp_file_path) as pdf:
            for page in pdf.pages:
                # Extract tables from the page
                tables = page.extract_tables()
                table = tables[table_id]
                # Iterate over each row in the table
                for i in range(1,len(table)): # skip header row
                    # Debugging: Print the length of the row
                    # print(f"Row Length: {len(table[i])}, Row: {table[i]}")
                    try:
                        # Extract data from the row
                        name = table[i][selected_header_index[0]]
                        quantity = table[i][selected_header_index[1]]
                        unit_price = table[i][selected_header_index[2]]
                        total = table[i][selected_header_index[3]]
                        if name == '' or quantity == ''or unit_price == '' or total == '' :
                            continue

                        # Append the extracted data to the list
                        extracted_data.append({
                            "Name": name,
                            "Quantity": quantity,
                            "Unit Price": unit_price,
                            "Total": total
                        })
                    except (ValueError, IndexError):
                        # Skip rows with invalid data
                        continue

    except requests.RequestException as e:
        print(f"Error downloading the PDF: {e}")
    except Exception as e:
        print(f"Error processing the PDF: {e}")

    finally:
        # Clean up the temporary file
        try:
            import os
            os.remove(temp_file_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up temporary file: {cleanup_error}")

    return extracted_data

# Example usage
url = "https://drive.usercontent.google.com/uc?id=1oZH31THekNqytulznj4muadluP3FPyVU&authuser=0&export=download"  # Replace with the actual URL of the PDF
data = extract_table_data_from_url(url,0,[1,2,3,4])
# headers = extract_table_header(url)
# Print the extracted data
print(f"Extracted Data: \n{data}")





from flask import Flask, request, jsonify
import requests
import tempfile
import pdfplumber
import os

# Initialize Flask app
app = Flask(__name__)

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
                    temp_dict = {"table_id": i, "header": tables[i][0]}  # Extract first row as header
                    extracted_data.append(temp_dict)

    except requests.RequestException as e:
        return {"error": f"Error downloading the PDF: {e}"}, 400
    except Exception as e:
        return {"error": f"Error processing the PDF: {e}"}, 500

    finally:
        # Clean up the temporary file
        try:
            os.remove(temp_file_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up temporary file: {cleanup_error}")

    return extracted_data, 200

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
                for i in range(1, len(table)):  # skip header row
                    try:
                        # Extract data from the row
                        name = table[i][selected_header_index[0]]
                        quantity = table[i][selected_header_index[1]]
                        unit_price = table[i][selected_header_index[2]]
                        total = table[i][selected_header_index[3]]
                        if name == '' or quantity == '' or unit_price == '' or total == '':
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
            os.remove(temp_file_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up temporary file: {cleanup_error}")

    return extracted_data

@app.route('/pdf-extract/get-header', methods=['POST'])
def get_pdf_header():
    try:
        # Parse the JSON request body
        data = request.get_json()
        if not data or 'pdf_url' not in data:
            return jsonify({"error": "Invalid request. 'pdf_url' is required."}), 400

        pdf_url = data['pdf_url']

        # Extract table headers from the PDF
        extracted_data, status_code = extract_table_header(pdf_url)
        return jsonify(extracted_data), status_code

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/pdf-extract/get-items', methods=['POST'])
def get_pdf_items():
    try:
        # Parse the JSON request body
        data = request.get_json()
        if not data or 'pdf_url' not in data or 'table_id' not in data or 'selected_header_index' not in data or 'header' not in data:
            return jsonify({"error": "Invalid request. 'pdf_url', 'table_id', 'header' and 'selected_header_index' are required."}), 400
        
        if len(data['selected_header_index']) != 4:
             return jsonify({"error": "Invalid request.'selected_header_index' does not have exactly 4 indexes."}), 400

        if max(data['selected_header_index']) >= len(data['header']):
            return jsonify({"error": "Invalid request.'selected_header_index' contains index out of bound of table 'header'."}), 400

        pdf_url = data['pdf_url']
        table_id = data['table_id']
        selected_header_index = data['selected_header_index']

        # Extract table data from the PDF
        extracted_data = extract_table_data_from_url(pdf_url, table_id, selected_header_index)
        return jsonify(extracted_data), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True,port=80)
import requests

# URL of the raw DICOM file
url = "https://raw.githubusercontent.com/marcodebe/dicom-ecg-plot/master/sample_files/anonymous_ecg.dcm"

# Output file name
output_file = "anonymous_ecg.dcm"

try:
    # Send a GET request to download the file
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Write the content to a local file
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"File downloaded successfully: {output_file}")

except requests.exceptions.RequestException as e:
    print(f"Error downloading the file: {e}")

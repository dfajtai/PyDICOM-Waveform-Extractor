import os
import shutil
from main import process_dicom_folder
from dcm_waveform_extractor.config_loader import load_config

def run_test():
    """
    Runs a test of the DICOM processing pipeline using sample data.
    """
    # Define sample input and output folders
    sample_input_folder = "./sample"
    test_output_folder = "./test_output"

    # Ensure the test output folder is clean
    if os.path.exists(test_output_folder):
        shutil.rmtree(test_output_folder)  # Remove existing test output directory
    os.makedirs(test_output_folder, exist_ok=True)

    # Load configuration from the default config.json
    config_path = "./config.json"
    config = load_config(config_path)

    # Override configuration for testing
    input_dir = sample_input_folder  # Use the sample folder as input
    output_dir = test_output_folder  # Use a dedicated test output folder
    metadata_format = config.get("metadata_format", "json")
    output_structure = config.get("output_structure", "{PATIENT_ID}/{STUDY_DATE}/{STUDY_TIME}/{CHANNEL}")
    file_format_mask = config.get("file_format_mask", ["*.dcm", "*.ima", "*"])

    print("Running test with the following configuration:")
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print(f"Metadata format: {metadata_format}")
    print(f"Output structure: {output_structure}")
    print(f"File format mask: {file_format_mask}")

    # Run the processing function
    process_dicom_folder(input_dir, output_dir, metadata_format, output_structure, file_format_mask,
                         raise_error=True)

    # Validate the results
    validate_test_results(test_output_folder)

def run_pydicom_test():
    try:
        from pydicom import examples
    except ImportError as e:
        print(e)
        return
    
    from dcm_waveform_extractor.data_extraction import extract_waveform_data_form_dcm
    dcm_data = examples.waveform
    
    try:
        waveform_df_dict, content_info = extract_waveform_data_form_dcm(dcm_data)
        
        print(content_info)
        print(waveform_df_dict)
        
    except Exception as e:
        print(e)
        
    

def validate_test_results(output_folder):
    """
    Validates the test results by checking for generated files in the output folder.

    Parameters:
        output_folder (str): Path to the folder where results are saved.
    
    Returns:
        None
    """
    if not os.path.exists(output_folder):
        print("Test failed: Output folder was not created.")
        return

    # Check for subfolders and files in the output directory
    generated_files = []
    for root, _, files in os.walk(output_folder):
        for file in files:
            generated_files.append(os.path.join(root, file))

    if not generated_files:
        print("Test failed: No files were generated in the output folder.")
        return

    print("Test passed: The following files were generated:")
    for file in generated_files:
        print(f" - {file}")


if __name__ == "__main__":
    run_pydicom_test()
    run_test()

"""
PyDICOM-Waveform-Extractor: Extracting waveforms so you don’t have to.

This lightweight MVP (Minimal Viable Product) is here to save the day for those who
prefer not to reinvent the wheel—or spend two minutes searching for a solution. 
Designed with just enough functionality to get the job done, this tool extracts 
waveform data from DICOM files and outputs it in CSV, JSON, or YAML formats.

⚠️ WARNING: This code doesn't do GDPR compliance, data anonymization, or any of that 
fancy stuff. Use responsibly and don't blame us if your boss starts asking questions.

Features:
- Extracts waveform data from DICOM files.
- Outputs results in plain CSV and metadata in JSON/YAML formats.
- Provides a command-line interface because GUIs are overrated.

What this *doesn't* do:
- Signal processing? Nope.
- Interactive plotting? Sorry.
- Advanced querying or registries? Not happening here.
- Replace your need to actually understand what you're doing? Absolutely not.

If you're looking for advanced features, you're in the wrong place. But hey, if
you just want to get some waveforms out of DICOM files without breaking a sweat,
you've come to the right script.

Made with just enough effort to work. You're welcome.
"""

import argparse
import logging
from dcm_waveform_extractor.config_loader import load_config
from dcm_waveform_extractor.data_extraction import extract_waveform_data_form_dcm, extract_dcm_id_info
from dcm_waveform_extractor.metadata_writers import store_json, store_yaml
import os
import glob
import random

# Configure logging
LOG_FILE = "error.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_output_path(base_dir: str, structure: str, metadata: dict) -> str:
    """
    Creates an output directory path based on a structure template and metadata.

    Parameters:
        base_dir (str): The base output directory.
        structure (str): The folder structure template (e.g., "{PatientID}/{StudyDate}/{StudyTime}").
        metadata (dict): Metadata dictionary containing tags like PatientID, StudyDate, etc.

    Returns:
        str: The full path of the output directory.
    """
    try:
        # Replace placeholders in the structure with actual metadata values
        sub_path = structure.format(
            PATIENT_ID=metadata.get("id", "UnknownPatient"),
            STUDY_DATE=metadata.get("study_date", "UnknownDate"),
            STUDY_TIME=metadata.get("study_time", "UnknownTime")
        )
        full_path = os.path.join(base_dir, sub_path)

        # Create the directory if it doesn't exist
        os.makedirs(full_path, exist_ok=True)

        return full_path

    except KeyError as e:
        raise ValueError(f"Missing required metadata key for folder structure: {e}")


def process_dicom_folder(input_folder: str, output_folder: str, metadata_format: str, output_structure: str, file_format_mask: list,
                         raise_error:bool=False):
    """
    Processes all DICOM files in the input folder and saves extracted data.

    Parameters:
        input_folder (str): Path to the folder containing DICOM files.
        output_folder (str): Path to the folder where output files will be saved.
        metadata_format (str): Format for saving metadata ("json" or "yaml").
        output_structure (str): Folder structure template for organizing output files.
        file_format_mask (list): List of file format patterns to search for (e.g., ["*.dcm", "*.ima", "*"]).
        raise_error (bool): Whether or not raise error for outside handling

    Returns:
        None
    """
    
    # Collect all files matching the specified masks
    dicom_files = []
    for mask in file_format_mask:
        dicom_files.extend(glob.glob(os.path.join(input_folder, mask)))
    
    if not dicom_files:
        print(f"No DICOM files found in {input_folder} with specified masks: {file_format_mask}.")
        return
    
    os.makedirs(output_folder, exist_ok=True)
    
    
    if not dicom_files:
        print(f"No DICOM files found in {input_folder}.")
        return
    
    for dicom_file in dicom_files:
        try:
            # Validate and extract basic info before processing
            info, is_valid = extract_dcm_id_info(dicom_file)
            if not is_valid:
                print(f"Skipping file {dicom_file}: Not a valid waveform series.")
                continue

            # Ensure default values for StudyDate and StudyTime if missing
            info["study_date"] = info.get("study_date", "UnknownDate")
            info["study_time"] = info.get("study_time", "UnknownTime")

            # Extract waveform data and metadata
            waveform_data, content_info = extract_waveform_data_form_dcm(dicom_file)

            # Process each channel group
            for group_name, df in waveform_data.items():
                # Create a custom output path for each channel group
                custom_output_folder = create_output_path(
                    output_folder,
                    output_structure,
                    info
                )

                # Save CSV for the channel group
                csv_path = os.path.join(custom_output_folder, f"{group_name}.csv")
                df.to_csv(csv_path, index=False)
                print(f"Saved CSV: {csv_path}")

            # Save metadata to JSON or YAML based on config
            metadata_path = os.path.join(custom_output_folder, f"metadata.{metadata_format}")
            
            if metadata_format == "json":
                store_json(content_info, metadata_path)
            elif metadata_format == "yaml":
                store_yaml(content_info, metadata_path)

            print(f"Saved metadata: {metadata_path}")

        except Exception as e:
            error_message = f"Error processing {dicom_file}: {e}"
            print(error_message)
            logging.error(error_message)  # Log the error to the log file
            if raise_error:
                raise e
            
def show_tip_of_the_day():
    """
    Displays a random 'Tip of the Day'.
    Take it or leave it.
    """
    tips = [
        "If you're going to rely on someone else's work, at least give them proper credit.",
        "MVP stands for 'Minimal Viable Product,' not 'Most Valuable Project.' Manage your expectations.",
        "When you ask for the bare minimum, don't expect the holy grail.",
        "A little gratitude goes a long way—just saying.",
        "If you think this is good, imagine what I didn’t give you.",
        "Building something great takes time. Handing over an MVP? Not so much.",
        "Treat your developers well—they might not hand over just the glaze next time.",
        "Remember, an MVP is like a demo track—it’s not the full album.",
        "If you want more than this MVP, maybe try asking nicely next time.",
        "When you say ‘just make it work,’ don’t expect bells and whistles."
    ]

    # Print a random tip
    print(f"\n💡 Tip of the Day: {random.choice(tips)}\n")


def add_spicy_help(parser):
    """
    Extends the argparse help menu with some extra helpful information.
    """
    spicy_puns = [
        "PyDICOM-Waveform-Extractor: Made this so you don't have to. You're welcome.",
        "PyDICOM-Waveform-Extractor: Extracting waveforms because some people can't.",
        "PyDICOM-Waveform-Extractor: Because reading the manual is hard.",
        "PyDICOM-Waveform-Extractor: An MVP brought to you by years of effort and two minutes of patience.",
        "PyDICOM-Waveform-Extractor: Remember, MVP stands for 'Minimal Viable Product,' not 'Most Valuable Project.'",
        "PyDICOM-Waveform-Extractor: Waveforms extracted. Gratitude? Still pending."
    ]

    # Pick a random pun
    spicy_message = random.choice(spicy_puns)

    # Append it to the default help text
    parser.description = f"{parser.description}\n\n{spicy_message}"

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Process DICOM files to extract waveform data and save it as CSV along with metadata."
    )

    # Add arguments for CLI
    parser.add_argument(
        "--config", "-c",
        type=str, 
        default="./config.json", 
        help="Path to the configuration file (default: './config.json')."
    )
    parser.add_argument(
        "--input_dir", "-i",
        type=str, 
        help="Override the input directory specified in the config file."
    )
    parser.add_argument(
        "--output_dir", "-o",
        type=str, 
        help="Override the output directory specified in the config file."
    )
    parser.add_argument(
        "--metadata_format", 
        type=str, 
        choices=["json", "yaml"], 
        help="Override the metadata format specified in the config file (options: 'json', 'yaml')."
    )
    parser.add_argument(
        "--output_structure",
        type=str,
        help="Override the output folder structure specified in the config file. Use placeholders like '{PATIENT_ID}/{STUDY_DATE}/{STUDY_TIME}'."
    )

    parser.add_argument(
        "--file_format_mask",
        type=str,
        nargs="+",  # Accept multiple values as a list
        help="Override the file format mask specified in the config file. Example: '*.dcm *.ima *'."
    )

    # Add spicy help with random puns
    add_spicy_help(parser)
    
    # Parse arguments
    args = parser.parse_args()
    try:

        # Load or generate configuration
        config = load_config(args.config)

        # Override config values with CLI arguments if provided
        input_dir = args.input_dir if args.input_dir else config.get("input_dir", "./dicom_files")
        output_dir = args.output_dir if args.output_dir else config.get("output_dir", "./waveform_dir")
        metadata_format = args.metadata_format if args.metadata_format else config.get("metadata_format", "json").lower()
        
        # Default folder structure is {PATIENT_ID}/{STUDY_DATE}/{STUDY_TIME} if not provided
        output_structure = args.output_structure if args.output_structure else config.get("output_structure", "{PATIENT_ID}/{STUDY_DATE}/{STUDY_TIME}")

        # Get file format mask from configuration or CLI arguments
        file_format_mask = args.file_format_mask if args.file_format_mask else config.get("file_format_mask", ["*.dcm"])
        
        # Validate metadata format
        if metadata_format not in ["json", "yaml"]:
            raise ValueError("Invalid metadata format. Use 'json' or 'yaml'.")

        # Process DICOM files
        process_dicom_folder(input_dir, output_dir, metadata_format, output_structure, file_format_mask)

    except Exception as e:
        # TODO: Add proper error handling... or not.
        
        error_message = f"Critical error occurred: {e}"
        logging.error(error_message)  # Log critical errors to the log file
        print(error_message)  # Print critical errors to the console

if __name__ == "__main__":
    """
    Main entry point for PyDICOM-Waveform-Extractor.
    """
    show_tip_of_the_day()  # Display a random tip for some lighthearted wisdom
    
    # Rest of your script logic here (e.g., argument parsing, processing)
    main()
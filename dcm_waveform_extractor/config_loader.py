import os
import json
from collections import OrderedDict

# Define accepted metadata tags
ACCEPTED_METADATA_TAGS = [
    "ACCESSION_NUMBER",
    "PATIENT_NAME",
    "PATIENT_ID",
    "STUDY_DATE",
    "STUDY_TIME",
    "SERIES_DESCRIPTION",
    "MODALITY"
]

def sanitize_output_structure(structure: str) -> str:
    """
    Sanitizes the output structure by ensuring only accepted metadata tags are used.

    Parameters:
        structure (str): The folder structure template.

    Returns:
        str: The sanitized folder structure.

    Raises:
        ValueError: If unsupported tags are found in the structure.
    """
    # Extract placeholders (e.g., {PATIENT_ID}, {STUDY_DATE})
    placeholders = [part.strip("{}") for part in structure.split("/") if part.startswith("{") and part.endswith("}")]

    # Check for unsupported tags
    unsupported_tags = [tag for tag in placeholders if tag not in ACCEPTED_METADATA_TAGS]
    if unsupported_tags:
        raise ValueError(f"Unsupported metadata tags found in output_structure: {unsupported_tags}. "
                         f"Accepted tags are: {ACCEPTED_METADATA_TAGS}")

    return structure


def generate_default_config(config_path: str):
    """
    Generates a default configuration file if it doesn't already exist.

    Parameters:
        config_path (str): Path to the configuration file.

    Returns:
        None
    """
    if not os.path.exists(config_path):
        print(f"Config file '{config_path}' not found. Generating default config...")

        # Define default configuration
        default_config = OrderedDict({
            "input_dir": "./dicom_files",  # Folder containing DICOM files
            "output_dir": "./output_csv",  # Folder for saving output files
            "metadata_format": "json",     # Options: "json" or "yaml"
            "output_structure": "{PATIENT_ID}/{STUDY_DATE}/{STUDY_TIME}",  # Default folder structure
            "file_format_mask": ["*.dcm", "*.ima", "*"]
        })

        # Create the config file
        with open(config_path, "w") as config_file:
            json.dump(default_config, config_file, indent=4)
        
        print(f"Default config file created at '{config_path}'.")
    else:
        print(f"Config file '{config_path}' already exists.")


def load_config(config_path: str) -> dict:
    """
    Loads a configuration file in JSON format. If the file does not exist,
    generates a default configuration and then loads it.

    Parameters:
        config_path (str): Path to the JSON configuration file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    # Ensure the config file exists or create a default one
    generate_default_config(config_path)

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        # Sanitize output_structure
        config["output_structure"] = sanitize_output_structure(config.get("output_structure", "{PATIENT_ID}/{STUDY_DATE}/{STUDY_TIME}"))

        
        # Ensure file_format_mask is properly set
        if not isinstance(config.get("file_format_mask"), list):
            config["file_format_mask"] = ["*.dcm", "*.ima", "*"]
        
        return config

    except ValueError as e:
        print(f"Configuration error: {e}")
        raise e

    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        raise e

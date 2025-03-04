from typing import Optional

import datetime
import os

from collections import OrderedDict

import numpy as np
import pandas as pd
from pydicom import dcmread
from pydicom.dataset import Dataset


def parse_datetime(date: str, time: str) -> Optional[datetime.datetime]:
    """Parses date and time strings into a datetime object."""
    try:
        return datetime.datetime.strptime(f"{date}#{time}", "%Y%m%d#%H%M%S.%f")
    except (ValueError, AttributeError):
        return None
    

def format_datetime_fields(
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime
) -> dict:
    """
    Formats start and end datetime objects into strings.

    Parameters:
        start_datetime (datetime.datetime): The start datetime object.
        end_datetime (datetime.datetime): The end datetime object.

    Returns:
        dict: A dictionary containing formatted "start" and "end" fields.
            - "start": Formatted start datetime as a string ("%Y-%m-%d %H:%M:%S.%f").
            - "end": Formatted end datetime as a string ("%Y-%m-%d %H:%M:%S.%f").
    """
    return {
        "start": start_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "end": end_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    }


def extract_dcm_id_info(dcm_path: str) -> tuple[Optional[dict],bool]:
    """
    Extracts basic identification and metadata information from a DICOM file.

    Parameters:
        dcm_path (str): The file path to the DICOM file.

    Returns:
        Optional[dict]: An ordered dictionary containing the following metadata:
            - "series" (str): The series description of the DICOM file.
            - "name" (str): The patient's name.
            - "id" (str): The patient's ID.
            - "accession_number" (str): The accession number of the DICOM file.
            - "content_datetime" (datetime.datetime, optional): The content date and time as a `datetime` object.
        
        Returns `None` if the file does not exist or cannot be read.

    Raises:
        None explicitly, but may raise exceptions if the DICOM file is malformed or missing required attributes.
    """
    
    
    if not os.path.exists(dcm_path):
        return {}, False
    D = dcmread(dcm_path,stop_before_pixels=True, force=True)

    info = OrderedDict()
    info["series"] = D.get("SeriesDescription","UnknownSeries")
    info["name"] = str(D.get("PatientName","UnknownPatient"))
    info["id"] = str(D.get("PatientID","UnknownPatientID"))
    info["accession_number"] = str(D.get("AccessionNumber","UnknownAccession"))
    info["sop_instance_uid"] = str(D.get("SOPInstanceUID",None))
        
    try:
        date = str(D.ContentDate).strip().replace(" ","")
        time = str(D.ContentTime).strip().replace(" ","")
        info["content_datetime"] = datetime.datetime.strptime(f"{date}#{time}","%Y%m%d#%H%M%S.%f")
    except:
        print(f"Unable to extract time informations")
        
    has_waveform = not isinstance(D.get([0x5400, 0x0100]),type(None))
    
    return info, has_waveform


def safe_extract_channel_def(sequence, tag_path, default=None, nested=False):
    """
    Safely extracts values from a DICOM channel definition sequence using the provided tag path.

    Parameters:
        sequence (list): The DICOM channel definition sequence (e.g., channel_definition_sequence).
        tag_path (list): The tag path to extract the value (e.g., [0x003a, 0x0203]).
        default: The default value to return if extraction fails.
        nested (bool): If True, extracts nested values from sequences within the main sequence.

    Returns:
        list: A list of extracted values or default values if extraction fails.
    """
    results = []
    idx = 1
    for item in sequence:
        try:
            # Extract the value at the specified tag path
            value = item.get(tag_path).value
            if nested and len(value) > 0:
                # Extract nested value if required
                value = value[0].get([0x0008, 0x0104]).value
            results.append(value)
        except (AttributeError, IndexError, TypeError):
            # Return default value if extraction fails
            results.append(f"unk.{default}_{idx}")
        idx+=1
    return results




def extract_waveform_data_form_dcm(
    dcm: str | Dataset,
    relevant_channels: Optional[dict] = None,
    extract_data: bool = True,
    custom_parser: bool = False,
    datetime_col: str = "DateTime",
    time_col: str = "Time"
    ) -> Optional[tuple]:
    """
    Reads waveform data from an angiography-related DICOM file and extracts it into structured data.

    Parameters:
        dcm (str | pydicom.Dataset): The file path to the DICOM file or a DICOM Dataset 
        relevant_channels (Optional[dict]): A dictionary specifying which channels to extract. 
            Keys are channel groups (e.g., "PRESSURE"), and values are lists of channel labels to include.
            If `None`, all channels are extracted.
        extract_data (bool): Whether to extract waveform data. Defaults to `True`.
        custom_parser (bool): Whether to use a custom parser for waveform data extraction. Defaults to `False`.
        datetime_col (str): The name of the column in the output DataFrame containing datetime information. Defaults to "DateTime".
        time_col (str): The name of the column in the output DataFrame containing time information. Defaults to "Time".

    Returns:
        Optional[tuple]: A tuple containing:
            - waveform_df_dict (dict): A dictionary where keys are channel groups (e.g., "PRESSURE") 
              and values are pandas DataFrames containing waveform data with columns for time, channel labels, 
              and optionally other metadata.
            - content_info (dict): A dictionary containing metadata about the DICOM file, including:
                - "name" (str): Patient's name.
                - "id" (str): Patient's ID.
                - "series" (str): Series description of the DICOM file.
                - "start" (str): Start datetime of the waveform recording.
                - "end" (str): End datetime of the waveform recording.
                - "duration" (float): Duration of the recording in seconds.
                - "frequency" (float): Sampling frequency of the waveform data.
                - "number_of_samples" (int): Total number of samples in the waveform data.
                - "pressure_sites" (dict): Mapping of pressure site labels to their meanings.
                - "channel_info" (dict): Detailed channel information, including labels, units, meanings, sensitivity, baselines, and correction factors.

    Raises:
        FileNotFoundError: If the specified DICOM file does not exist.
        AttributeError: If required attributes are missing or malformed in the DICOM file.

    Notes:
        - This function assumes that waveform data is stored in a specific format within the DICOM file 
          and may not work for all types of DICOM files.
        - If `custom_parser` is set to `True`, a custom method is used to parse raw waveform data into numerical values. 
          Otherwise, it relies on pydicom's built-in `waveform_array` method.

    Example Usage:
        >>> dicom_file = "/path/to/dicom/file.dcm"
        >>> relevant_channels = {"PRESSURE": ["Channel1", "Channel2"]}
        >>> waveforms, info = read_angio_dcm(dicom_file, relevant_channels)
        >>> print(info["name"], info["start"])
        >>> print(waveforms["PRESSURE"].head())
    """
    if not isinstance(dcm, Dataset):
        assert isinstance(dcm,str)
        dicom_file = dcm
        
        if not os.path.exists(dcm):
            raise AttributeError("DCM file '{0}' not valid.".format(dicom_file))
        
        dcm = dcmread(dcm, force = True)
        
    else:
        dicom_file = dcm.get("SOPInstanceUID")
        
    assert isinstance(dcm,Dataset)
    
    sop_instance_uid = str(dcm.get("SOPInstanceUID",None))
    patient_name = dcm.get('PatientName')
    patient_id = dcm.get('PatientID')
    accession_number = dcm.get('AccessionNumber')
    content_date = dcm.get('ContentDate')
    content_time = dcm.get('ContentTime')
    if float(content_time)==0.0:
        content_time = dcm.get('InstanceCreationTime')
    content_time = str(float(content_time)+0.0)
    
    series_description = dcm.get('SeriesDescription')

    start_datetime = parse_datetime(content_date,content_time)

    try:
        waveform_base = dcm.get([0x5400, 0x0100]).value

    except AttributeError:
        raise AttributeError("DCM file '{0}' not valid.".format(dicom_file))

    waveform_df_dict = {}

    freq = waveform_base[0].get([0x003a, 0x001a]).value
    num_of_samples = waveform_base[0].get([0x003a, 0x0010]).value
    duration = float(num_of_samples)/float(freq)
    end_datetime = start_datetime+datetime.timedelta(seconds=float(num_of_samples-1)/float(freq))
    content_info = OrderedDict({"name":str(patient_name),
                    "id":str(patient_id),
                    "SOPInstanceUID":sop_instance_uid,
                    "accession":str(accession_number),
                    "series":str(series_description),
                    **format_datetime_fields(start_datetime, end_datetime),
                    "duration":duration,
                    "frequency":freq,
                    "number_of_samples": num_of_samples,
                    "pressure_sites":{},
                    "channel_info":{}})


    for i_w in range(len(waveform_base)):
        channel_group = waveform_base[i_w].get([0x003a, 0x0020]).value
        # print(channel_group)

        sampling_frequency = waveform_base[i_w].get([0x003a, 0x001a]).value
        # num_of_samples =  waveform_base[i_w].get([0x003a, 0x0010]).value

        channel_definition_sequence = waveform_base[i_w].get([0x003a, 0x0200]).value
        # Safely extract channel information
        channel_count = len(channel_definition_sequence)
        channel_label = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x0203], default="label")
        channel_bits = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x021a], default=0)
        channel_sensitivity = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x0210], default=1.0)
        channel_sensitivity_correction_factor = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x0212], default=1.0)
        channel_baseline = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x0213], default=0)

        # Safely extract nested channel information
        channel_meaning = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x0208], default="meaning", nested=True)
        channel_units = safe_extract_channel_def(channel_definition_sequence, [0x003a, 0x0211], default="unit", nested=True)
        
        
        channel_info = OrderedDict({"labels":channel_label,
                        "unit":channel_units,
                        "meaning":channel_meaning,
                        "sensitivity":channel_sensitivity,
                        "baseline":channel_baseline,
                        "corr.factor":channel_sensitivity_correction_factor})
        content_info["channel_info"][channel_group] = channel_info

        if not extract_data:
            continue

        if custom_parser:
            # signal_bit_count = np.sum(np.array(channel_bits))
            waveform_data = waveform_base[i_w].get([0x5400, 0x1010]).value

            # parsed_data = read_byte_array(waveform_data)
            parsed_data = np.frombuffer(waveform_data,np.int16)
            parsed_data = parsed_data.reshape((int(parsed_data.shape[0]/channel_count),channel_count))
            # parsed_data = parsed_data*np.array(channel_sensitivity).T
            parsed_data = (np.array(channel_baseline).T + parsed_data) * np.array(channel_sensitivity).T * np.array(channel_sensitivity_correction_factor).T
        else:
            parsed_data = dcm.waveform_array(i_w)

        time = np.arange(0,(parsed_data.shape[0])/float(sampling_frequency),step= 1.0/float(sampling_frequency))

        if time.shape[0] != parsed_data.shape[0] :
            print(f"Correcting length mismatch. (number of timepoints: {time.shape[0]},number of stored data points: {parsed_data.shape[0]})")
            min_shape = min([time.shape[0],parsed_data.shape[0]])
            time = time[:min_shape]
            parsed_data = parsed_data[:min_shape,:]

        df = pd.DataFrame()
        df[time_col] = time
        for channel_index in range(len(channel_label)):
            if(str(channel_group)==str("PRESSURE")):
                content_info["pressure_sites"][channel_label[channel_index]] = channel_meaning[channel_index]
            # df["{0}[{1}]".format(channel_label[channel_index],channel_units[channel_index])] = parsed_data[:,channel_index]
            df["{0}".format(channel_label[channel_index])] = parsed_data[:,channel_index]

        if isinstance(relevant_channels,dict):
            if isinstance(relevant_channels.get(channel_group),list):
                accepted_colnames = relevant_channels.get(channel_group)
                # selected_cols = [time_col] + [colname for colname in df.columns if any([str(colname).startswith(acn + "[") for acn in accepted_colnames])]
                selected_cols = [time_col] + [colname for colname in df.columns if any([str(colname).startswith(acn) for acn in accepted_colnames])]
                df = df[selected_cols]
            else:
                continue

        df[datetime_col] = df[time_col].apply(lambda x: start_datetime+datetime.timedelta(seconds=float(x)))

        waveform_df_dict[channel_group] = df

    return waveform_df_dict, content_info
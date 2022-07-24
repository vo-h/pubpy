import requests
from typing import Tuple, List
import copy
import re


def get_total_pages(annotation: str = "Boiling Point", heading_type: str = "Compound") -> int:
    """Get the total # of pages of a given (annotation, heading_type) combination.

    Args:
        annotation (str, optional): Defaults to "Boiling Point".
        heading_type (str, optional): Defaults to "Compound".

    Returns:
        int: # of pages.
    """
    annotation = annotation.replace(" ", "%20")
    res = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/{annotation}/JSON?heading_type={heading_type}")
    return int(res.json()["Annotations"]["TotalPages"])


def get_page(annotation: str = "Boiling Point", heading_type: str = "Compound", page: int = 1) -> dict:
    """Get a particular page of a given (annotation, heading_type) combination

    Args:
        annotation (str, optional): Defaults to "Boiling Point".
        heading_type (str, optional): Defaults to "Compound".
        page (int, optional): Defaults to 1.

    Returns:
        dict: the returned data from pubchem's pug view api.
    """
    annotation = annotation.replace(" ", "%20")
    res = requests.get(
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/{annotation}/JSON?heading_type={heading_type}&page={page}"
    )
    return res.json()


def get_raw_data_by_page(annotation: str = "Boiling Point", heading_type: str = "Compound", page: int = 1) -> Tuple[dict, dict]:
    """Reduce output of get_page() to a dictionary of the annotion in question and the cid ref.

    Args:
        annotation (str, optional): Defaults to "Boiling Point".
        heading_type (str, optional): Defaults to "Compound".
        page (int, optional): Defaults to 1.

    Returns:
        Tuple[dict, dict]: (raw_data, err_data). err_data contains a tuple of indices and what's wrong with them.
    """

    page = get_page(annotation=annotation, heading_type=heading_type, page=page)
    records = page["Annotations"]["Annotation"]

    raw_data = {}
    err_data = []
    for record_ind, record in enumerate(records):
        name = record["Name"]

        data = []
        for datum in record["Data"]:
            try:
                data.append(datum["Value"]["StringWithMarkup"])
            except KeyError:
                err_data.append((record_ind, "no stringwithmarkup"))

        record_data = {}

        # Add data to record_data
        record_data["data"] = data
        try:
            record_data["cid"] = record["LinkedRecords"]["CID"]
        except KeyError:
            err_data.append((page, record_ind, "no cid"))

        # Only add datum if all are available
        if "data" in record_data.keys() and "cid" in record_data.keys():
            raw_data[name.lower()] = record_data

    return raw_data, err_data


def separate_by_cid(raw_data: dict) -> Tuple[dict, dict]:
    """Reduce output of get_raw_data_by_page() to only those that are connected to 1 cid ref.

    Args:
        raw_data (dict): output of get_raw_data_by_page()

    Returns:
        Tuple[dict, dict]: dict_with_one_cid, dict_with_multiple_cid
    """

    keys = list(raw_data.keys())
    data = copy.deepcopy(raw_data)

    one_cid = {}
    mul_cid = {}

    for key in keys:
        cids = data[key]["cid"]

        if len(cids) == 1:
            data[key]["cid"] = cids[0]
            one_cid[key] = data[key]
        else:
            mul_cid[key] = data[key]
    return one_cid, mul_cid


def flatten(xss: List[list]) -> list:
    """_summary_

    Args:
        xss (List[list]): nested (2d) list

    Returns:
        list: flattened list
    """
    return [x for xs in xss for x in xs]


def separate_by_reports(raw_data: dict) -> Tuple[dict, dict]:
    """Reduce output of get_raw_data_by_page() to only those that contain one report.

    Args:
        raw_data (dict): output of get_raw_data_by_page()

    Returns:
        Tuple[dict, dict]: (dict_with_one_report, dict_with_multiple_reports)
    """

    keys = list(raw_data.keys())
    data = copy.deepcopy(raw_data)

    one_report = {}
    mul_report = {}

    for key in keys:
        reports = flatten(data[key]["data"])

        if len(reports) == 1:
            data[key]["data"] = reports[0]["String"]
            one_report[key] = data[key]
        else:
            mul_report[key] = data[key]

    return one_report, mul_report


def convert_to_celcius(temp: str) -> float:
    """Convert report string to float in celcius

    Args:
        temp (str): Something like 36 C

    Returns:
        float: 36 from '36 C'
    """

    temp = temp.lower()
    check_c = bool(re.search("^[\-|0-9][0-9]*[.]?[0-9]*[ ]*[u'\N{DEGREE SIGN}'][c ]$", temp))
    check_f = bool(re.search("^[\-|0-9][0-9]*[.]?[0-9]*[ ]*[u'\N{DEGREE SIGN}'][f ]$", temp))
    check_c_and_pressure_1 = bool(re.search("^[\-|0-9][0-9]*[.]?[0-9]*[ ]*[u'\N{DEGREE SIGN}'][c ] at 760 mm hg", temp))
    check_c_and_pressure_2 = bool(re.search("^[\-|0-9][0-9]*[.]?[0-9]*[ ]*[u'\N{DEGREE SIGN}'][c ] @ 760 mm hg", temp))

    if check_c or check_c_and_pressure_1 or check_c_and_pressure_2:
        return float(temp.split("\N{DEGREE SIGN}")[0].strip())
    if check_f:
        f_temp = float(temp.split("\N{DEGREE SIGN}")[0].strip())
        c_temp = (f_temp - 32) * (5 / 9)
        return c_temp


def separate_by_data_string(raw_data: dict) -> Tuple[dict, dict]:
    """Clean output of separate_by_reports() by converting report
    strings to float in celcius.

    Args:
        raw_data (dict): output of separate_by_reports()

    Returns:
        Tuple[dict, dict]: (dict_with_converted_data, dict_failed_to_convert)
    """

    keys = list(raw_data.keys())
    data = copy.deepcopy(raw_data)

    clean_string = {}
    dirty_string = {}

    for key in keys:
        data_string = convert_to_celcius(data[key]["data"])

        if data_string is not None:
            data[key]["data"] = data_string
            clean_string[key] = data[key]
        else:
            dirty_string[key] = data[key]
    return clean_string, dirty_string

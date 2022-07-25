import requests
from typing import Tuple, List

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


def get_page(annotation: str = "Boiling Point", heading_type: str = "Compound", page_no: int = 1) -> dict:
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
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/{annotation}/JSON?heading_type={heading_type}&page={page_no}"
    )
    return res.json()


def get_all_raw_data(annotation: str = "Boiling Point", heading_type: str = "Compound", total_pages: int = None) -> Tuple[dict, dict]:

    if total_pages is None:
        total_pages = get_total_pages(annotation=annotation, heading_type=heading_type)

    raw_data = {}
    err_data = []

    for page_no in range(1, total_pages + 1):

        page = get_page(annotation=annotation, heading_type=heading_type, page_no=page_no)
        records = page["Annotations"]["Annotation"]

        for record_ind, record in enumerate(records):

            record_data = {}
            name = record["Name"].lower().strip()

            # Get data with specified annotation
            data = []
            for datum in record["Data"]:
                try:
                    data.append(datum["Value"]["StringWithMarkup"])
                except KeyError:
                    err_data.append((name, page_no, record_ind, "no stringwithmarkup"))

            # Get cid ref
            cids = None
            try:
                cids = record["LinkedRecords"]["CID"]
            except KeyError:
                err_data.append((name, page_no, record_ind, "no cid"))

            # Update raw_data
            if cids and data:

                if name in raw_data.keys():
                    for datum in data:
                        raw_data[name]["data"].append(datum)
                    for cid in cids:
                        if cid not in raw_data[name]["cid"]:
                            raw_data[name]["cid"].append(cid)
                else:
                    record_data["data"] = data
                    record_data["cid"] = cids
                    raw_data[name] = record_data

    for key in raw_data.keys():
        temp_data = flatten(raw_data[key]["data"])
        raw_data[key]["data"] = [datum["String"] for datum in temp_data]

    return raw_data, err_data


def single_record(data_str: str) -> bool:

    if ";" in data_str:
        return False
    else:
        return True


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
                err_data.append((page, record_ind, "no stringwithmarkup"))

        record_data = {}

        # Add data to record_data
        record_data["data"] = data
        try:
            record_data["cid"] = record["LinkedRecords"]["CID"]
        except KeyError:
            err_data.append((page, record_ind, "no cid"))

        # Only add datum if all are available and name is unique.
        if name in raw_data.keys():
            err_data.append((page, record_ind, "duplicate name"))
        elif "data" in record_data.keys() and "cid" in record_data.keys():
            raw_data[name.lower()] = record_data

    return raw_data, err_data


def flatten(xss: List[list]) -> list:
    """_summary_

    Args:
        xss (List[list]): nested (2d) list

    Returns:
        list: flattened list
    """
    return [x for xs in xss for x in xs]

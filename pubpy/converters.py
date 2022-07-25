import re
from typing import Literal

# number = "[\-|0-9][0-9]*[.]?[0-9]*"
all_number = "[\-]*[0-9]+[.]?[0-9]*"
pos_number = "[0-9]+[.]?[0-9]*"
celcius = "[u'\N{DEGREE SIGN}']*[ ]*c"
farenheit = "[u'\N{DEGREE SIGN}']*[ ]*f"
cp = "(centipoise|cp)"
mpas = "mpa[.*-](s|sec)"
hg = "mm[ ]*hg"

def convert_to_c(data_str: str, position: Literal["start", "mid", "end"]) -> float:
    """Given a data string, search for temperature info
    and convert it to celcius.

    Args:
        data_str (str): sth like 'djd 36 C djfdifj'

    Returns:
        float: 36
    """

    string = data_str.lower().strip()

    if position == "start":
        start = "^"
        end = ""
    elif position == "mid":
        start = ""
        end = ""
    elif position == "end":
        start = ""
        end = "$"

    check_c = re.search(f"{start}{all_number}[ ]*{celcius}{end}", string)
    check_f = re.search(f"{start}{all_number}[ ]*{farenheit}{end}", string)

    if check_c:
        span = check_c.span()
        temp = string[span[0] : span[1]]

        if "\N{DEGREE SIGN}" in temp:
            return float(temp.split("\N{DEGREE SIGN}")[0].strip())
        else:
            try:
                return float(temp.split()[0].strip())
            except ValueError:
                return float(temp.split("c")[0].strip())

    if check_f:
        span = check_f.span()
        temp = string[span[0] : span[1]]

        if "\N{DEGREE SIGN}" in temp:
            f_temp = float(temp.split("\N{DEGREE SIGN}")[0].strip())
        else:
            try:
                f_temp = float(temp.split()[0].strip())
            except ValueError:
                f_temp = float(temp.split("c")[0].strip())

        c_temp = round((f_temp - 32) * (5 / 9), 2)
        return c_temp

def convert_to_atm(data_str: str) -> float:

    string = data_str.lower().strip()

    check_hg = re.search(f"{pos_number}[ ]*{hg}", string)
    check_atm = re.search(f"{pos_number}[ ]*atm", string)
    check_pa = re.search(f"{pos_number}[ ]*pa", string)


    try:
        if check_hg:
            span = check_hg.span()
            pres = float(string[span[0] : span[1]].split()[0])
            return round(pres / 760, 2)

        elif check_atm:
            span = check_atm.span()
            pres = float(string[span[0] : span[1]].split()[0])
            return pres

        elif check_pa:
            span = check_pa.span()
            pres = float(string[span[0] : span[1]].split()[0])
            return round(pres / 101300, 2)
    except ValueError:
        return None

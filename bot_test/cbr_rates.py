import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

CBR_URL = "https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={}&date_req2={}&VAL_NM_RQ=R01235"


def get_interest_rates(start_date):
    """ Загружает процентные ставки ЦБ РФ начиная с указанной даты. """
    end_date = datetime.now()
    date_format = "%d/%m/%Y"

    url = CBR_URL.format(start_date.strftime(date_format), end_date.strftime(date_format))
    response = requests.get(url)

    if response.status_code != 200:
        return []

    rates = []
    root = ET.fromstring(response.content)

    for record in root.findall("Record"):
        rate_date = datetime.strptime(record.attrib["Date"], "%d.%m.%Y")
        rate_value = float(record.find("Value").text.replace(",", "."))
        rates.append((rate_date, rate_value))

    return rates

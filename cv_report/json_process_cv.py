# Local imports
from month_generator import generate_months


def json_data_extract(data):
    """
    Generates a formatted list suitable for ReportLab's table generation method
    :param data: a JSON file
    :return: a list of lists where each element is a row of data
    """
    outer_list = []
    layer1 = data.get("cvDataList", "")
    tests = len(layer1)
    months = generate_months(data["startDateStr"])

    for i in range(tests):
        inner_list = []
        first = True
        layer2 = layer1[i]["levelData"]
        details = len(layer2)

        for j in range(details):
            # Add the two values only on the first occurrence of the test. Every other instance needs to be empty
            if first:
                inner_list.append(layer1[i].get("analytesName", ""))
                inner_list.append("")
            else:
                inner_list.append("")
                inner_list.append("")

            # Extracted using the get method to handle missing keys
            inner_list.append(layer2[j].get("level", ""))

            layer3 = layer2[j]["dataList"]
            cvs = len(layer3)
            for month in months:
                appended = False
                for k in range(cvs):
                    if layer3[k]["yearMonth"] == month:
                        inner_list.append(layer3[k].get("cv"))
                        appended = True
                if not appended:
                    inner_list.append("")

            inner_list.append(layer1[i].get("target", ""))
            outer_list.append(inner_list)
            inner_list = []
            first = False

    return outer_list

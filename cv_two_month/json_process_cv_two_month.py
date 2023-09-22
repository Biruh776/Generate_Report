# Extracts the information from the json file and returns a list that can be expressed in a table
def json_data_extract(data):
    """
    Generates a formatted list suitable for ReportLab's table generation method
    :param data: a JSON file
    :return: a list of lists where each element is a row of data
    """
    outer_list = []
    layer1 = data.get("projectMonthDataList", "")
    tests = len(layer1)
    format_index = [2, 3, 5, 6, 10, 11]
    lev_list = data.get("levelList", "")
    lev_len = len(lev_list)
    month_list = []

    for i in range(tests):
        inner_list = []
        first = True
        layer2 = layer1[i].get("monthDataList", "")
        details = len(layer2)

        for j in range(details):
            # Add the two values only on the first occurrence of the test. Every other instance needs to be empty
            if first:
                inner_list.append(layer1[i].get("analytesName", ""))
            else:
                inner_list.append("")

            # Extracted using the get method to handle missing keys
            inner_list.append(str(layer2[j].get("level", "")))
            layer3 = layer2[j].get("monthData", "")
            details3 = len(layer3)

            if details3 > 0:
                for idx in range(details3):
                    month = layer3[idx].get("yearMonth", "")
                    if month not in month_list:
                        month_list.append(month)
                    inner_list.append(layer3[idx].get("mean", ""))
                    inner_list.append(layer3[idx].get("cv", ""))
                    inner_list.append(str(layer3[idx].get("dataCount", "")))

            else:
                inner_list.append("")
                inner_list.append("")
                inner_list.append("")
                inner_list.append("")
                inner_list.append("")
                inner_list.append("")

            if inner_list[5] != '' and inner_list[2] != '':
                mean_diff = ((inner_list[5] - inner_list[2])/inner_list[2])*100
                mean_diff = f'{mean_diff:.2f}%'
            else:
                mean_diff = ''
            inner_list.append(mean_diff)

            if inner_list[6] != '' and inner_list[3] != '':
                cv_diff = ((inner_list[6] - inner_list[3])/inner_list[3])*100
                cv_diff = f'{cv_diff:.2f}%'
            else:
                cv_diff = ''
            inner_list.append(cv_diff)

            if lev_len == 1:
                if inner_list[6] != '' and inner_list[3] != '':
                    cvr = inner_list[3]/inner_list[6]
                else:
                    cvr = ''
                inner_list.append(cvr)

            inner_list.append(layer2[j].get("target", ""))
            formatted_list = []
            for idx in range(len(inner_list)):
                value = inner_list[idx]
                if idx in format_index:
                    if isinstance(value, (int, float)):
                        formatted_value = "{:.2f}".format(value)
                        formatted_list.append(formatted_value)
                    else:
                        formatted_list.append(value)
                else:
                    formatted_list.append(value)

            outer_list.append(formatted_list)
            inner_list = []
            first = False
            
    if not outer_list:
        for i in range(2):
            outer_list.append([""]*11)

    return outer_list, month_list

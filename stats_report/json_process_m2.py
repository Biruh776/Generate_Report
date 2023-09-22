# Extracts the information from the json file and returns a list that can be expressed in a table
def json_data_extract(data):
    """
    Generates a formatted list suitable for ReportLab's table generation method
    :param data: a JSON file
    :return: a list of lists where each element is a row of data
    """
    outer_list = []
    batch_layer = data.get("batchManageList", "")
    batches = len(batch_layer)
    format_index = [3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21]
    for x in range(batches):
        batch_first = True
        layer1 = batch_layer[x]
        interm_layer = layer1.get("testProjectList", "")
        tests = len(interm_layer)

        for i in range(tests):
            inner_list = []
            first = True
            layer2 = interm_layer[i].get("levelDataList", "")
            details = len(layer2)

            for j in range(details):
                # Add the two values only on the first occurrence of the test. Every other instance needs to be empty
                if batch_first:
                    inner_list.append(layer1.get("batchCode", ""))
                else:
                    inner_list.append("")

                if first:
                    inner_list.append(interm_layer[i].get("analytesName", ""))
                else:
                    inner_list.append("")

                # Extracted using the get method to handle missing keys
                inner_list.append(layer2[j].get("level", ""))
                inner_list.append(layer2[j].get("testMean", ""))
                inner_list.append(layer2[j].get("testSd", ""))
                inner_list.append(layer2[j].get("testCv", ""))
                inner_list.append(layer2[j].get("monthMean", ""))
                inner_list.append(layer2[j].get("monthSd", ""))
                inner_list.append(layer2[j].get("monthCv", ""))
                inner_list.append(layer2[j].get("monthDataCount", ""))
                inner_list.append(layer2[j].get("monthUncontrolledDataCount", ""))
                inner_list.append(layer2[j].get("monthControlRate", ""))
                inner_list.append(layer2[j].get("controlMean", ""))
                inner_list.append(layer2[j].get("controlSd", ""))
                inner_list.append(layer2[j].get("controlCv", ""))
                inner_list.append(layer2[j].get("totalMean", ""))
                inner_list.append(layer2[j].get("totalSd", ""))
                inner_list.append(layer2[j].get("totalCv", ""))
                inner_list.append(layer2[j].get("totalDataCount", ""))
                inner_list.append(layer2[j].get("totalUncontrolledRate", ""))
                inner_list.append(layer2[j].get("goalCv", ""))
                inner_list.append(layer2[j].get("goalSd", ""))

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
                batch_first = False

    if not outer_list:
        for i in range(2):
            outer_list.append([""]*22)

    return outer_list

# Extracts the information from the json file and returns a list that can be expressed in a table
def json_data_extract(data):
    """
    Generates a formatted list suitable for ReportLab's table generation method
    :param data: a JSON file
    :return: a list of lists where each element is a row of data
    """
    outer_list = []
    layer1 = data.get("testProjectList", "")
    tests = len(layer1)

    for i in range(tests):
        inner_list = []
        first = True
        layer2 = layer1[i]["levelDataList"]
        details = len(layer2)

        for j in range(details):
            # Add the two values only on the first occurrence of the test. Every other instance needs to be empty
            if first:
                inner_list.append(layer1[i].get("analytesName", ""))
                inner_list.append(layer1[i].get("measureUnit", ""))
            else:
                inner_list.append("")
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
            inner_list.append(layer2[j].get("totalUncontrolledRate", ''))
            inner_list.append(layer2[j].get("goalCv", ''))
            inner_list.append(layer2[j].get("goalSd", ''))

            outer_list.append(inner_list)
            inner_list = []
            first = False

    return outer_list

# Extracts the information from the json file and returns a list that can be expressed in a table
def json_data_extract(data):
    """
    Generates a formatted list suitable for ReportLab's table generation method
    :param data: a JSON file
    :return: a list of lists where each element is a row of data
    """
    outer_list = []
    layer1 = data.get("projectDataList", "")
    tests = len(layer1)
    format_index = [3, 4, 5, 6]

    for i in range(tests):
        inner_list = []
        first = True
        layer2 = layer1[i].get("pointDataList", "")
        details = len(layer2)

        for j in range(details):
            # Add the two values only on the first occurrence of the test. Every other instance needs to be empty
            if first:
                inner_list.append(layer1[i].get("analytesName", ""))
            else:
                inner_list.append("")

            # Extracted using the get method to handle missing keys
            inner_list.append(layer2[j].get("level", ""))
            inner_list.append(layer2[j].get("createTime", ""))
            inner_list.append(layer2[j].get("pointValue", ""))
            inner_list.append(layer2[j].get("mean", ""))
            inner_list.append(layer2[j].get("sd", ""))
            inner_list.append(layer2[j].get("zPoint", ""))

            # Accecptable or non-acceptable values
            try:
                state = "拒绝" if layer2[j]["acceptable"] == 0 else "接受"
            except:
                state = ""
            inner_list.append(state)

            inner_list.append(layer2[j].get("operationUserName", ""))

            # Final column
            spc_rule = layer2[j].get("spcRule", "")
            action_logs = layer2[j].get("actionLogList", "")
            remark = layer2[j].get("remark", "")

            formatted_logs = []

            for _, action_log in enumerate(action_logs):
                action_desc = action_log.get("actionDesc", "")
                operation_user = action_log.get("operationUserName", "")
                create_time = action_log.get("createTime", "")  # Extract yyyy-mm-dd from the timestamp
                if create_time:
                    create_time = create_time[:10]
                formatted_log = f"{action_desc}({operation_user}, - {create_time})"
                formatted_logs.append(formatted_log)

            formatted_string = f"{spc_rule}, {' // '.join(formatted_logs)} // {remark}"
            inner_list.append(formatted_string)

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
            outer_list.append([""]*10)

    return outer_list

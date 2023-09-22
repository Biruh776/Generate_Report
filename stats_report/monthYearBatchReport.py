# Standard library imports
import os
import uuid
import copy

# External library imports
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph

# Local imports
from json_process_m2 import json_data_extract
# from point_lj_report.pdfCreateTemp import upload_report

# Default paragraph style
paragraph_style = ParagraphStyle(name='CustomStyle',
                                 fontName='SimHei',
                                 fontSize=9,
                                 textColor=colors.black,
                                 wordWrap='CJK',
                                 leading=12,
                                 alignment=0, )


def pdf_gen(json_file, month_or_year):
    # Define reference points
    mar_in = 0.15
    left = mar_in * inch
    bottom = mar_in * inch
    right = landscape(A4)[0] - mar_in * inch
    top = landscape(A4)[1] - mar_in * inch
    middle_vert = (right - left) / 2

    # Define table parameters
    cell_x = (right - left) / 22
    col_widths = [cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x,
                  cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x, cell_x]
    col_widths[1] = col_widths[1] + 15 + 17 + 17
    col_widths[2] = col_widths[2] - 15
    col_widths[9] = col_widths[9] - 17
    col_widths[18] = col_widths[18] - 17
    cell_y = 19  # Create 22 uniform cells of size cell_y by cell_x
    grid_width = 1
    grid_color = [0.3, 0.3, 0.3]
    left_pad = 2

    # Set up a Chinese Font
    pdfmetrics.registerFont(TTFont("SimHei", "simhei.ttf"))
    pdfmetrics.registerFont(TTFont("SimHei-Bold", "simhei_bold.ttf"))

    # Create a new PDF document with a unique name on an A4 paper in landscape orientation
    pdf_file_name = f'./{str(uuid.uuid4())}.pdf'
    pdf_file_name = 'Month2.pdf'
    pdf = canvas.Canvas(pdf_file_name, pagesize=landscape(A4))
    pdf.setLineCap(2)

    # Title (top middle)
    if month_or_year == 1:
        title_text = "室内质控月报表"
    else:
        title_text = "室内质控年报表"
    pdf.setFont("SimHei-Bold", 16)
    pdf.drawString((right - left) / 2 - 47, top - 20, title_text)

    # # Load the passed in json
    data = json_file

    # ID (top right)
    id_text = data["reportCode"]
    pdf.setFont("Helvetica", 10)
    pdf.drawString(right - 100, top - 14, id_text)

    # Text field at the top of the first page
    # Top line
    vert_pos1 = top - 45
    pdf.line(left, vert_pos1, right, vert_pos1)

    # Extract text data
    start_date = data.get("startDateStr", "")
    end_date = data.get("endDateStr", "")
    instrument = data.get("kitsName", "")
    laboratory = data.get("laboratoryName", "")
    lab_relation = data.get("laboratoryRelation", "")

    # Text within the field
    textbox1 = {"time_range": start_date + " - " + end_date,
                "instrument/kit": instrument,
                "laboratory": laboratory + "(" + lab_relation + ")"
                }

    # First row
    pdf.setFont("SimHei", 11)  # Set for the whole box
    pdf.drawString(left + 65, vert_pos1 - 23, "时间范围: ")
    pdf.drawString(left + 120, vert_pos1 - 23, textbox1["time_range"])

    # Check if the laboratory name text overflows
    threshold = right - middle_vert - 127
    text_location = textbox1["laboratory"]
    first_line, overflow, status = _check_text_overflow(pdf, text_location, threshold)
    if status:
        pdf.drawString(middle_vert + 75, vert_pos1 - 23, "实验室: ")
        pdf.drawString(middle_vert + 120, vert_pos1 - 23, first_line)
        pdf.drawString(middle_vert + 120, vert_pos1 - 43, overflow)

    else:
        pdf.drawString(middle_vert + 75, vert_pos1 - 23, "实验室: ")
        pdf.drawString(middle_vert + 120, vert_pos1 - 23, text_location)

    # Second row
    pdf.drawString(left + 65, vert_pos1 - 48, "仪器: ")
    pdf.drawString(left + 100, vert_pos1 - 48, textbox1["instrument/kit"])

    # Bottom line
    vert_pos2 = vert_pos1 - 48 - 12
    pdf.line(left, vert_pos2, right, vert_pos2)

    # Status box blue border light blue fill, with a status text
    # Dimensions
    x = left
    y = vert_pos2 - 30
    width = right - left
    height_blue_box = 20

    # Set the colors
    pdf.setStrokeColorRGB(0.725, 0.898, 1)
    pdf.setFillColorRGB(0.902, 0.969, 1)
    pdf.roundRect(x, y, width, height_blue_box, 1, stroke=1, fill=1)

    # Set the text properties inside the box
    numb_of_data = _data_counter(data)
    text = f"总计{numb_of_data}条数据"
    text_color = colors.black
    left_padding_box_text = 10

    # Draw the text
    pdf.setFillColor(text_color)
    pdf.setFont("SimHei", 11)
    pdf.drawString(x + left_padding_box_text, y + height_blue_box / 2 - 11 / 2 + 1, text)  # 11 is font size

    # Define a new vertical reference point at the end of the box
    vert_pos3 = y - height_blue_box

    # Draw the title rows (row one and two). These values are the same for every report.
    if month_or_year == 1:
        reading_data = '当月原始测定结果'
    else:
        reading_data = '当年原始测定结果'
    headers = [
        ['批号',
         '测定项目',
         '绘制质控图的均值和标准差', '', '', '',
         reading_data, '', '', '', '', '',
         '除失控后的测定结果', '', '',
         '累计测定结果', '', '', '', '',
         '质量目标', ''],
        ['', '', '水平', '均值', 'SD', 'CV%', '均值', 'SD', 'CV%', 'N', '失控数', '在控率%',
         '均值', 'SD', 'CV%', '均值', 'SD', 'CV%', 'N', '在控率%', 'CV%', 'SD']
    ]
    table = Table(headers, colWidths=col_widths, cornerRadii=[1, 1, 0, 0])
    table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), left_pad - 1),
        ('SPAN', (0, 0), (0, 1)),
        ('SPAN', (1, 0), (1, 1)),
        ('SPAN', (2, 0), (5, 0)),
        ('SPAN', (6, 0), (11, 0)),
        ('SPAN', (12, 0), (14, 0)),
        ('SPAN', (15, 0), (19, 0)),
        ('SPAN', (20, 0), (21, 0)),
        ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), grid_width, grid_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE')
    ]))
    table.wrapOn(pdf, right - left, top - bottom)
    table.drawOn(pdf, x, vert_pos3 - 20)

    # Create a new vertical reference point at the end of the headers to draw the rest of the tables
    vert_pos4 = vert_pos3 - 20

    # Draw the rest of the table. This is not used to draw, rather it is used to judge the height of the table.
    datarow = json_data_extract(data)

    col_data = _colum_extr(datarow, 0)
    cell_height, numb_line = _calc_newline_numb(col_widths[0], col_data)
    table = Table(datarow, colWidths=col_widths, rowHeights=cell_height, cornerRadii=[1, 1, 0, 0])

    # This sets the base style for the table
    table_style = TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), left_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), left_pad),
        ('FONTNAME', (0, 0), (1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (1, 0), (-1, -1), grid_width, grid_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ("LINEOVERFLOW", (0, 0), (-1, -1), 0)
    ])
    # Compute table dimensions
    table_width, table_height = table.wrapOn(pdf, right - left, top - bottom)
    size_all = table_height

    # Set the maximum height for a single page
    max_page_height = vert_pos4 - 15

    # Flag to check if the first page has already been drawn. Important because the starting position on the
    # first page is dependent on other quantities like the length of the laboratory name
    fst_run = True
    one_page_format_flag = False

    while True:
        if fst_run:
            # Compute the number of lines taking text wrapping into consideration
            cell_height, numb_line, drawable = process_data(datarow, col_widths[0:2], 20)
            if status:
                cell_height, numb_line, drawable = process_data(datarow, col_widths[0:2], 19)
            rows_per_page = drawable

            # Accommodate for possible multiline laboratory name
            if status and numb_line <= 14:
                one_page_format_flag = True
            elif not status and numb_line <= 15:
                one_page_format_flag = True

            # Update the table data for the current page
            table_data = datarow[:rows_per_page]
            datarow = datarow[rows_per_page:]

            table_data_old = copy.deepcopy(table_data)

            table_data = _wrappable(table_data, 0)
            table_data = _wrappable(table_data, 1)

            # Create a Table object for the current page
            table = Table(table_data, colWidths=col_widths, rowHeights=cell_height[:drawable], cornerRadii=[0, 0, 1, 1])
            if one_page_format_flag:
                table = Table(table_data, colWidths=col_widths, rowHeights=cell_height[:drawable],
                              cornerRadii=[0, 0, 0, 0])
            table.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 0, colors.white)]))
            table.setStyle(table_style)

            # Apply different colors based on rules
            _cv_color_changer(table, table_data)
            _mean_color_changer(table, table_data)

            # Handles grouping the batches
            _handle_groups(table, table_data_old)

            # Get the table width and height for the current page
            table_width, table_height = table.wrapOn(pdf, right - left, cell_y)

            # Table height update
            store_height = table_height
            shift_val = max_page_height - bottom - store_height

            # Draw the table on the current page
            # Initial table drawing position
            y = 28
            pdf.saveState()
            pdf.translate(x, y)
            table.drawOn(pdf, 0, shift_val - 2)
            pdf.restoreState()

            # Turn off the first run flag
            fst_run = False

            # Create a new page if there is any data left
            if datarow or not one_page_format_flag:
                # Create a new page
                pdf.showPage()

            if len(datarow):
                # Update parameters for the leftover data
                cell_height, numb_line, drawable = process_data(datarow, col_widths[0:2], 30)

        if numb_line >= 30:
            # Determine the number of rows that can fit within the page height
            rows_per_page = drawable

            # Update the table data for the current page
            table_data = datarow[:rows_per_page]
            datarow = datarow[rows_per_page:]

            table_data_old = copy.deepcopy(table_data)

            table_data = _wrappable(table_data, 0)
            table_data = _wrappable(table_data, 1)

            # Create a Table object for the current page
            table = Table(table_data, colWidths=col_widths, rowHeights=cell_height[:drawable], cornerRadii=[1, 1, 1, 1])
            table.setStyle(table_style)

            # Apply different colors based on rules
            _cv_color_changer(table, table_data)
            _mean_color_changer(table, table_data)

            # Handles grouping the batches
            _handle_groups(table, table_data_old)

            # Get the table width and height for the current page
            table_width, table_height = table.wrapOn(pdf, right - left, top - bottom)

            # Table height update
            y = bottom + 3
            max_page_height = top
            store_height = table_height
            table_height = size_all - table_height
            shift_val = max_page_height - bottom - store_height

            # Draw the table on the current page
            pdf.saveState()
            pdf.translate(x, y)
            table.drawOn(pdf, 0, shift_val)
            pdf.restoreState()

            # Create a new page
            pdf.showPage()

            # Update parameters for the leftover data
            cell_height, numb_line, drawable = process_data(datarow, col_widths[0:2], 30)

        elif 30 > numb_line > 24:
            # Determine the number of rows that can fit within the page height
            rows_per_page = drawable

            # Update the table data for the current page
            table_data = datarow[:rows_per_page]
            datarow = datarow[rows_per_page:]

            table_data_old = copy.deepcopy(table_data)

            table_data = _wrappable(table_data, 0)
            table_data = _wrappable(table_data, 1)

            # Create a Table object for the current page
            table = Table(table_data, colWidths=col_widths, rowHeights=cell_height[:drawable], cornerRadii=[1, 1, 1, 1])
            table.setStyle(table_style)

            # Apply different colors based on rules
            _cv_color_changer(table, table_data)
            _mean_color_changer(table, table_data)

            # Handles grouping the batches
            _handle_groups(table, table_data_old)

            # Get the table width and height for the current page
            table_width, table_height = table.wrapOn(pdf, right - left, top - bottom)

            # Table height update
            max_page_height = top
            y = bottom + 3
            store_height = table_height
            table_height = size_all - table_height
            shift_val = max_page_height - bottom - store_height

            # Draw the table on the current page
            pdf.saveState()
            pdf.translate(x, y)
            table.drawOn(pdf, 0, shift_val)
            pdf.restoreState()

            # Create a new page
            pdf.showPage()

            # update y and max_page_height
            y = bottom + 3
            max_page_height = top

            # Update parameters for the leftover data
            cell_height, numb_line, drawable = process_data(datarow, col_widths[0:2], 30)


        else:
            # When it reaches here, it either has printed the whole table, and the only thing left is the summary box
            # or there is data left that fits in the next page with the summary box and the signature.
            break

    # Draw the last page
    # Update parameters for the leftover data
    cell_height, numb_line, drawable = process_data(datarow, col_widths[0:2], 30)

    max_page_height = top
    len_data_lastpage = numb_line

    datarow_old = copy.deepcopy(datarow)  # Store the unconverted data

    datarow = _wrappable(datarow, 0)
    datarow = _wrappable(datarow, 1)

    # If there is any more data left, draw it on the last page
    if len_data_lastpage:
        y = bottom + 3
        table = Table(datarow, colWidths=col_widths, rowHeights=cell_height[:drawable], cornerRadii=[1, 1, 0, 0])
        table.setStyle(table_style)

        # Apply different colors based on rules
        _cv_color_changer(table, datarow)
        _mean_color_changer(table, datarow)

        # Handles grouping the batches
        _handle_groups(table, datarow_old)

        # Draw the table on the last page
        pdf.saveState()
        pdf.translate(x, y)
        width2, height2 = table.wrapOn(pdf, right - left, cell_y)
        val = max_page_height - bottom - height2 - 2
        table.drawOn(pdf, 0, val)
        pdf.restoreState()

        last_height = height2

    # If the data is only one page, the information needs to be positioned using a variable y value to accommodate for
    # variable height in the first page
    elif one_page_format_flag:
        val = vert_pos4 - bottom - table_height - 3
        last_height = top - vert_pos4 + table_height - 12

    # There is no data left, and we only need to draw the summary box and signature
    else:
        val = top - 12
        last_height = 0

    # Outer visible box
    x = left
    y = val - 11 - 3 * cell_y
    width = right - left
    min_height = 25 + 3 * cell_y

    # Inner transparent textbox
    x_inner = x + 23
    width_inner = width - 23

    # Get the summary text
    summary_text = data.get("summary", "")

    # Split the string into lines
    lines = summary_text.split('\n')

    # Check if the box fits in the current page
    fit_height = 0
    for line in lines:
        line_paragraph = Paragraph(line, paragraph_style)
        line_height = line_paragraph.wrap(right, left + 120)[1]
        fit_height += line_height

    # If it doesn't fit, transfer it to the next page
    if fit_height > top - last_height - bottom - 35 + 2:
        pdf.showPage()
        val = top - 12
        y = val - 11 - 3 * cell_y

    # Iterate through each line and draw it within the box. If the box doesn't fit the line, it automatically
    # creates a new line. The box size is set to a minimum value. It, however, resizes dynamically if the summary
    # requires a bigger space
    paragraph_height = 0
    for line in lines:
        line_paragraph = Paragraph(line, paragraph_style)
        line_height = line_paragraph.wrap(right - 40, left + 120)[1]
        paragraph_height += line_height

        # Place the paragraph inside the rectangle
        paragraph_width = width_inner - (2 * mm)  # Subtract padding
        line_paragraph.wrapOn(pdf, paragraph_width, line_height)
        y_parag = y + (min_height - paragraph_height)
        line_paragraph.drawOn(pdf, x_inner + mm, y_parag - 2)

    # Draw the inner and outer box. The inner box is invisible and is only used as a textbox.
    if paragraph_height >= min_height:
        y -= (paragraph_height - min_height)
    pdf.setStrokeColor(colors.black)
    pdf.setFillColor(colors.white)
    paragraph_height = min_height if min_height >= paragraph_height else paragraph_height
    pdf.roundRect(x, y - 2, width, paragraph_height + 2, [0, 0, 1, 1], fill=0, stroke=1)
    pdf.roundRect(x_inner, y, width_inner, paragraph_height, 1, fill=0, stroke=0)

    # Print the summary title
    summary_title = "评价:"
    pdf.setFillColor(colors.black)
    pdf.setFont("SimHei", 9)
    pdf.drawString(x + 2, y - 11 + paragraph_height, summary_title)

    # Signature at the bottom. Docked to the bottom margin
    # Reviewer
    from_bottom = bottom + 10
    pdf.setFillColor(colors.black)
    reviewer = "审核人: "
    pdf.setFont("SimHei", 12)
    pdf.drawString(right - 300, from_bottom, reviewer)
    pdf.line(right - 255, from_bottom, right - 148, from_bottom)

    # Time and date
    time = "时间: "
    pdf.setFont("SimHei", 12)
    pdf.drawString(right - 140, from_bottom, time)
    pdf.line(right - 107, from_bottom, right, from_bottom)

    # Save the file
    pdf.save()

    # Upload the pdf, delete it from the local machine and return the path
    # pdf_path = upload_report(pdf_file_name)
    #
    # os.remove(pdf_file_name)
    # return pdf_path


def _data_counter(data):
    """
    Counts how many instances of the test are provided
    :param data: a json data
    :return: the total number of tests
    """
    batches = data["batchManageList"]
    numb_batches = len(batches)
    count = 0
    for j in range(numb_batches):
        test = batches[j]["testProjectList"]
        tests = len(test)
        for i in range(tests):
            lev = len(test[i]["levelDataList"])
            count = count + lev
    return count


def _cv_color_changer(table, table_data):
    """
    Reformat CV values to bold and red if they are greater than the expected CV value
    :param table: The table with both actual and expected CV values
    :param table_data: The data to be drawn within the table
    :return:
    """
    # Apply different colors based on rules for expected and actual CV
    cv_col = 8
    for row in range(0, len(table_data)):
        try:
            current_cv = float(table_data[row][cv_col])
            target_cv = float(table_data[row][20])
        except:
            current_cv = ''
            target_cv = ''

        if type(current_cv) == float and type(target_cv) == float:
            if current_cv > target_cv:
                table.setStyle(TableStyle([('TEXTCOLOR', (cv_col, row), (cv_col, row), colors.red)]))
                table.setStyle(TableStyle([('FONTNAME', (cv_col, row), (cv_col, row), 'SimHei-Bold', 9)]))
            else:
                table.setStyle(TableStyle([('TEXTCOLOR', (cv_col, row), (cv_col, row), colors.black)]))
                table.setStyle(TableStyle([('FONTNAME', (cv_col, row), (cv_col, row), 'SimHei', 9)]))
        else:
            continue


def _mean_color_changer(table, table_data):
    """
    Reformat mean values to bold and blue if they are less than the assessment mean minus the SD and to bold and
    red if they are greater than the assessment mean plus the SD
    :param table: The table with both actual and expected CV values
    :param table_data: The data to be drawn within the table
    :return:
    """
    mean_col = 6
    for row in range(0, len(table_data)):
        try:
            assessment_mean = float(table_data[row][3])
            actual_mean = float(table_data[row][mean_col])
            actual_sd = float(table_data[row][4])
        except:
            assessment_mean = ""
            actual_sd = ""
            actual_mean = ""

        if type(assessment_mean) == float and type(actual_mean) == float and type(actual_sd) == float:
            if actual_mean < assessment_mean - actual_sd:
                table.setStyle(TableStyle([('TEXTCOLOR', (mean_col, row), (mean_col, row), colors.blue)]))
                table.setStyle(TableStyle([('FONTNAME', (mean_col, row), (mean_col, row), 'SimHei-Bold', 9)]))
            elif actual_mean > assessment_mean + actual_sd:
                table.setStyle(TableStyle([('TEXTCOLOR', (mean_col, row), (mean_col, row), colors.red)]))
                table.setStyle(TableStyle([('FONTNAME', (mean_col, row), (mean_col, row), 'SimHei-Bold', 9)]))
            else:
                table.setStyle(TableStyle([('TEXTCOLOR', (mean_col, row), (mean_col, row), colors.black)]))
                table.setStyle(TableStyle([('FONTNAME', (mean_col, row), (mean_col, row), 'SimHei', 9)]))
        else:
            continue


def _check_text_overflow(c, text, threshold):
    """
    Checks if the text overflows at the end of the line.
    :param c: the pdf file
    :param text: the text to be analyzed
    :param threshold: The threshold limit
    :return: the text that fits, the remaining text that didn't fit, and a status showing if there is overflow
    """
    if c.stringWidth(text) > threshold:
        # Calculate the remaining text
        remaining_text = ""
        for i in range(len(text)):
            remaining_text = text[i:]
            printed_text = text[:i]
            if c.stringWidth(printed_text) > threshold:
                return printed_text, remaining_text, 1

        # If the loop completes without returning, the entire text overflows
        return text, remaining_text, 1

    return text, "", 0


def _row_span_calc(table_data):
    """
    Computes the spanning range for each batch(group) of data
    :param table_data: the data used to create the table.
    :return:
    """
    rowspan = []
    column = []
    counter = 0
    for row in table_data:
        data = row[0]
        column.append(data)
    for i in range(len(column)):
        if column[i]:
            counter = 1
        else:
            counter += 1
        if (i + 1) == (len(column)):
            rowspan.append(counter)
            break

        if column[i + 1]:
            rowspan.append(counter)
            counter = 1

    return rowspan


def _handle_groups(table, table_data_old):
    """
    Handles created groups of rows
    :param table: a table created on canvas
    :param table_data_old: the data used to create the table.
    :return:
    """

    rowspan = _row_span_calc(table_data_old)
    current_row = 0

    for group_rowspan in rowspan:
        table_style = [('SPAN', (0, current_row), (0, current_row + group_rowspan - 1)),
                       ('GRID', (0, 0), (0, -1), 1, colors.gray)]
        table.setStyle(TableStyle(table_style))
        current_row += group_rowspan


def _calc_newline_numb(width, text):
    """
    Calculates the number of lines and the cell height required to fit the text
    :param width: The width of the column
    :param text: A list of all the text to be written in the table column
    :return: the cell height and the number of lines for each cell
    """
    sample_paragraph = Paragraph("S", paragraph_style)
    line_height = sample_paragraph.wrap(width - 2, 0)[1]

    total_lines = []
    cell_height = []
    cell_y = 19

    for str in text:
        paragraph = Paragraph(str, paragraph_style)
        lines_needed = paragraph.wrap(width - 2, 0)[1] // line_height
        if lines_needed == 0 or lines_needed == 1:
            lines_needed = 1
            cell_height.append(cell_y)
            total_lines.append(lines_needed)
        else:
            cell_height.append(lines_needed * 12)
            total_lines.append(lines_needed)

    return cell_height, total_lines


def _data_for_n_rows(n, width1, width2, text1, text2):
    """
    How much of the data can fit in n number of rows.
    :param text1: A list of all the text to be printed in the table column 1
    :param n: The number of available rows in a page
    :param width1: The width of the cell 1
    :param width2: The width of the cell 2
    :param text2: A list of all the text to be printed in the table column 2
    :return: how many of the rows are drawable in the current page
    """
    sample_paragraph1 = Paragraph("S", paragraph_style)
    line_height1 = sample_paragraph1.wrap(width1 - 2, 0)[1]

    drawable_size0 = []
    drawable_size1 = []
    numb_iter = 0
    for str1 in text1:
        paragraph = Paragraph(str1, paragraph_style)
        lines_needed = paragraph.wrap(width1 - 2, 0)[1] // line_height1
        if lines_needed == 0 or lines_needed == 1:
            lines_needed = 1
            drawable_size0.append(19 * lines_needed)
        else:
            drawable_size0.append(12 * lines_needed)

    sample_paragraph2 = Paragraph("S", paragraph_style)
    line_height2 = sample_paragraph2.wrap(width2 - 2, 0)[1]

    for str2 in text2:
        paragraph = Paragraph(str2, paragraph_style)
        lines_needed = paragraph.wrap(width2 - 2, 0)[1] // line_height2
        if lines_needed == 0 or lines_needed == 1:
            lines_needed = 1
            drawable_size1.append(19 * lines_needed)
        else:
            drawable_size1.append(12 * lines_needed)

    drawable = [max(x, y) for x, y in zip(drawable_size0, drawable_size1)]
    for i in range(len(drawable) + 1):
        numb_iter += 1
        if sum(drawable[:i]) > n * 19:  # Data exceeds the page
            return numb_iter - 2

        elif sum(drawable[:i]) == n * 19:
            return numb_iter - 1

        if i == len(drawable) - 1:
            return numb_iter


def _colum_extr(data, n):
    """
    Extracts the column of interest from the data
    :param n: The column to be extracted
    :param data: data used to draw the table
    :return: The extracted column as a list
    """
    col = []
    for item in data:
        col.append(item[n])

    return col


def _wrappable(data, col_num):
    """
    Converts column n of the data to paragraphs
    :param data: A list of lists used to construct the table
    :param col_num: The column of interest
    :return: The data with the converted column
    """
    numb_row = len(data)
    for i in range(numb_row):
        paragraph = Paragraph(data[i][col_num], paragraph_style)
        data[i][col_num] = paragraph

    return data


def process_data(datarow, col_widths, n_drawable):
    """
    Process the table data and returns parameters that can be used to construct the table
    :param datarow: the data used for creating the table
    :param col_widths: A list of column width values
    :param n_drawable: The number of drawable full cell_y height units (18, 19 or 30)
    :return: cell_height - list of cell_height values for all the rows
            numb_line - cell_y normalized number of lines used for judgements
            drawable - the maximum number of data able to fit on the available space. Used to split the datarow.
    """
    col_data0 = _colum_extr(datarow, 0)
    col_data1 = _colum_extr(datarow, 1)

    cell_height0, numb_line0 = _calc_newline_numb(col_widths[0], col_data0)
    cell_height1, numb_line1 = _calc_newline_numb(col_widths[1], col_data1)

    drawable = _data_for_n_rows(n_drawable, col_widths[0], col_widths[1], col_data0, col_data1)
    group_size = _row_span_calc(datarow[:drawable])

    # This normalizes cell_height0 for the number of rows in a group
    b_sum = [0]
    running_sum = 0
    for numb in group_size:
        running_sum += numb
        b_sum.append(running_sum)

    for i in range(len(b_sum) - 1):
        start = b_sum[i]
        end = b_sum[i + 1]
        cell_height0[start:end] = [cell_height0[start] / (end - start)] * (end - start)

    cell_height = [max(x, y) for x, y in zip(cell_height0, cell_height1)]

    for i in range(len(numb_line0)):
        if numb_line0[i] > 1:
            numb_line0[i] *= (12 / 19)
        if numb_line1[i] > 1:
            numb_line1[i] *= (12 / 19)
    numb_line = sum(max(x, y) for x, y in zip(numb_line0, numb_line1))

    return cell_height, numb_line, drawable

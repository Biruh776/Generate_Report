# Standard library imports
import os
import uuid

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
from json_process_cv import json_data_extract
from month_generator import generate_months
# from point_lj_report.pdfCreateTemp import upload_report

# Default paragraph style
paragraph_style = ParagraphStyle(name='CustomStyle',
                                 fontName='SimHei',
                                 fontSize=9,
                                 textColor=colors.black,
                                 wordWrap='CJK',
                                 leading=12,
                                 alignment=0, )


def pdf_gen(json_data):
    """
    Generates a pdf report for quality control data
    :param json_data: quality control data
    :return:
    """
    # Define reference points
    mar_in = 0.15
    left = mar_in * inch
    bottom = mar_in * inch
    right = landscape(A4)[0] - mar_in * inch
    top = landscape(A4)[1] - mar_in * inch
    middle_vert = (right - left) / 2

    # Define table parameters
    cell_x = (right - left) / 16
    col_widths = [cell_x] * 15
    col_widths[0] = cell_x * 2
    cell_y = 19  # Create 16 uniform cells of size cell_y by cell_x
    grid_width = 1
    grid_color = [0.3, 0.3, 0.3]
    left_pad = 3

    # Set up a Chinese Font
    pdfmetrics.registerFont(TTFont("SimHei", "simhei.ttf"))
    pdfmetrics.registerFont(TTFont("SimHei-Bold", "simhei_bold.ttf"))

    # Create a new PDF document with A4 size and landscape orientation
    pdf_file_name = f'./{str(uuid.uuid4())}.pdf'
    pdf = canvas.Canvas(pdf_file_name, pagesize=landscape(A4))

    # Title (top middle)
    title_text = "批CV均值年汇总报告"
    pdf.setFont("SimHei-Bold", 16)
    pdf.drawString((right - left) / 2 - 72, top - 20, title_text)

    # Load the passed in json
    data = json_data

    # ID (top right)
    id_text = data["reportCode"]
    pdf.setFont("Helvetica", 10)
    pdf.drawString(right - 100, top - 14, id_text)

    # Text field at the top of the first page
    # Top line
    vert_pos1 = top - 45
    pdf.line(left, vert_pos1, right, vert_pos1)

    # Text within the field
    textbox1 = {"time_range": f'{data["startDateStr"]} - {data["endDateStr"]}',
                "instrument/kit": f'{data["kitsName"]}',
                "laboratory": f'{data["laboratoryName"]} ({data["laboratoryRelation"]})',
                "lot_numb/expiry_date": f'{data["batchCode"]}, {_generate_regent_name(data["qualityControls"])},'
                                        f' {data["batchExpirationDateStr"]}',
                }

    # First row
    pdf.setFont("SimHei", 11)  # Set for the whole box
    pdf.drawString(left + 65, vert_pos1 - 23, "时间范围: ")
    pdf.drawString(left + 120, vert_pos1 - 23, textbox1["time_range"])

    # Check if the right-hand side text overflows
    threshold = right - middle_vert - 127
    threshold2 = right - middle_vert - 145
    text_location = textbox1["laboratory"]
    text_location2 = textbox1["lot_numb/expiry_date"]
    first_line, overflow, status = _check_text_overflow(pdf, text_location, threshold)
    first_line2, overflow2, status2 = _check_text_overflow(pdf, text_location2, threshold2)

    # Laboratory name overflows but lot_numb/expiry_date doesn't
    if status and not status2:
        pdf.drawString(middle_vert + 75, vert_pos1 - 23, "实验室: ")
        pdf.drawString(middle_vert + 120, vert_pos1 - 23, first_line)
        pdf.drawString(middle_vert + 120, vert_pos1 - 40, overflow)

        # Second row
        pdf.drawString(left + 65, vert_pos1 - 68, "仪器: ")
        pdf.drawString(left + 100, vert_pos1 - 68, textbox1["instrument/kit"])
        pdf.drawString(middle_vert + 75, vert_pos1 - 68, "批号/效期: ")
        pdf.drawString(middle_vert + 138, vert_pos1 - 68, textbox1["lot_numb/expiry_date"])

        # Bottom line
        vert_pos2 = vert_pos1 - 68 - 12
        pdf.line(left, vert_pos2, right, vert_pos2)

    # Laboratory name doesn't overflow but lot_numb/expiry_date does
    elif not status and status2:
        pdf.drawString(middle_vert + 75, vert_pos1 - 23, "实验室: ")
        pdf.drawString(middle_vert + 120, vert_pos1 - 23, text_location)

        # Second row
        pdf.drawString(left + 65, vert_pos1 - 48, "仪器: ")
        pdf.drawString(left + 100, vert_pos1 - 48, textbox1["instrument/kit"])

        pdf.drawString(middle_vert + 75, vert_pos1 - 48, "批号/效期: ")
        pdf.drawString(middle_vert + 138, vert_pos1 - 48, first_line2)
        pdf.drawString(middle_vert + 138, vert_pos1 - 65, overflow2)

        # Bottom line
        vert_pos2 = vert_pos1 - 68 - 12
        pdf.line(left, vert_pos2, right, vert_pos2)

    # Both Laboratory name and lot_numb/expiry_date overflow
    elif status and status2:
        pdf.drawString(middle_vert + 75, vert_pos1 - 20, "实验室: ")
        pdf.drawString(middle_vert + 120, vert_pos1 - 20, first_line)
        pdf.drawString(middle_vert + 120, vert_pos1 - 33, overflow)

        # Second line
        pdf.drawString(left + 65, vert_pos1 - 55, "仪器: ")
        pdf.drawString(left + 100, vert_pos1 - 55, textbox1["instrument/kit"])

        pdf.drawString(middle_vert + 75, vert_pos1 - 55, "批号/效期: ")
        pdf.drawString(middle_vert + 138, vert_pos1 - 55, first_line2)
        pdf.drawString(middle_vert + 138, vert_pos1 - 68, overflow2)

        # Bottom line
        vert_pos2 = vert_pos1 - 68 - 12
        pdf.line(left, vert_pos2, right, vert_pos2)

    # Neither Laboratory name nor lot_numb/expiry_date overflow
    else:
        pdf.drawString(middle_vert + 75, vert_pos1 - 23, "实验室: ")
        pdf.drawString(middle_vert + 120, vert_pos1 - 23, text_location)

        # Second row
        pdf.drawString(left + 65, vert_pos1 - 48, "仪器: ")
        pdf.drawString(left + 100, vert_pos1 - 48, textbox1["instrument/kit"])
        pdf.drawString(middle_vert + 75, vert_pos1 - 48, "批号/效期: ")
        pdf.drawString(middle_vert + 138, vert_pos1 - 48, textbox1["lot_numb/expiry_date"])

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

    # Import data
    datarow = json_data_extract(data)

    # Define Months
    months = generate_months(data["startDateStr"])

    # Draw the title rows (row one and two). These values are the same for every report.
    headers = [
        ['测定项目', '', '每月cv%', ''],
        ['', '', '水平', months[0], months[1], months[2], months[3], months[4], months[5], months[6], months[7],
         months[8], months[9], months[10], months[11], '质量目标']
    ]
    table = Table(headers, colWidths=cell_x, cornerRadii=[1, 1, 0, 0])
    table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), left_pad),
        ('SPAN', (0, 0), (1, 1)),
        ('SPAN', (2, 0), (-2, 0)),
        ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), grid_width, grid_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (2, 0), (-2, 0), 'CENTER'),
        ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
    ]))
    table.wrapOn(pdf, right - left, cell_y * 2)
    table.drawOn(pdf, x, vert_pos3 - 20)

    # Create a new vertical reference point at the end of the headers to draw the rest of the tables
    vert_pos4 = vert_pos3 - 20

    col_data = _colum_extr(datarow, 0)
    cell_height, numb_line = _calc_newline_numb(col_widths[0], col_data)
    table = Table(datarow, colWidths=cell_x, rowHeights=cell_height, cornerRadii=[1, 1, 0, 0])

    # This sets the base style for the table
    table_style = TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), left_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), left_pad),
        ('FONTNAME', (0, 0), (1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), grid_width, grid_color),
        ("GRID", (1, 0), (1, -1), 0, grid_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ])
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
            cell_height, numb_line, drawable = process_data(datarow, col_widths[0], 20)
            if status:
                cell_height, numb_line, drawable = process_data(datarow, col_widths[0], 19)
            rows_per_page = drawable

            # Accommodate for possible multiline laboratory name
            if status and numb_line <= 14:
                one_page_format_flag = True
            elif not status and numb_line <= 15:
                one_page_format_flag = True

            # Update the table data for the current page
            table_data = datarow[:rows_per_page]
            datarow = datarow[rows_per_page:]

            table_data = _wrappable(table_data, 0)

            # Create a Table object for the current page
            table = Table(table_data, colWidths=cell_x, rowHeights=cell_height[:drawable], cornerRadii=[0, 0, 1, 1])
            if one_page_format_flag:
                table = Table(table_data, colWidths=cell_x, rowHeights=cell_height[:drawable], cornerRadii=[0, 0, 0, 0])
            table.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 0, colors.white)]))
            table.setStyle(table_style)

            # Apply different colors based on rules
            _cv_color_changer(table, table_data)

            # Format the first column
            _first_column_merge(table, table_data)

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
                cell_height, numb_line, drawable = process_data(datarow, col_widths[0], 30)

        if numb_line >= 30:
            # Determine the number of rows that can fit within the page height
            rows_per_page = drawable

            # Update the table data for the current page
            table_data = datarow[:rows_per_page]
            datarow = datarow[rows_per_page:]

            table_data = _wrappable(table_data, 0)

            # Create a Table object for the current page
            table = Table(table_data, colWidths=cell_x, rowHeights=cell_height[:drawable], cornerRadii=[1, 1, 1, 1])
            table.setStyle(table_style)

            # Apply different colors based on rules
            _cv_color_changer(table, table_data)

            # Format the first column
            _first_column_merge(table, table_data)

            # Get the table width and height for the current page
            table_width, table_height = table.wrapOn(pdf, right - left, cell_y)

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
            cell_height, numb_line, drawable = process_data(datarow, col_widths[0], 30)

        elif 30 > numb_line > 25:
            # Determine the number of rows that can fit within the page height
            rows_per_page = drawable

            # Update the table data for the current page
            table_data = datarow[:rows_per_page]
            datarow = datarow[rows_per_page:]

            table_data = _wrappable(table_data, 0)

            # Create a Table object for the current page
            table = Table(table_data, colWidths=cell_x, rowHeights=cell_height[:drawable], cornerRadii=[1, 1, 1, 1])
            table.setStyle(table_style)

            # Apply different colors based on rules
            _cv_color_changer(table, table_data)

            # Format the first column
            _first_column_merge(table, table_data)

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
            cell_height, numb_line, drawable = process_data(datarow, col_widths[0], 30)

        else:
            # When it reaches here, it either has printed the whole table, and the only thing left is the summary box
            # or there is data left that fits in the next page with the summary box and the signature.
            break

    # Draw the last page
    cell_height, numb_line, drawable = process_data(datarow, col_widths[0], 30)
    max_page_height = top
    len_data_lastpage = numb_line

    datarow = _wrappable(datarow, 0)

    # If there is any more data left, draw it on the last page
    if len_data_lastpage:
        y = bottom + 3
        table = Table(datarow, colWidths=cell_x, rowHeights=cell_height[:drawable], cornerRadii=[1, 1, 0, 0])
        table.setStyle(table_style)

        # Apply different colors based on rules
        _cv_color_changer(table, datarow)

        # Format the first column
        _first_column_merge(table, datarow)

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
    x_inner = x + 30
    width_inner = width - 30

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
    if fit_height + 8 > top - last_height - bottom - 35 + 2:
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
        y_parag = y + (min_height - paragraph_height) - 6
        line_paragraph.drawOn(pdf, x_inner + mm, y_parag - 3)

    # Draw the inner and outer box. The inner box is invisible and is only used as a textbox.
    if paragraph_height >= min_height:
        y -= (paragraph_height - min_height)
    pdf.setStrokeColor(colors.black)
    pdf.setFillColor(colors.white)
    paragraph_height = min_height if min_height >= paragraph_height else paragraph_height
    pdf.roundRect(x, y - 2, width, paragraph_height + 2, [0, 0, 1, 1], fill=0, stroke=0)
    pdf.roundRect(x_inner, y - 8, width_inner, paragraph_height, 2, fill=0, stroke=1)

    # Print the summary title
    summary_title = "总结:"
    pdf.setFillColor(colors.black)
    pdf.setFont("SimHei", 10)
    pdf.drawString(x + 2, y - 8 + paragraph_height - 10, summary_title)

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

    pdf.save()

    # # Upload the pdf, delete it from the local machine and return the path
    # pdf_path = upload_report(pdf_file_name)
    #
    # os.remove(pdf_file_name)
    # return pdf_path


def _generate_regent_name(string):
    """
    Generates a regent name by removing content in the last parenthesis
    :param string: the full regent name
    :return: the formatted regent name
    """
    try:
        index_start = string.rindex("(")
        index_end = string.rindex(")") + 1
        result = f"{string[:index_start]}{string[index_end:]}"
        return result
    except:
        return string


def _data_counter(data):
    """
    Counts how many instances of the test are provided
    :param data: a json data
    :return: the total number of tests
    """
    tests = len(data["cvDataList"])
    count = 0
    for i in range(tests):
        lev = len(data["cvDataList"][i]["levelData"])
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
    for row in range(0, len(table_data)):
        try:
            target_cv = float(table_data[row][15])
        except:
            target_cv = ''

        for column in range(3, 15):
            try:
                current_cv = float(table_data[row][column])
            except:
                current_cv = ''

            if type(current_cv) == float and type(target_cv) == float:
                if current_cv > target_cv:
                    table.setStyle(TableStyle([('TEXTCOLOR', (column, row), (column, row), colors.red,)]))
                    table.setStyle(TableStyle([('FONTNAME', (column, row), (column, row), 'SimHei-Bold',)]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (column, row), (column, row), colors.black,)]))
                    table.setStyle(TableStyle([('FONTNAME', (column, row), (column, row), 'SimHei',)]))
            else:
                continue


def _check_text_overflow(c, text, threshold):
    """
    Checks if the text overflows at the end of the line. Checks if it surpasses the threshold
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


def _first_column_merge(table, table_data):
    """
    Merges the first two columns into one by iteratively spanning the cells.
    :param table: A table created on canvas
    :param table_data: the table data used to create the table
    :return:
    """
    column = 0
    length = len(table_data)
    for row in range(0, length):
        table.setStyle(TableStyle([('SPAN', (column, row), (column + 1, row))]))


def _calc_newline_numb(width, text):
    """
    Calculates the number of lines and the cell height required to fit the text
    :param width: The width of the column
    :param text: A list of all the text to be written in the table column
    :return: the cell height and the number of lines for each cell
    """
    sample_paragraph = Paragraph("S", paragraph_style)
    line_height = sample_paragraph.wrap(width - 4, 0)[1]

    total_lines = []
    cell_height = []
    cell_y = 19

    for str in text:
        paragraph = Paragraph(str, paragraph_style)
        lines_needed = paragraph.wrap(width - 4, 0)[1] // line_height
        if lines_needed == 0 or lines_needed == 1:
            lines_needed = 1
            cell_height.append(cell_y)
            total_lines.append(lines_needed)
        else:
            cell_height.append(lines_needed * 12)
            total_lines.append(lines_needed)

    return cell_height, total_lines


def _data_for_n_rows(n, width1, text1):
    """
    How much of the data can fit in n number of rows.
    :param text1: A list of all the text to be printed in the table column 1
    :param n: The number of available rows in a page
    :param width1: The width of cell 1
    :return: how many of the rows are drawable in the current page
    """
    sample_paragraph1 = Paragraph("S", paragraph_style)
    line_height1 = sample_paragraph1.wrap(width1 - 4, 0)[1]

    drawable_size0 = []
    numb_iter = 0
    for str1 in text1:
        paragraph = Paragraph(str1, paragraph_style)
        lines_needed = paragraph.wrap(width1 - 4, 0)[1] // line_height1
        if lines_needed == 0 or lines_needed == 1:
            lines_needed = 1
            drawable_size0.append(19 * lines_needed)
        else:
            drawable_size0.append(12 * lines_needed)

    drawable = drawable_size0
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

    cell_height0, numb_line0 = _calc_newline_numb(col_widths, col_data0)

    cell_height = cell_height0
    for i in range(len(numb_line0)):
        if numb_line0[i] > 1:
            numb_line0[i] *= (12 / 19)
    numb_line = sum(numb_line0)

    drawable = _data_for_n_rows(n_drawable, col_widths, col_data0)
    return cell_height, numb_line, drawable

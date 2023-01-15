from flask import (
    Flask,
    request,
    render_template,
    send_file,
    make_response,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from logging.config import dictConfig

import random
import json
import base64
import logging
from borb.pdf.pdf import PDF
from borb.pdf import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.table.fixed_column_width_table import (
    FixedColumnWidthTable as Table,
)
from borb.pdf import X11Color
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from datetime import datetime
from decimal import Decimal
from pathlib import Path

MIMETYPE = "application/xml"

# Create document
pdf = Document()

page = Page()
pdf.add_page(page)

page_layout = SingleColumnLayout(page)
page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

# add an Image
page_layout.add(
    Image(
        Path("images/fastaccounting.png"),
        width=Decimal(250),
        height=Decimal(30),
    )
)

# create a FixedColumnWidthTable

page_layout.add(
    Paragraph("Invoice", horizontal_alignment=Alignment.CENTERED, font_size=Decimal(30))
)

page_layout.add(
    Table(number_of_columns=4, number_of_rows=3)
    .add(Paragraph("Item"))
    .add(Paragraph("Num"))
    .add(Paragraph("Unit Price"))
    .add(Paragraph("Amount"))
    .add(Paragraph("Tesla"))
    .add(Paragraph("1"))
    .add(Paragraph("5,000,000"))
    .add(Paragraph("5,500,000"))
    .add(Paragraph("Ferary"))
    .add(Paragraph("1"))
    .add(Paragraph("10,000,000"))
    .add(Paragraph("11,000,000"))
    # set padding on all (implicit) TableCell objects in the FixedColumnWidthTable
    .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    # apply 'zebra striping' to the FixedColumnWidthTable
    .even_odd_row_colors(X11Color("LightGray"), X11Color("White"))
)


def _build_invoice_information():
    table_001 = Table(number_of_rows=5, number_of_columns=3)
    table_001.add(Paragraph("[Street Address]"))
    table_001.add(
        Paragraph("Date", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT)
    )
    now = datetime.now()
    table_001.add(Paragraph("%d/%d/%d" % (now.day, now.month, now.year)))
    # table_001.add(Paragraph("Company"))
    # table_001.add(Paragraph("%s" % "FAST ACCOUNTING"))
    table_001.add(Paragraph("[City, State, ZIP Code]"))
    table_001.add(
        Paragraph(
            "Invoice #", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT
        )
    )
    table_001.add(Paragraph("%d" % random.randint(1000, 10000)))
    table_001.add(Paragraph("[Phone]"))
    table_001.add(
        Paragraph(
            "Due Date", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT
        )
    )
    table_001.add(Paragraph("%d/%d/%d" % (now.day, now.month, now.year)))
    table_001.add(Paragraph("[Email Address]"))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph("[Company Website]"))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    table_001.no_borders()
    return table_001


# import pymysql


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)

# Cloud SQLに接続し、テーブルを作成する(テーブルは予めコンソールから作成しておくこと!)
# connection = pymysql.connect(host='34.84.231.41', user='root', password='Gn4+*5biC8=1nACI', db='peppol-builder')
# with connection.cursor() as cursor:
#     print(cursor.execute("show databases;"))
#     sql = '''
#     CREATE TABLE aiueo (
#        student_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#        first_name VARCHAR(50) NULL,
#        last_name VARCHAR(50) NULL,
#        birthday DATE NULL,
#        gender ENUM('F','M')
#     )'''
#     cursor.execute(sql)


@app.route("/")
def index():
    # app.logger.debug("This is debug message.")
    # app.logger.info("This is info message.")
    # app.logger.warning("This is warning message.")
    # app.logger.error("This is error message.")
    # app.logger.critical("This is critical message.")
    return render_template("main.html")


@app.route("/call_from_ajax", methods=["POST"])
def callfromajax():
    if request.method == "POST":
        # ここにPythonの処理を書く
        # app.logger.error("send_data: " + str(request.form.getlist()))
        app.logger.error("send_data2: " + str(request.form))

        try:
            encoded_string = ""
            company = "Fast Accounting Co."
            name = "岡崎優尋"
            invoice_no = request.form["data"]
            page_layout.add(_build_invoice_information())

            # Empty paragraph for spacing
            page_layout.add(Paragraph(" "))
            with open("output.pdf", "wb") as pdf_file_handle:
                PDF.dumps(pdf_file_handle, pdf)
                # logging.warning("encoded_string: " + str(encoded_string))
        except Exception as e:
            # message = str(e)
            print(e)
        with open("output.pdf", "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())
        # encoded_string = base64.b64encode("../output.pdf")
        # app.logger.error(encoded_string)
        dict = {
            "name": name,
            "invoice_no": invoice_no,
            "encoded_string": encoded_string.decode(),
        }  # 辞書
    return json.dumps(dict)


@app.route("/pdfdownload", methods=["GET"])
def pdfdownload():
    downloadFile = "output.pdf"

    return send_file(
        downloadFile,
        as_attachment=True,
        mimetype="application/xml",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)

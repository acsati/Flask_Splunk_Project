#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ALP CANER SATI, Ekim 2021

from flask import Flask, render_template, flash, redirect, url_for, request, send_file
from wtforms import Form, TextAreaField
from wtforms.fields.core import StringField
import splunk_teftis
import splunk_log_checks
import os
from logging import FileHandler, WARNING, ERROR
from logging.handlers import SMTPHandler
import datetime
import json

app = Flask(__name__)
app.secret_key = "SplunkLog"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/splunklogcheck", methods=["GET","POST"])
def splunklogcheck():
    form = QueryForm(request.form) 
    if request.method == "GET":
        return render_template("splunklogcheck.html",form=form)
    else:
        content = form.content.data
        log_type = request.form.get("log_type")
        source_type = request.form.get("source_type")
        
        if log_type=="Internal Log":
            splunk_log_checks.check_metricslog(content,source_type)
            return send_file("./results\\internal_log_result.xlsx")
             
        elif (log_type=="Winevent Log" and source_type=="Hostname"):
            splunk_log_checks.check_wineventlog(content)
            return send_file("./results\\winevent_log_result.xlsx")
        else:
            flash("Yanlış işlem tipi seçtiniz...\n\nEğer Winevent log'unu sorgulamak istiyorsanız lütfen Hostname'i seçin.","danger")
            return redirect(url_for("splunklogcheck"))

@app.route("/teftis", methods=["GET","POST"])
def teftis():
    form = TeftisForm(request.form)
    if request.method == "GET":
        return render_template("teftis.html",form=form)
    else:
        file_name = form.file_name.data
        spl_query = form.spl_query.data
        dates = request.form.get("dates")
        splunk_teftis.query(file_name,spl_query,dates)
        return send_file("results\\"+file_name+".zip")

class QueryForm(Form):
    content = TextAreaField(label="")
class TeftisForm(Form):
    file_name = StringField(label="File Name")
    spl_query = TextAreaField(label="SPL Query")

if __name__=="__main__":
    os.chdir("C:\\ScriptsForAutomation\\WebApp")
    # Error oluşursa mail ve log oluştur.
    if not app.debug:
        file_handler = FileHandler("./Logs\\Error_"+str(datetime.datetime.now()).split(" ")[0]+".log")
        file_handler.setLevel(WARNING)

        mail_handler = SMTPHandler(
            mailhost=json.load(open("config.json"))["mail_handler"]['mailhost'],
            fromaddr=json.load(open("config.json"))["mail_handler"]['fromaddr'],
            toaddrs=json.load(open("config.json"))["mail_handler"]['toaddrs'],
            subject="IOM WebApp'inde Sorun Çıktı!!")
        mail_handler.setLevel(ERROR)

        app.logger.addHandler(file_handler)
        app.logger.addHandler(mail_handler)
    app.run(host="0.0.0.0")

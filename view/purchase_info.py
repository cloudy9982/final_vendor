from flask import render_template, request, redirect, url_for, Blueprint
import sqlalchemy as db
from sqlalchemy import func
from datetime import datetime
import math
from sqlalchemy.engine import Engine
from sqlalchemy import event
import traceback
import sys


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


pc_info_app = Blueprint('purchase_info_app', __name__, url_prefix="/pc_info")

path_to_db = "./db/LabPropertyMgt20211231.db"
table_name_PurchasingInfo = 'PurchasingInfo'
table_name_Supplier = 'Supplier'
table_name_Member = 'Member'
engine = db.create_engine(f'sqlite:///{path_to_db}', native_datetime=True)


metadata = db.MetaData()
table_PurchasingInfo = db.Table(
    table_name_PurchasingInfo, metadata,  autoload_with=engine)
table_Supplier = db.Table(table_name_Supplier, metadata, autoload_with=engine)
table_Member = db.Table(table_name_Member, metadata, autoload_with=engine)


@pc_info_app.route('/')
def index():  # show Purchasinginfo

    page = int(request.args.get('page') if request.args.get('page') else 1)
    each_page = 30

    connection = engine.connect()
    query = db.select(func.count()).select_from(table_PurchasingInfo)
    proxy = connection.execute(query)
    total_pages = math.ceil(proxy.fetchall()[0][0]/each_page)

    query = db.select(table_PurchasingInfo).limit(
        each_page).offset((page-1)*each_page)
    proxy = connection.execute(query)
    results = proxy.fetchall()
    print(results[0].keys())

    connection.close()

    return render_template('purchasinginfo_table.html',
                           page_header="所有申請之採購清單",
                           total_pages=total_pages,
                           outputs=results,
                           page=page)


@pc_info_app.route('/pcinfo_submit', methods=["GET", "POST"])
def Purchasing_submit():
    PurchasingList_ID_GENERATE = "None"

    if request.method == "POST":
        try:
            connection = engine.connect()
            query = db.select(table_Member.c.Member_ID).order_by(
                table_Member.c.Member_ID)
            proxy = connection.execute(query)
            id_list_member = [idx[0] for idx in proxy.fetchall()]

            query = db.select(table_Supplier.c.Supplier_ID).order_by(
                table_Supplier.c.Supplier_ID)
            proxy = connection.execute(query)
            sup_id_list = [idx[0] for idx in proxy.fetchall()]

            query = db.select(table_PurchasingInfo.c.Purchaser_ID).order_by(
                table_PurchasingInfo.c.Purchaser_ID)
            proxy = connection.execute(query)
            pcer_id_list = [idx[0] for idx in proxy.fetchall()]

            if request.form['Applicant_ID']:
                query = db.select(table_PurchasingInfo.c.List_ID).select_from(
                    table_PurchasingInfo).order_by(table_PurchasingInfo.c.List_ID.desc())
                proxy = connection.execute(query)
                PurchasingList_ID_GENERATE = 'P' + \
                    str(int([idx[0]
                        for idx in proxy.fetchall()][0].split('P')[1])+1)

                query = db.insert(table_PurchasingInfo).values(Applicant_ID=request.form['Applicant_ID'], List_ID=PurchasingList_ID_GENERATE, Purchaser_ID=request.form['Purchaser_ID'], AcceptDate=request.form['AcceptDate'],
                                                               TransactionDate=request.form['TransactionDate'], DeliveryDate=request.form['DeliveryDate'], SubmitDate=request.form['SubmitDate'], Supplier_ID=request.form['Supplier_ID'])
                proxy = connection.execute(query)
                connection.commit()
            else:
                raise Exception
        except Exception as e:
            error_class = e.__class__.__name__  # 取得錯誤類型
            detail = e.args[0] if len(e.args) >= 1 else ""  # 取得詳細內容
            cl, exc, tb = sys.exc_info()  # 取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
            fileName = lastCallStack[0]  # 取得發生的檔案名稱
            lineNum = lastCallStack[1]  # 取得發生的行號
            funcName = lastCallStack[2]  # 取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(
                fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            return render_template('purchasinginfo_submit.html',
                                   page_header="建立採購清單資訊", id_list_member=id_list_member, sup_id_list=sup_id_list, pcer_id_list=pcer_id_list, status="Failed",
                                   PurchasingList_ID_GENERATE=PurchasingList_ID_GENERATE)
        else:
            return render_template('purchasinginfo_submit.html',
                                   page_header="建立採購清單資訊", id_list_member=id_list_member, sup_id_list=sup_id_list, pcer_id_list=pcer_id_list, status="Success",
                                   PurchasingList_ID_GENERATE=PurchasingList_ID_GENERATE)
        finally:
            connection.close()

    if request.method == "GET":
        connection = engine.connect()
        query = db.select(table_Member.c.Member_ID).order_by(
            table_Member.c.Member_ID)
        proxy = connection.execute(query)
        id_list_member = [idx[0] for idx in proxy.fetchall()]

        query = db.select(table_Supplier.c.Supplier_ID).order_by(
            table_Supplier.c.Supplier_ID)
        proxy = connection.execute(query)
        sup_id_list = [idx[0] for idx in proxy.fetchall()]

        query = db.select(table_PurchasingInfo.c.Purchaser_ID).order_by(
            table_PurchasingInfo.c.Purchaser_ID)
        proxy = connection.execute(query)
        pcer_id_list = [idx[0] for idx in proxy.fetchall()]

        connection.close()

        return render_template('purchasinginfo_submit.html',
                               page_header="建立採購清單資訊", id_list_member=id_list_member, sup_id_list=sup_id_list, pcer_id_list=pcer_id_list)


@pc_info_app.route('/pcinfo_edit', methods=["GET", "POST"])
def purchasing_edit_info():

    if request.method == "POST":
        try:
            connection = engine.connect()  # connection 要放在view function中，否則會出現thread error
            query = db.select(table_Member.c.Member_ID).order_by(
                table_Member.c.Member_ID)
            proxy = connection.execute(query)
            id_list_member = [idx[0] for idx in proxy.fetchall()]

            query = db.select(table_PurchasingInfo.c.List_ID).order_by(
                table_PurchasingInfo.c.List_ID)
            proxy = connection.execute(query)
            id_list = [idx[0] for idx in proxy.fetchall()]

            query = db.select(table_Supplier.c.Supplier_ID).order_by(
                table_Supplier.c.Supplier_ID)
            proxy = connection.execute(query)
            sup_id_list = [idx[0] for idx in proxy.fetchall()]

            query = db.select(table_PurchasingInfo.c.Purchaser_ID).order_by(
                table_PurchasingInfo.c.Purchaser_ID)
            proxy = connection.execute(query)
            pcer_id_list = [idx[0] for idx in proxy.fetchall()]

            if request.form['Applicant_ID']:
                query = db.update(table_PurchasingInfo).where(table_PurchasingInfo.c.List_ID == request.form['List_ID']).values(Applicant_ID=request.form['Applicant_ID'], Purchaser_ID=request.form['Purchaser_ID'], AcceptDate=request.form['AcceptDate'],
                                                                                                                                TransactionDate=request.form['TransactionDate'], DeliveryDate=request.form['DeliveryDate'], SubmitDate=request.form['SubmitDate'], Supplier_ID=request.form['Supplier_ID'])
                proxy = connection.execute(query)

            else:
                raise Exception
        except Exception as e:
            error_class = e.__class__.__name__  # 取得錯誤類型
            detail = e.args[0] if len(e.args) >= 1 else ""  # 取得詳細內容
            cl, exc, tb = sys.exc_info()  # 取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
            fileName = lastCallStack[0]  # 取得發生的檔案名稱
            lineNum = lastCallStack[1]  # 取得發生的行號
            funcName = lastCallStack[2]  # 取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(
                fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            return render_template('purchasinginfo_edit_info.html',
                                   page_header="修改採購清單資訊", id_list=id_list, id_list_member=id_list_member, sup_id_list=sup_id_list, pcer_id_list=pcer_id_list, status="Failed")
        else:
            return render_template('purchasinginfo_edit_info.html',
                                   page_header="修改採購清單資訊", id_list=id_list, id_list_member=id_list_member, sup_id_list=sup_id_list, pcer_id_list=pcer_id_list, status="Success")
        finally:
            # Close connection
            connection.close()

    if request.method == "GET":
        connection = engine.connect()  # connection 要放在view function中，否則會出現thread error
        query = db.select(table_Member.c.Member_ID).order_by(
            table_Member.c.Member_ID)
        proxy = connection.execute(query)
        id_list_member = [idx[0] for idx in proxy.fetchall()]

        query = db.select(table_PurchasingInfo.c.List_ID).order_by(
            table_PurchasingInfo.c.List_ID)
        proxy = connection.execute(query)
        id_list = [idx[0] for idx in proxy.fetchall()]

        query = db.select(table_Supplier.c.Supplier_ID).order_by(
            table_Supplier.c.Supplier_ID)
        proxy = connection.execute(query)
        sup_id_list = [idx[0] for idx in proxy.fetchall()]

        query = db.select(table_PurchasingInfo.c.Purchaser_ID).order_by(
            table_PurchasingInfo.c.Purchaser_ID)
        proxy = connection.execute(query)
        pcer_id_list = [idx[0] for idx in proxy.fetchall()]

        connection.close()
        return render_template('purchasinginfo_edit_info.html',
                               page_header="修改採購清單資訊", id_list=id_list, id_list_member=id_list_member, sup_id_list=sup_id_list, pcer_id_list=pcer_id_list)

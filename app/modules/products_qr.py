from fastapi import APIRouter
import app.utils as utils
import base64
import qrcode
from os import remove
from pymongo import MongoClient
from configs import get_values_database_postgress, get_values_database_nosql_collection_qr, get_values_hosting


router = APIRouter(
    prefix="/products-qr",
    tags=["products-qr"])

host, port, db, usr, pwd = get_values_database_postgress()

uri_qr, database_no_sql_qr, collection_db_qr = get_values_database_nosql_collection_qr()

hosting = get_values_hosting()


@router.get("/{item_id}")
async def get_qr_by_id_product(item_id: str):
    try:
        client_mongo = MongoClient(uri_qr)
        db_mongo = client_mongo[database_no_sql_qr]
        collection_qr = db_mongo[collection_db_qr]
        for qr_base64 in collection_qr.find({ "id": item_id}):
            qr_base64= qr_base64['b64_string']
            qr_base64 = str(qr_base64)
            qr_base64 = qr_base64[2:-1]
        dict_json = {"result": qr_base64}
    except Exception as error:
        print(f'Ocurrió un error inesperado: {error}')
        dict_json = {"result": "error"}
    return dict_json


@router.post("/")
async def update_url_qr():
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        query = "SELECT id_producto FROM producto "
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        client_mongo = MongoClient(uri_qr )
        db_mongo = client_mongo[database_no_sql_qr]
        collection_qr = db_mongo[collection_db_qr]
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                url_qr = hosting
                url_qr = str(url_qr)+ row[0]
                img = qrcode.make(url_qr)
                img.save("qr_auxiliar.jpg")
                with open("qr_auxiliar.jpg", "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read())
                remove("qr_auxiliar.jpg")
                mydict = { "id": row[0], "b64_string": str(b64_string) }
                qr_result = collection_qr.insert_one(mydict)
                print('insertado en mongodb')
        client_mongo.close()
    except Exception as error:
        dict_json = {"status": "error"}
        print(f'Ocurrió un error inesperado: {error}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json

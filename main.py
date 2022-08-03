from fastapi import FastAPI
from pydantic import BaseModel
import utils
from configparser import ConfigParser
from fastapi.middleware.cors import CORSMiddleware
import base64
import qrcode
from os import remove
from pymongo import MongoClient

file = "config.ini"
config = ConfigParser()
config.read(file)
app = FastAPI()

origins = [
    "https://coquitofrontadmin.herokuapp.com",
    "http://localhost",
    "http://localhost:3000",
    "https://adminv2.ferrerepuestoscoquito.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UnidadMedida(BaseModel):
    codigo: str
    descripcion: str

class TipoProducto(BaseModel):
    descripcion: str

class Producto(BaseModel):
    id_tipo_producto: int
    nombre: str
    descripcion: str
    precio_compra: float
    precio_venta_menor: float
    precio_venta_mayor: float
    stock: float
    id_unidad_medida: int

host = config['database']['host_heroku']
port = config['database']['port_heroku']
db = config['database']['db_heroku']
usr = config['database']['usr_heroku']
pwd = config['database']['pwd_heroku']

@app.get("/tipo-producto")
def get_all_tipo_producto():
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        query = "select row_to_json(row) from (SELECT id, descripcion FROM tipo_productos) row"
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                dict_json.append(row[0])
    except Exception as error:
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.get("/tipo-producto/{item_id}")
def get_by_id_tipo_producto(item_id: int):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "select row_to_json(row) from (SELECT id, descripcion FROM tipo_productos where id = %s) row"
        cursor.execute(select_query,(item_id,))
        print('Query ejecutado')
        if cursor.rowcount > 0:
            dict_json = cursor.fetchone()
            dict_json = dict_json[0]
    except Exception as error:
        dict_json = []
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.post("/tipo-producto")
def insert_tipo_producto(tipo_producto: TipoProducto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "insert into tipo_productos (descripcion) values (%s)"
        cursor.execute(select_query,(tipo_producto.descripcion,))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"insertado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.put("/tipo-producto/{item_id}")
def update_tipo_producto(item_id: int, tipo_producto: TipoProducto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "update tipo_productos set descripcion = (%s) where id = (%s)"
        cursor.execute(select_query,(tipo_producto.descripcion, item_id))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"actualizado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.get("/products")
def get_all_products():
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        query = "select row_to_json(row) from (SELECT id_producto, t.descripcion as categoria, nombre, p.descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, concat(stock,' ',um.descripcion) as stock FROM producto p inner join tipo_productos t on p.id_tipo_producto = t.id inner join unidad_medida um on p.id_unidad_medida = um.id) row"
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                dict_json.append(row[0])
    except Exception as error:
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.get("/products/{item_id}")
def get_by_id_products(item_id: str):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "select row_to_json(row) from (SELECT id_tipo_producto, nombre, descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, id_unidad_medida  FROM producto where id_producto = %s) row"
        cursor.execute(select_query,(item_id,))
        print('Query ejecutado')
        if cursor.rowcount > 0:
            dict_json = cursor.fetchone()
            dict_json = dict_json[0]
    except Exception as error:
        dict_json = []
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json



@app.get("/products-qr/{item_id}")
def get_qr_by_id_product(item_id: str):
    try:
        client_mongo = MongoClient(config['mongodb']['uri'] )
        db_mongo = client_mongo[config['mongodb']['database']]
        collection_qr = db_mongo[config['mongodb']['collection_qr']]
        for qr_base64 in collection_qr.find({ "id": item_id}):
            qr_base64= qr_base64['b64_string']
            qr_base64 = str(qr_base64)
            qr_base64 = qr_base64[2:-1]
        dict_json = {"result": qr_base64}
    except Exception as error:
        print(f'Ocurrió un error inesperado: {error}')
        dict_json = {"result": "error"}
    return dict_json


@app.post("/products")
def insert_producto(producto: Producto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "insert into producto (id_tipo_producto, nombre, descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, id_unidad_medida,fecha_registro, fecha_actualizacion) values (%s,%s, %s, %s, %s, %s, %s, %s,current_timestamp, current_timestamp) RETURNING id_producto"
        cursor.execute(select_query,(producto.id_tipo_producto,producto.nombre,producto.descripcion, producto.precio_compra, producto.precio_venta_menor, producto. precio_venta_mayor, producto.stock, producto.id_unidad_medida))
        conn.commit()
        print('Query ejecutado')
        if cursor.rowcount > 0:
            dict_json = cursor.fetchone()
            dict_json = dict_json[0]
            url_qr = config['hosting']['url_hosting'] 
            url_qr = str(url_qr)+ dict_json
            img = qrcode.make(url_qr)
            print('qr generado correctamente')
            img.save("qr_auxiliar.jpg")
            with open("qr_auxiliar.jpg", "rb") as img_file:
                b64_string = base64.b64encode(img_file.read())
            remove("qr_auxiliar.jpg")
            client_mongo = MongoClient(config['mongodb']['uri'] )
            db_mongo = client_mongo[config['mongodb']['database']]
            collection_qr = db_mongo[config['mongodb']['collection_qr']]
            mydict = { "id": dict_json, "b64_string": str(b64_string) }
            qr_result = collection_qr.insert_one(mydict)
            print("Qr Guardado correctamente")
            client_mongo.close()
        dict_json = {"status":"ok"}
    except Exception as error:
        dict_json = {"status": "error"}
        print(f'Ocurrió un error inesperado: {error}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json




@app.get("/update-url-qr")
def update_url_qr():
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        query = "SELECT id_producto FROM producto "
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        client_mongo = MongoClient(config['mongodb']['uri'] )
        db_mongo = client_mongo[config['mongodb']['database']]
        collection_qr = db_mongo[config['mongodb']['collection_qr']]
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                url_qr = config['hosting']['url_hosting'] 
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



@app.put("/products/{item_id}")
def update_producto(item_id: str, producto: Producto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "update producto set id_tipo_producto = (%s) , nombre = (%s), descripcion = (%s), precio_compra = (%s), precio_venta_menor = (%s), precio_venta_mayor = (%s), stock = (%s), id_unidad_medida = (%s), fecha_actualizacion = (current_timestamp) where id_producto = (%s)"
        cursor.execute(select_query,(producto.id_tipo_producto,producto.nombre,producto.descripcion, producto.precio_compra, producto.precio_venta_menor, producto. precio_venta_mayor, producto.stock, producto.id_unidad_medida, item_id))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"actualizado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.delete("/products/{item_id}")
def delete_producto(item_id: str):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "delete from producto where id_producto = (%s)"
        cursor.execute(select_query,(item_id,))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"eliminado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print(f'Ocurrió un error inesperado: {error}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.get("/unidad-medida")
def get_all_unidad_medida():
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        query = "select row_to_json(row) from (SELECT id,codigo, descripcion FROM unidad_medida) row"
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                dict_json.append(row[0])
    except Exception as error:
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.get("/unidad-medida/{item_id}")
def get_by_id_unidad_medida(item_id: int):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "select row_to_json(row) from (SELECT id,codigo, descripcion FROM unidad_medida where id = %s) row"
        cursor.execute(select_query,(item_id,))
        print('Query ejecutado')
        if cursor.rowcount > 0:
            dict_json = cursor.fetchone()
            dict_json = dict_json[0]
    except Exception as error:
        dict_json = []
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@app.post("/unidad-medida")
def insert_unidad_medida(unidad_medida: UnidadMedida):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "insert into unidad_medida (codigo,descripcion) values (%s,%s)"
        cursor.execute(select_query,(unidad_medida.codigo,unidad_medida.descripcion,))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"insertado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json



@app.put("/unidad-medida/{item_id}")
def update_unidad_medida(item_id: int, unidad_medida: UnidadMedida):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "update unidad_medida set codigo = (%s) , descripcion = (%s) where id = (%s)"
        cursor.execute(select_query,(unidad_medida.codigo,unidad_medida.descripcion, item_id))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"actualizado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


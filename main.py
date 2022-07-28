from fastapi import FastAPI
from pydantic import BaseModel
import utils
from configparser import ConfigParser

file = "config.ini"
config = ConfigParser()
config.read(file)
app = FastAPI()

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
        query = "select row_to_json(row) from (SELECT id_tipo_producto, nombre, descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, id_unidad_medida  FROM producto) row"
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


@app.post("/products")
def insert_producto(producto: Producto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "insert into producto (id_tipo_producto, nombre, descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, id_unidad_medida) values (%s,%s, %s, %s, %s, %s, %s, %s) RETURNING id_producto"
        cursor.execute(select_query,(producto.id_tipo_producto,producto.nombre,producto.descripcion, producto.precio_compra, producto.precio_venta_menor, producto. precio_venta_mayor, producto.stock, producto.id_unidad_medida))
        conn.commit()
        print('Query ejecutado')
        if cursor.rowcount > 0:
            dict_json = cursor.fetchone()
            dict_json = dict_json[0]
        #dict_json = {"status":"insertado"}
    except Exception as error:
        dict_json = {"status": "error"}
        print('Ocurrió un error inesperado')
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
        select_query = "update producto set id_tipo_producto = (%s) , nombre = (%s), descripcion = (%s), precio_compra = (%s), precio_venta_menor = (%s), precio_venta_mayor = (%s), stock = (%s), id_unidad_medida = (%s) where id_producto = (%s)"
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


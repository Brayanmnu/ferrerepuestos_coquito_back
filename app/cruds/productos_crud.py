from fastapi import APIRouter
from pydantic import BaseModel
import app.utils as utils
import base64
import qrcode
from os import remove
from pymongo import MongoClient
from configs import get_values_database_postgress, get_values_hosting, get_values_database_nosql_collection_qr

router = APIRouter(
    prefix="/products",
    tags=["products"]
    )

host, port, db, usr, pwd = get_values_database_postgress()

hosting = get_values_hosting()

uri_qr, database_no_sql_qr, collection_db_qr = get_values_database_nosql_collection_qr()

class Producto(BaseModel):
    id_tipo_producto: int
    id_sub_tipo: str| None = None
    desc_sub_tipo: str| None = None
    id_de: str| None = None
    desc_de: str| None = None
    id_a: str| None = None
    desc_a: str| None = None
    descripcion: str| None = None
    precio_compra: float
    precio_venta_menor: float
    precio_venta_mayor: float
    stock: float
    id_unidad_medida: int

@router.get("/")
async def get_all_products():
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        query = "select row_to_json(row) from (SELECT id_producto, t.descripcion as categoria, nombre, p.descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, um.descripcion as uni_medida, estado FROM producto p inner join tipo_productos t on p.id_tipo_producto = t.id inner join unidad_medida um on p.id_unidad_medida = um.id) row"
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                dict_json.append(row[0])
    except BaseException as error:
        print(f'Ocurrió un error inesperado: {error.__str__}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@router.get("/v2/{nroPag}/{productType}")
async def get_all_products_v2(nroPag: str, productType:str, idSubProductType:str| None = None, deRequest:str| None = None, aRequest:str| None = None):
    dict_json = []
    try:
        filter = ""
        if idSubProductType:
            filter = f" and s.id  = '{idSubProductType}' "
        if deRequest:
            filter = filter + f"and m.id = '{deRequest}' "
        if aRequest:
            filter = filter + f"and me.id = '{aRequest}' "

        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        sub_query_nombre = "concat(s.descripcion ,(case when m.descripcion!='' then CONCAT(' DE ', m.descripcion) END) ,(case when me.descripcion!='' then CONCAT(' A ', me.descripcion) END) ,' ', p.descripcion) as nombre "
        sub_query_columns = f"select count(*) OVER() AS total_elements, p.id_producto, p.stock, um.descripcion as uni_medida, {sub_query_nombre} , precio_venta_menor, precio_venta_mayor,precio_compra "
        sub_query_tables = " from producto p left join sub_tipo_producto s on p.id_sub_tipo_producto =s.id left join medida m on p.de =m.id left join medida me on p.a= me.id inner join unidad_medida um on p.id_unidad_medida = um.id "
        query = f"select row_to_json(row) from ( {sub_query_columns} {sub_query_tables} where p.estado = 1 and p.id_tipo_producto = {productType} {filter} order by nombre limit 10 offset {nroPag}) row"
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        if cursor.rowcount > 0:
            records = cursor.fetchall()
            for row in records:
                dict_json.append(row[0])
    except BaseException as error:
        print(f'Ocurrió un error inesperado: {error.__str__}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json


@router.get("/{item_id}")
async def get_by_id_products(item_id: str):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "select row_to_json(row) from (SELECT id_sub_tipo_producto, de as id_de, a as id_a, descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, id_unidad_medida  FROM producto where id_producto = %s) row"
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


@router.get("/detail/{item_id}")
async def get_by_id_product_detail(item_id: str):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        sub_query_nombre = "concat(s.descripcion ,(case when m.descripcion!='' then CONCAT(' DE ', m.descripcion) END) ,(case when me.descripcion!='' then CONCAT(' A ', me.descripcion) END) ,' ', p.descripcion) as nombre "
        sub_query_tables = " from producto p left join sub_tipo_producto s on p.id_sub_tipo_producto =s.id left join medida m on p.de =m.id left join medida me on p.a= me.id inner join unidad_medida um on p.id_unidad_medida = um.id "
        select_query = f"select row_to_json(row) from (SELECT {sub_query_nombre} , precio_compra, precio_venta_menor, precio_venta_mayor, stock, um.descripcion as uni_medida  {sub_query_tables} where p.id_producto = %s) row"
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

@router.post("/")
async def insert_producto(producto: Producto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        
        if producto.desc_sub_tipo:
            insert_query = "insert into sub_tipo_producto (descripcion , id_tipo_producto) values (%s,%s) RETURNING id"
            cursor.execute(insert_query,(producto.desc_sub_tipo, producto.id_tipo_producto))
            conn.commit()
            print('sub_tipo_producto insertado')
            if cursor.rowcount > 0:
                dict_json = cursor.fetchone()
                id_sub_tipo_product = dict_json[0]
        else:
            id_sub_tipo_product = producto.id_sub_tipo

        if producto.desc_de:
            insert_query = "insert into medida (descripcion , id_tipo_producto) values (%s,%s) RETURNING id"
            cursor.execute(insert_query,(producto.desc_de, producto.id_tipo_producto))
            conn.commit()
            print('medida DE insertado')
            if cursor.rowcount > 0:
                dict_json = cursor.fetchone()
                id_de = dict_json[0]
        else:
            id_de = producto.id_de
        if producto.desc_a:
            insert_query = "insert into medida (descripcion , id_tipo_producto) values (%s,%s) RETURNING id"
            cursor.execute(insert_query,(producto.desc_a, producto.id_tipo_producto))
            conn.commit()
            print('medida A insertado')
            if cursor.rowcount > 0:
                dict_json = cursor.fetchone()
                id_a = dict_json[0]
        else:
            id_a = producto.id_a

        if not id_de:
            id_de = None

        if not id_a:
            id_a = None

        select_query = "insert into producto (id_tipo_producto, id_sub_tipo_producto, de ,a , descripcion, precio_compra, precio_venta_menor, precio_venta_mayor, stock, id_unidad_medida,fecha_registro, fecha_actualizacion) values (%s,%s, %s, %s, %s, %s, %s,%s,%s, %s,current_timestamp, current_timestamp) RETURNING id_producto"
        cursor.execute(select_query,(producto.id_tipo_producto,id_sub_tipo_product, id_de,id_a, producto.descripcion, producto.precio_compra, producto.precio_venta_menor, producto.precio_venta_mayor, producto.stock, producto.id_unidad_medida))
        conn.commit()
        print('Query ejecutado')
        if cursor.rowcount > 0:
            dict_json = cursor.fetchone()
            dict_json = dict_json[0]
            url_qr = hosting
            url_qr = str(url_qr)+ dict_json
            img = qrcode.make(url_qr)
            print('qr generado correctamente')
            img.save("qr_auxiliar.jpg")
            with open("qr_auxiliar.jpg", "rb") as img_file:
                b64_string = base64.b64encode(img_file.read())
            remove("qr_auxiliar.jpg")
            client_mongo = MongoClient(uri_qr)
            db_mongo = client_mongo[database_no_sql_qr]
            collection_qr = db_mongo[collection_db_qr]
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


@router.put("/{item_id}")
async def update_producto(item_id: str, producto: Producto):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        
        if producto.desc_sub_tipo:
            insert_query = "insert into sub_tipo_producto (descripcion , id_tipo_producto) values (%s,%s) RETURNING id"
            cursor.execute(insert_query,(producto.desc_sub_tipo, producto.id_tipo_producto))
            conn.commit()
            print('sub_tipo_producto insertado')
            if cursor.rowcount > 0:
                dict_json = cursor.fetchone()
                id_sub_tipo_product = dict_json[0]
        else:
            id_sub_tipo_product = producto.id_sub_tipo

        if producto.desc_de:
            insert_query = "insert into medida (descripcion , id_tipo_producto) values (%s,%s) RETURNING id"
            cursor.execute(insert_query,(producto.desc_de, producto.id_tipo_producto))
            conn.commit()
            print('medida DE insertado')
            if cursor.rowcount > 0:
                dict_json = cursor.fetchone()
                id_de = dict_json[0]
        else:
            id_de = producto.id_de

        if producto.desc_a:
            insert_query = "insert into medida (descripcion , id_tipo_producto) values (%s,%s) RETURNING id"
            cursor.execute(insert_query,(producto.desc_a, producto.id_tipo_producto))
            conn.commit()
            print('medida A insertado')
            if cursor.rowcount > 0:
                dict_json = cursor.fetchone()
                id_a = dict_json[0]
        else:
            id_a = producto.id_a
        
        select_query = "update producto set id_sub_tipo_producto = (%s), de = (%s), a = (%s) , descripcion = (%s), precio_compra = (%s), precio_venta_menor = (%s), precio_venta_mayor = (%s), stock = (%s), id_unidad_medida = (%s), fecha_actualizacion = (current_timestamp) where id_producto = (%s)"
        cursor.execute(select_query,(id_sub_tipo_product, id_de, id_a, producto.descripcion, producto.precio_compra, producto.precio_venta_menor, producto.precio_venta_mayor, producto.stock, producto.id_unidad_medida, item_id))
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


@router.post("/delete/{item_id}")
async def delete_producto(item_id: str):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        select_query = "update producto set estado=0 where id_producto = (%s)"
        cursor.execute(select_query,(item_id,))
        conn.commit()
        print('Query ejecutado')
        dict_json = {"status":"eliminacion logica"}
    except Exception as error:
        dict_json = {"status": "error"}
        print(f'Ocurrió un error inesperado: {error}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json

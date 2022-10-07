from fastapi import APIRouter
from pydantic import BaseModel
import app.utils as utils
from configs import get_values_database_postgress

router = APIRouter(
    prefix="/medida",
    tags=["medida"]
    )

host, port, db, usr, pwd = get_values_database_postgress()

@router.get("/de/{subProductType}")
async def get_de_by_sub_product_type(subProductType:str):
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        
        query = f"select row_to_json(row) from ( select distinct de as id,m.descripcion  from producto p inner join medida m on p.de =m.id where id_sub_tipo_producto ='{subProductType}' order by de) row"
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


@router.get("/a/{subProductType}")
async def get_a_by_sub_product_type(subProductType:str):
    dict_json = []
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        
        query = f"select row_to_json(row) from ( select distinct a as id,m.descripcion  from producto p inner join medida m on p.a =m.id where id_sub_tipo_producto ='{subProductType}' order by a) row"
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


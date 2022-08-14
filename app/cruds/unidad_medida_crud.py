from fastapi import APIRouter
from pydantic import BaseModel
import app.utils as utils
from configs import get_values_database_postgress

host, port, db, usr, pwd = get_values_database_postgress()

router = APIRouter(
    prefix="/unidad-medida",
    tags=["unidad-medida"]
    )

class UnidadMedida(BaseModel):
    codigo: str
    descripcion: str


@router.get("/")
async def get_all_unidad_medida():
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


@router.get("/{item_id}")
async def get_by_id_unidad_medida(item_id: int):
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


@router.post("/")
async def insert_unidad_medida(unidad_medida: UnidadMedida):
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



@router.put("/{item_id}")
async def update_unidad_medida(item_id: int, unidad_medida: UnidadMedida):
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

from fastapi import APIRouter
from pydantic import BaseModel
import app.utils as utils
from configs import get_values_database_postgress

router = APIRouter(
    prefix="/medida",
    tags=["medida"]
    )

host, port, db, usr, pwd = get_values_database_postgress()

@router.get("/")
async def get_all_or_by_product_type(productType:str| None = None):
    dict_json = []
    try:
        filter = ""
        if productType:
            filter = f" where id_tipo_producto = '{productType}' "

        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        
        query = f"select row_to_json(row) from ( select id, descripcion from medida {filter} order by descripcion) row"
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


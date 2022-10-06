from fastapi import APIRouter
from pydantic import BaseModel
import app.utils as utils
from configs import get_values_database_postgress
from typing import  List



router = APIRouter(
    prefix="/proveedor",
    tags=["proveedor"]
    )

host, port, db, usr, pwd = get_values_database_postgress()

class Contacto(BaseModel):
    telefono: str

class Proveedor(BaseModel):
    nombres_razon: str
    apellidos: str
    id_tipo_documento: int
    nro_doc: str
    direccion: str
    contacto: List[Contacto]
    

@router.post("/")
async def insert_proveedor(proveedor: Proveedor):
    try:
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        insert_query_persona = "insert into persona (nombres_razon_social,apellidos,id_tipo_documento,nro_doc,direccion,fecha_registro,fecha_actualizacion) values (%s,%s,%s,%s,%s,current_timestamp,current_timestamp) RETURNING id_persona"
        cursor.execute(insert_query_persona,(proveedor.nombres_razon,proveedor.apellidos,proveedor.id_tipo_documento,proveedor.nro_doc,proveedor.direccion,))
        conn.commit()
        print('Query persona ejecutado')
        if cursor.rowcount > 0:
            response_insert = cursor.fetchone()
            id_persona = response_insert[0]
            insert_query_proveedor = "insert into proveedor (id_persona) values (%s)"
            cursor.execute(insert_query_proveedor,(id_persona,))
            conn.commit()
            print('Query proveedor ejecutado')
            for contacto in proveedor.contacto:
                insert_query_contacto = "insert into contacto (id_persona,telefono) values (%s,%s)"
                cursor.execute(insert_query_contacto,(id_persona,contacto.telefono))
                conn.commit()
                print('Query contacto ejecutado')
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

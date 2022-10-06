from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.cruds import productos_crud , tipo_producto_crud ,  unidad_medida_crud, proveedor_crud, sub_product_type_crud, medida_crud
from app.modules import products_qr, login

app = FastAPI()

'''
SECCION DONDE SE LLAMAN A LAS APIS DESARROLLADAS
'''
# CRUDS
app.include_router(tipo_producto_crud.router)
app.include_router(productos_crud.router)
app.include_router(unidad_medida_crud.router)
app.include_router(proveedor_crud.router)
app.include_router(sub_product_type_crud.router)
app.include_router(medida_crud.router)

#MODULES
app.include_router(products_qr.router)
app.include_router(login.router)


'''
SECCION DONDE SE AGREGAN LOS CORS
'''
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


'''
SECCION DONDE SE INICIALIZA LA APLICACION
'''
@app.get("/")
async def root():
    return {"message": "WELCOME TO APP FERREREPUESTOS-COQUITO"}


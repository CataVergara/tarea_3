from fastapi import FastAPI, Depends, HTTPException
from lista_doble import ListaVuelos
from database import get_db, engine
from sqlalchemy.orm import Session
from models import Base, Vuelo
from schemas import VueloCreate, VueloOut

Base.metadata.create_all(bind=engine)

app = FastAPI()
lista_vuelos = ListaVuelos()

@app.post("/vuelos", response_model=VueloOut)
def agregar_vuelo(vuelo: VueloCreate, db: Session = Depends(get_db)):
    db_vuelo = Vuelo(**vuelo.dict())
    db.add(db_vuelo)
    db.commit()
    db.refresh(db_vuelo)
    if vuelo.estado == "emergencia":
        lista_vuelos.insertar_al_frente(db_vuelo)
    else:
        lista_vuelos.insertar_al_final(db_vuelo)
    return db_vuelo

@app.get("/vuelos/total")
def total():
    return {"total": lista_vuelos.longitud()}

@app.get("/vuelos/proximo", response_model=VueloOut)
def proximo():
    vuelo = lista_vuelos.obtener_primero()
    if not vuelo:
        raise HTTPException(status_code=404, detail="No hay vuelos")
    return vuelo

@app.get("/vuelos/ultimo", response_model=VueloOut)
def ultimo():
    vuelo = lista_vuelos.obtener_ultimo()
    if not vuelo:
        raise HTTPException(status_code=404, detail="No hay vuelos")
    return vuelo

@app.post("/vuelos/insertar", response_model=VueloOut)
def insertar(vuelo: VueloCreate, posicion: int, db: Session = Depends(get_db)):
    db_vuelo = Vuelo(**vuelo.dict())
    db.add(db_vuelo)
    db.commit()
    db.refresh(db_vuelo)
    lista_vuelos.insertar_en_posicion(db_vuelo, posicion)
    return db_vuelo

@app.delete("/vuelos/extraer", response_model=VueloOut)
def extraer(posicion: int):
    vuelo = lista_vuelos.extraer_de_posicion(posicion)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Posición inválida")
    return vuelo

@app.get("/vuelos/lista", response_model=list[VueloOut])
def listar():
    return lista_vuelos.recorrer_lista()

@app.patch("/vuelos/reordenar")
def reordenar():
    vuelos = lista_vuelos.recorrer_lista()
    lista_vuelos.__init__()
    for vuelo in vuelos:
        if vuelo.estado == "retrasado":
            lista_vuelos.insertar_al_final(vuelo)
        elif vuelo.estado == "emergencia":
            lista_vuelos.insertar_al_frente(vuelo)
        else:
            lista_vuelos.insertar_al_final(vuelo)
    return {"detalle": "Reordenado por estado"}
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Request,status
from app.dependencies import management_auth
from app.schemas.people import PersonCreate,PersonResponse
from app.schemas.learn import EnrollmentSessionOut
router=APIRouter(prefix="/people",tags=["people"],dependencies=[Depends(management_auth)])
@router.post("",response_model=PersonResponse,status_code=201)
def create(body:PersonCreate,request:Request): return request.app.state.container.people.create(body.name)
@router.get("",response_model=list[PersonResponse])
def list_people(request:Request): return request.app.state.container.people.list()
@router.get("/{person_id}",response_model=PersonResponse)
def get_person(person_id:UUID,request:Request):
    person=request.app.state.container.people.get(person_id)
    if not person: raise HTTPException(404,detail={"code":"INVALID_PERSON","message":"Person not found"})
    return person
@router.delete("/{person_id}",status_code=204)
def delete_person(person_id:UUID,request:Request):
    if not request.app.state.container.people.deactivate(person_id): raise HTTPException(404,detail={"code":"INVALID_PERSON","message":"Person not found"})
@router.post("/{person_id}/enrollment",response_model=EnrollmentSessionOut,status_code=201)
def enrollment(person_id:UUID,request:Request):
    c=request.app.state.container
    if not c.people.get(person_id): raise HTTPException(404,detail={"code":"INVALID_PERSON","message":"Person not found"})
    return c.sessions.create(person_id)

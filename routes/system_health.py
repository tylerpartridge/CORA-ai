from fastapi import APIRouter, Response

router = APIRouter()

@router.head("/")
def head_root():
    return Response()

@router.head("/expenses")
def head_expenses():
    return Response()

@router.get("/healthz")
def healthz():
    return {"ok": True}

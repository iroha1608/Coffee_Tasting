from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Roaster, Coffee, Taster, PREFECTURES, MAX_COFFEES

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/roaster/add")
async def show_roaster_form(request: Request):
    return templates.TemplateResponse(
        request,
        "roaster_add.html",
        {
            "prefectures": PREFECTURES,
        },
    )


@app.post("/roaster/add")
async def handle_roaster(
    request: Request,
    company_name: str = Form(),
    company_name_kana: str = Form(),
    contact_person: str = Form(),
    address: str = Form(),
    phone: str = Form(),
    email: str = Form(),
    prefecture: str = Form(),
    db: Session = Depends(get_db),
):
    if db.query(Roaster).filter(Roaster.email == email).first():
        return templates.TemplateResponse(
            request,
            "roaster_add.html",
            {
                "prefectures": PREFECTURES,
                "error": "このメールアドレスはすでに登録されています。",
                "values": {
                    "company_name": company_name,
                    "company_name_kana": company_name_kana,
                    "contact_person": contact_person,
                    "address": address,
                    "phone": phone,
                    "email": email,
                    "prefecture": prefecture,
                },
            },
        )

    roaster = Roaster(
        company_name=company_name,
        company_name_kana=company_name_kana,
        contact_person=contact_person,
        address=address,
        phone=phone,
        email=email,
        prefecture=prefecture,
        access_hash=Roaster.new_hash(),
    )
    db.add(roaster)
    db.commit()
    db.refresh(roaster)

    return RedirectResponse(url=f"/roaster/{roaster.access_hash}", status_code=303)


@app.get("/roaster/login")
async def show_roaster_login_form(request: Request):
    return templates.TemplateResponse(request, "roaster_login.html", {})


@app.post("/roaster/login")
async def handle_roaster_login(
    request: Request,
    email: str = Form(),
    db: Session = Depends(get_db),
):
    roaster = db.query(Roaster).filter(Roaster.email == email).first()
    if not roaster:
        return templates.TemplateResponse(
            request,
            "roaster_login.html",
            {
                "error": "このメールアドレスは登録されていません。",
            },
        )

    return RedirectResponse(url=f"/roaster/{roaster.access_hash}", status_code=303)


@app.get("/roaster/{access_hash}")
async def show_roaster_page(
    request: Request,
    access_hash: str,
    db: Session = Depends(get_db),
):
    roaster = db.query(Roaster).filter(Roaster.access_hash == access_hash).first()
    if not roaster:
        raise HTTPException(status_code=404, detail="ページが見つかりません")

    return templates.TemplateResponse(
        request,
        "roaster_page.html",
        {
            "roaster": roaster,
            "coffees": roaster.coffees,
            "max_coffees": MAX_COFFEES,
        },
    )


@app.post("/roaster/{access_hash}/coffee/add")
async def add_coffee(
    request: Request,
    access_hash: str,
    name: str = Form(),
    db: Session = Depends(get_db),
):
    roaster = db.query(Roaster).filter(Roaster.access_hash == access_hash).first()
    if not roaster:
        raise HTTPException(status_code=404, detail="ページが見つかりません")

    if len(roaster.coffees) >= MAX_COFFEES:
        return templates.TemplateResponse(
            request,
            "roaster_page.html",
            {
                "roaster": roaster,
                "coffees": roaster.coffees,
                "max_coffees": MAX_COFFEES,
                "error": f"出品コーヒーの登録は最大{MAX_COFFEES}件です。",
            },
        )

    db.add(Coffee(roaster_id=roaster.id, name=name))
    db.commit()
    db.refresh(roaster)

    return RedirectResponse(url=f"/roaster/{access_hash}", status_code=303)


@app.get("/taster/add")
async def show_taster_form(request: Request):
    return templates.TemplateResponse(
        request,
        "taster_add.html",
        {
            "prefectures": PREFECTURES,
        },
    )


@app.post("/taster/add")
async def handle_taster(
    request: Request,
    name: str = Form(),
    name_kana: str = Form(),
    prefecture: str = Form(),
    address: str = Form(),
    phone: str = Form(),
    email: str = Form(),
    company_name: str = Form(),
    db: Session = Depends(get_db),
):

    if db.query(Taster).filter(Taster.email == email).first():
        return templates.TemplateResponse(
            request,
            "taster_add.html",
            {
                "prefectures": PREFECTURES,
                "error": "このメールアドレスはすでに登録されています。",
                "values": {
                    "name": name,
                    "name_kana": name_kana,
                    "prefecture": prefecture,
                    "address": address,
                    "phone": phone,
                    "email": email,
                    "company_name": company_name,
                },
            },
        )

    taster = Taster(
        name=name,
        name_kana=name_kana,
        prefecture=prefecture,
        address=address,
        phone=phone,
        email=email,
        company_name=company_name,
        access_hash=Roaster.new_hash(),
    )
    db.add(taster)
    db.commit()
    db.refresh(taster)

    return RedirectResponse(url=f"/taster/{taster.access_hash}", status_code=303)


@app.get("/taster/login")
async def show_taster_login_form(request: Request):
    return templates.TemplateResponse(request, "taster_login.html", {})


@app.post("/taster/login")
async def handle_taster_login(
    request: Request,
    email: str = Form(),
    db: Session = Depends(get_db),
):
    taster = db.query(Taster).filter(Taster.email == email).first()
    if not taster:
        return templates.TemplateResponse(
            request,
            "taster_login.html",
            {
                "error": "このメールアドレスは登録されていません。",
            },
        )

    return RedirectResponse(url=f"/taster/{taster.access_hash}", status_code=303)


@app.get("/taster/{access_hash}")
async def show_taster_page(
    request: Request,
    access_hash: str,
    db: Session = Depends(get_db),
):
    taster = db.query(Taster).filter(Taster.access_hash == access_hash).first()
    if not taster:
        raise HTTPException(status_code=404, detail="ページが見つかりません")

    return templates.TemplateResponse(
        request,
        "taster_page.html",
        {
            "taster": taster,
        },
    )
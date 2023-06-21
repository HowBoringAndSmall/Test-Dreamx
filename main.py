
from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


from database import connection

from library import create_user, select_all_grants, search_fonds, select_all_fonds, get_fond_by_id, get_grant_by_id, \
    search_grants

app = FastAPI()


app.mount("/static", StaticFiles(directory="templates/static"))
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")


@app.get("/", response_class=HTMLResponse)
async def main():
    with open("./templates/main/main.html", "r") as file:
        content = file.read()
    return content


@app.get("/registration", response_class=HTMLResponse)
async def main():
    with open("./templates/registration/registration.html", "r") as file:
        content = file.read()
    return content


@app.post("/register")
async def register_user(
        name: str = 'Бриса',
        surname: str = 'Брисович',
        birthday: str = '2023-06-09',
        email: str = Form(...),
        phone: str = '123',
        password: str = Form(...)
        ):
    try:
        await create_user(name, surname, birthday, email, phone, password)
        response = RedirectResponse(url="/pre_reg", status_code=307)
        return response
    except Exception as e:
        connection.rollback()
        return JSONResponse(content={"error": str(e)})


@app.post("/forgot_password/send_email")
async def send_email(email=Form()):
    try:
        with connection.cursor() as cursor:
            # Создание нового пользователя в базе данных
            sql_password = "SELECT password FROM user WHERE email=%s"
            cursor.execute(sql_password, email)

            user = {'email': email, 'password': sql_password}
            return JSONResponse(content=user)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})


@app.post("/pre_reg", response_class=HTMLResponse)
def registration_successfully(request: Request):
    return templates.TemplateResponse("pre_reg/pre_reg.html", {"request": request})


@app.get("/home_page", response_class=HTMLResponse)
def home_template(request: Request):
    return templates.TemplateResponse("home_page/home_page.html", {"request": request})


@app.get("/forgot_password", response_class=HTMLResponse)
async def main():
    with open("./templates/forgot_password/forgot_password.html", "r") as file:
        content = file.read()
    return content


@app.get("/home/fonds", response_class=HTMLResponse)
async def show_fonds(request: Request):
    filters = {
        "title": request.query_params.get("title"),
        "type": request.query_params.get("type")
    }
    fonds = select_all_fonds()
    if filters["title"] or filters["type"]:
        fonds = search_fonds(filters["title"], filters["type"])
    return templates.TemplateResponse("fonds/fonds.html", {"request": request, "fonds": fonds, "filters": filters})


@app.get("/home/fonds/results", response_class=HTMLResponse)
async def show_filtered_fonds(request: Request):
    filters = {
        "title": request.query_params.get("title"),
        "type": request.query_params.get("type")
    }
    fonds = search_fonds(filters["title"], filters["type"])
    return templates.TemplateResponse("fonds/fonds.html", {"request": request, "fonds": fonds, "filters": filters})


@app.get("/home/fond/{fond_id}", response_class=HTMLResponse)
async def show_fond(request: Request, fond_id: int):
    # Здесь вы можете получить информацию о фонде с помощью идентификатора `fond_id`
    fond = get_fond_by_id(fond_id)
    if fond is None:
        # Если фонд не найден, вы можете вернуть ошибку или перенаправить на другую страницу
        return templates.TemplateResponse("error.html", {"request": request})
    return templates.TemplateResponse("fonds/fonds.html", {"request": request, "fond": fond})


# Логика грантов
@app.get("/home/grants", response_class=HTMLResponse)
async def show_grants(request: Request):
    filters = {
        "direction": request.query_params.get("direction"),
        "status": request.query_params.get("status"),
        "foundation": request.query_params.get("foundation")
    }
    grants = select_all_grants()
    if filters["direction"] or filters["status"] or filters["foundation"]:
        fonds = search_fonds(filters["title"], filters["type"])
    return templates.TemplateResponse("grants/grants.html", {"request": request, "grants": grants, "filters": filters})


@app.get("/home/grants/results", response_class=HTMLResponse)
async def show_filtered_fonds(request: Request):
    filters = {
        "direction": request.query_params.get("direction"),
        "status": request.query_params.get("status"),
        "foundation": request.query_params.get("foundation")
    }
    grants = search_grants(filters["direction"], filters["status"], filters["foundation"])
    return templates.TemplateResponse("grants/grants.html", {"request": request, "grants": grants, "filters": filters})


@app.get("/home/grant/{grant_id}", response_class=HTMLResponse)
async def show_grant(request: Request, grant_id: int):
    grant = get_grant_by_id(grant_id)
    if grant is None:
        return templates.TemplateResponse("error.html", {"request": request})
    return templates.TemplateResponse("grants/grants.html", {"request": request, "grant": grant})






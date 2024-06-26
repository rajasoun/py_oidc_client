#!/usr/bin/env python3
import json

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from loguru import logger

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")
config = Config(".env")
oauth = OAuth(config)

oidc_provider_conf_url = config('provider_url') + \
                         '/.well-known/openid-configuration'

oauth.register(
    name='oidc',
    server_metadata_url=oidc_provider_conf_url,
    client_id=config('client_id'),
    client_secret=config('client_secret'),
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# # add a custom header X-Process-Time containing the time in seconds that it took to process the request and
# generate a response
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def read_users_file(filename='users.txt'):
    with open(filename, 'r') as file:
        users = file.read().splitlines()
    return users

def is_user_authorized(user, users):
    return user['email'] in users

def generate_html_response(content, link_text, link_href):
    return HTMLResponse(f'<h1>{content}</h1><a href="{link_href}">{link_text}</a>')

def process_authorized_user(user):
    user_data = json.dumps(user)
    html_content = f'<pre>{user_data}</pre><a href="/logout">logout</a>'
    return HTMLResponse(html_content)

@app.route('/')
async def homepage(request):
    user = request.session.get('user')
    if not user:
        return generate_html_response('Please login to continue', 'login', '/login')

    users = read_users_file()
    if not is_user_authorized(user, users):
        return generate_html_response('Unauthorized', 'login', '/login')
    
    # Process authorized user
    return process_authorized_user(user)

@app.route('/login')
async def login(request):
    redirect_uri = request.url_for('auth')
    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@app.route('/callback')
async def auth(request):
    try:
        token = await oauth.oidc.authorize_access_token(request)
        logger.info("Successfully authenticated")
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        logger.info(f"User: {user} added to session")
    return RedirectResponse(url='/')


@app.route('/logout')
async def logout(request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@app.get("/health")
def ping():
    return {"status": "ok"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=3000)

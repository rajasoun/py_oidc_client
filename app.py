import json
from starlette.config import Config
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth

app = Starlette(debug=True)
app.add_middleware(SessionMiddleware, secret_key="!secret")

config = Config(".env")
oauth = OAuth(config)


# "https://cloudsso-test.cisco.com/.well-known/openid-configuration"

oidc_provider_conf_url = config('provider_url')+'/.well-known/openid-configuration'

oauth.register(
    name='oidc',
    server_metadata_url=oidc_provider_conf_url ,
    client_id=config('client_id'),
    client_secret=config('client_secret'),
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.route('/')
async def homepage(request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.route('/login')
async def login(request):
    redirect_uri = request.url_for('auth')
    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@app.route('/callback')
async def auth(request):
    token = await oauth.oidc.authorize_access_token(request)
    user = await oauth.oidc.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.route('/logout')
async def logout(request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3000)

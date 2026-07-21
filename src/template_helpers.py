from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from src import APP_VERSION


templates = Environment(loader=FileSystemLoader('src/templates'), autoescape=True)


def _url_for(endpoint, **kwargs):
    if endpoint == 'static':
        return '/static/' + kwargs.get('filename', '') + '?v=' + APP_VERSION
    return '/'


templates.globals['url_for'] = _url_for
templates.globals['app_version'] = APP_VERSION


class _AnonymousUser:
    is_authenticated = False
    settings = {}
    name = ''


_ANONYMOUS = _AnonymousUser()


def _render(name, current_user=None, **kwargs):
    user = current_user if current_user is not None else _ANONYMOUS
    return templates.get_template(name).render(current_user=user, **kwargs)


def _require_dashboard_user(current_user):
    if current_user is None:
        return RedirectResponse(url='/auth/login', status_code=302)
    return current_user


def _render_or_redirect(name, current_user, active_page, **kwargs):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render(name, current_user=current_user, active_page=active_page, **kwargs))

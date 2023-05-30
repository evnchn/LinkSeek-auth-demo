#!/usr/bin/env python3
'''This is only a very simple authentication example which stores session IDs in memory and does not do any password hashing.

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a real authentication system.

Here we just demonstrate the NiceGUI integration.
'''

question_list = '''1. Are you a self-starter?
2. Do you work well independently?
3. Do you prefer working on a team or individually?
4. Are you detail-oriented?
5. Do you enjoy working with numbers?
6. Do you consider yourself creative?
7. Are you comfortable taking risks?
8. Are you comfortable with ambiguity?
9. Do you enjoy problem-solving?
10. Are you comfortable with public speaking?
11. Do you enjoy working with people?
12. Do you prefer working with machines?
13. Are you comfortable with technology?
14. Are you comfortable with a fast-paced work environment?
15. Do you enjoy multitasking?
16. Do you enjoy working in a structured environment?
17. Do you enjoy working in a flexible environment?
18. Are you comfortable with change?
19. Do you have strong communication skills?
20. Are you comfortable with conflict?
21. Do you enjoy learning new things?
22. Are you comfortable with feedback?
23. Do you enjoy research?
24. Do you enjoy writing?
25. Do you enjoy teaching?
26. Are you comfortable with sales?
27. Do you enjoy working with your hands?
28. Are you comfortable with repetitive tasks?
29. Do you enjoy working in a leadership role?
30. Are you comfortable with a customer-facing role?
31. Do you enjoy working in a service-oriented role?
32. Are you comfortable with administrative tasks?
33. Are you comfortable with data entry?
34. Do youenjoy problem-solving?
35. Are you comfortable with deadlines?
36. Are you comfortable with a high-pressure work environment?
37. Do you enjoy working in a creative field?
38. Are you comfortable working with confidential information?
39. Do you enjoy working with people from diverse backgrounds?
40. Are you comfortable with traveling for work?
41. Do you enjoy working in a fast-paced environment?
42. Are you comfortable with a physically demanding job?
43. Do you enjoy working in a customer service role?
44. Are you comfortable working with children?
45. Do you enjoy working in a healthcare-related field?
46. Are you comfortable with a job that involves a lot of driving?
47. Do you enjoy working in a sales-related field?
48. Are you comfortable with a job that involves a lot of standing?
49. Do you enjoy working in a team-oriented environment?
50. Are you comfortable with a job that involves long hours?'''.split("\n")[:5]

import json

def save_users():
    global users
    with open('users.json', 'w') as f:
        json.dump(users, f)

def load_users():
    global users
    with open('users.json', 'r') as f:
        users = json.load(f)

def save_user_personalities():
    global user_personalities
    with open('user_personalities.json', 'w') as f:
        json.dump(user_personalities, f)

def load_user_personalities():
    global user_personalities
    try:
        with open('user_personalities.json', 'r') as f:
            user_personalities = json.load(f)
    except:
        user_personalities = {}

import uuid
from typing import Dict

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from nicegui import app, ui

app.add_middleware(SessionMiddleware, secret_key='some_random_string')  # use your own secret key here

# in reality users and session_info would be persistent (e.g. database, file, ...) and passwords obviously hashed
# users = [('user1', 'pass1'), ('user2', 'pass2')]
load_users()
load_user_personalities()
save_user_personalities()

session_info: Dict[str, Dict] = {}


def is_authenticated(request: Request) -> bool:
    return session_info.get(request.session.get('id'), {}).get('authenticated', False)


"""@ui.page('/personality_test')
def personality_test(request: Request) -> None:
    if not is_authenticated(request):
        return RedirectResponse('/login')
    session = session_info[request.session['id']]
    with ui.column().classes('absolute-center items-center'):
        ui.label(f'Personality test').classes('text-2xl')
        for question in question_list:
            with ui.dialog() as dialog, ui.card():
                ui.label(question)
                with ui.row():
                    ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
                    ui.button('No', on_click=lambda: dialog.submit('No'))

            async def show():
                result = await dialog
        # NOTE we navigate to a new page here to be able to modify the session cookie (it is only editable while a request is en-route)
        # see https://github.com/zauberzeug/nicegui/issues/527 for more details
        ui.button('', on_click=lambda: ui.open('/logout')).props('outline round icon=logout')
        ui.button('Perform personality test', on_click=lambda: ui.open('/personality_test'))"""

    

@ui.page('/')
def main_page(request: Request) -> None:
    if not is_authenticated(request):
        return RedirectResponse('/login')
    session = session_info[request.session['id']]


    async def personality_test():
        res_string = ""
        for question in question_list:
            with ui.dialog() as dialog, ui.card():
                ui.label(question)
                with ui.row().classes('items-center'):
                    ui.button('Yes', on_click=lambda: dialog.submit('Y'))
                    ui.button('No', on_click=lambda: dialog.submit('N'))
            result = await dialog
            res_string += result
        ui.notify(f'You chose {res_string}')
        user_personalities[session["username"]] = res_string
        save_user_personalities()
        ui.open('/')

    with ui.dialog() as dialog_document, ui.card():
        ui.label('Please send the document with your LinkSeek username to admin@linkseek.com:')
        ui.label('CV and portfolios would help potentil employers identify you.')
        ui.button('Close', on_click=dialog_document.close)

    with ui.column().classes('absolute-center items-center'):
        ui.label(f'Hello {session["username"]}!').classes('text-2xl')
        if session["username"] in user_personalities.keys():
            ui.label(f'Your personality: {user_personalities[session["username"]]}!')
        else:
            ui.label("Please take a personality test for job-matching!")
        # NOTE we navigate to a new page here to be able to modify the session cookie (it is only editable while a request is en-route)
        # see https://github.com/zauberzeug/nicegui/issues/527 for more details
        ui.button('', on_click=lambda: ui.open('/logout')).props('outline round icon=logout')
        ui.button('Perform personality test', on_click=personality_test)
        ui.button('Upload documents', on_click=dialog_document.open)



@ui.page('/login')
def login(request: Request) -> None:
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        if [username.value, password.value] in users:
            session_info[request.session['id']] = {'username': username.value, 'authenticated': True}
            ui.open('/')
        else:
            ui.notify('Wrong username or password', color='negative')
    if is_authenticated(request):
        return RedirectResponse('/')
    request.session['id'] = str(uuid.uuid4())  # NOTE this stores a new session ID in the cookie of the client
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password').props('type=password').on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
        ui.button('Sign up', on_click=lambda: ui.open('/new_account'))

@ui.page('/new_account')
def new_account(request: Request) -> None:
    def create_acc() -> None:  # local function to avoid passing username and password as arguments
        if username.value in (x[0] for x in users):
            ui.notify('User already exists!', color='negative')
        elif not username.value or not password.value:
            ui.notify('Fill in username and password', color='negative')
        else:
            print("CREATE ACCOUNT")
            users.append([username.value, password.value])
            save_users()
            ui.open('/login')
    if is_authenticated(request):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', create_acc)
        password = ui.input('Password').props('type=password').on('keydown.enter', create_acc)
        ui.button('Create new account', on_click=create_acc)
        ui.button('Go back', on_click=lambda: ui.open('/'))


@ui.page('/logout')
def logout(request: Request) -> None:
    if is_authenticated(request):
        session_info.pop(request.session['id'])
        request.session['id'] = None
        return RedirectResponse('/login')
    return RedirectResponse('/')


ui.run()

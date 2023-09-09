from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from drf_yasg import openapi
from rest_framework.parsers import JSONParser
import json
import sqlite3
import smtplib

from config_reader import config


class MyView(viewsets.ViewSet):

    user_from = config.USER_FROM.get_secret_value()
    password_key = config.PASSWORD.get_secret_value()
    user_to = config.USER_TO.get_secret_value()

    @csrf_exempt
    @swagger_auto_schema(
            method='post',
            tags=['https://prosto-web.agency/django_prosto/send_form/'],
            operation_id = 'Отправка заявки',
            operation_description = '...',
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'tnumber', 'content'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'tnumber': openapi.Schema(type=openapi.TYPE_STRING),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            responses={
                200: openapi.Response(
                    description='Успешная отправка',
                    examples={
                        'application/json': {
                            'status': 'success',
                            'content': 'Success sending'
                        }
                    }
                ),
                201: openapi.Response(
                    description='Успешно, проблема с smtp',
                    examples={
                        'application/json': {
                            'status': 'success',
                            'content': 'Error with mail'
                        }
                    }
                ),
                400: openapi.Response(
                    description='Некорректные данные запроса',
                    examples={
                        'application/json': {
                            'status': 'error',
                            'content': 'Invalid data'
                        }
                    }
                ),
                405: openapi.Response(
                    description='Метод не разрешен',
                    examples={
                        'application/json': {
                            'status': 'error',
                            'content': 'Invalid method'
                        }
                    }
                ),
                520: openapi.Response(
                    description='Ошибка с базой данных',
                    examples={
                        'application/json': {
                            'status': 'error',
                            'content': 'Error with database'
                        }
                    }
                ),
            }
        )
    @api_view(['POST'])
    @parser_classes([JSONParser])
    def send_form(request):
        if request.method == 'POST':
            try:
                request_data = json.loads(request.body)
                name = request_data.get('name')
                tnumber = request_data.get('tnumber')
                content = request_data.get('content')
            except Exception:
                return Response(data = {'status': 'error', 'content': 'Invalid data'}, status=400)
            try:
                db = sqlite3.connect('/root/tg_bots/prosto_telegram/database/main.db')
                cur = db.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, tnumber TEXT, content TEXT, status TEXT);""")
                db.commit()
                new_request = (name, tnumber, content, 'new')
                cur.execute("INSERT INTO requests (name, tnumber, content, status) VALUES(?, ?, ?, ?);", new_request)
                db.commit()
            except Exception:
                return Response(data = {'status': 'error', 'content': 'Error with database'}, status=520)
            try:
                pass
                letter = 'From: ...\n' + 'To: ...\n' + 'Subject: Новая заявка\n' + \
                    'Content-Type: text/plain; charset="UTF-8";\n' + f'Имя: {name}\nНомер телефона: {tnumber}\nОписание: {content}'
                letter = letter.encode("UTF-8")
                server = smtplib.SMTP_SSL('smtp.gmail.com:587')
                server.login(user_from, password_key)
                server.sendmail(user_from, user_to, letter)
                server.quit()
            except Exception:
                return Response(data = {'status': 'not all', 'content': 'Error with mail'}, status=201)
            return Response(data = {'status': 'success', 'content': 'Success sending'}, status=200)
        else:
            return Response(data = {'status': 'error', 'content': 'Invalid method'}, status=405)

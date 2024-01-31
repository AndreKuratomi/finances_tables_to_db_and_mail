import os
import requests
import time

from django.conf import settings
from django.core.mail import EmailMessage, mail_admins, send_mail
from django.template.loader import render_to_string

from dotenv import load_dotenv

from pathlib import Path

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tqdm import tqdm

from filter_tables.models import TableName

from robot_sharepoint.modules.robot_for_login_and_download_from_sharepoint import robot_for_sharepoint
from robot_sharepoint.modules.recursive_robot import recursive_robot

# from management_before_django.robot_sharepoint.robot_for_outlook_exchangelib import func_for_search

# # While there's no model:
# model_dir = './models.py'
# count = 1
# do_we_have_tablename = False

# while not do_we_have_tablename:
#     try:
#         from .models import TableName
#         do_we_have_tablename = True
#     except ImportError:
#         print(count)
#         time.sleep(count)
#         count += 1
#     # module = __import__('models', fromlist=[''])
#     # do_we_have_tablename = hasattr(module, 'TableName')
    
# from .serializers import EmailSerializer

import ipdb

load_dotenv()

# ENVS:
# Keys for login:
username = os.getenv("USERN")
password = os.getenv("PASSWORD")

# Input ids:
hover_selector = os.getenv("HOVER_SELECTOR")
download_selector = os.getenv("DOWNLOAD_SELECTOR")

# Sharepoint URL:
sharepoint_url = os.getenv("SHAREPOINT_URL")

# Download directory:
download_directory = os.getenv("DOWNLOAD_DIRECTORY")


# Table to work with:


table_data = TableName.objects.all()
# ipdb.set_trace()

class EmailAttachByTable(APIView):
    def post(self):
        try:
            counter = 0
            for row in tqdm(table_data, "Each line, each search and email:"):
                print(row)
                if counter == 0:
                    counter += 1
                    continue
                else:
                    cnpj = row.cnpj
                    nfe = row.numero
                    razao_social = row.nome_do_cliente
                    valor_liquido = row.valor_liquido

                    row_data = {"cnpj": cnpj, "nfe": nfe, "razao_social": razao_social, "valor_liquido": valor_liquido}

                    # TAKING INPUT IDS WITH SELENIUM ROBOT:
                    input_ids = recursive_robot(username, sharepoint_url)
                    print(input_ids)
                    
                    # # PLACING TABLE TO WORK WITH WITH SELENIUM ROBOT:
                    robot_for_sharepoint(username, password, input_ids["user_input_id"], input_ids["password_input_id"], sharepoint_url, download_directory, "02390435000115", "17779")
                    # robot_for_sharepoint(username, password, input_ids["user_input_id"], input_ids["password_input_id"], sharepoint_url, download_directory, row_data["cnpj"], row_data["nfe"])
                    ipdb.set_trace()

                    # response = requests.post("<my_powerautomate_http_endpoint>", json=row_data)

                    # if response.status_code == 200:
                    #     print("Flow working!")
                    # else:
                    #     print(f"Error! Status code {response.status_code}")
                    # counter += 1


                    # print("Email successfully sent! Check inbox.")

            return Response({"message": "Email successfully sent"}, status=status.HTTP_200_OK)
  
        except:
            return Exception({"error": "Something went wrong! Contact the dev!"})

class SendEmailView(APIView):
    def post(self):
        try: 
            # USERNAME AND EMAIL TO WORK WITH:
            data={'receiver_name': "Andre", 'receiver_email': "andrekuratomi@gmail.com"}
            
            # serializer = EmailSerializer(data)
            # # print(serializer)
            # if not serializer.is_valid():
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Creating table from model:
            table_html = "<table>"
            table_html += "<tr>"
            
            # <TH>s:
            for field1 in tqdm(TableName._meta.fields, "Filtering table from dataframe..."):
                # print(field1.verbose_name)

                if field1.verbose_name == 'index':
                    # print(field1)
                    continue
                elif field1.verbose_name == 'id':
                    # print(field1.verbose_name)
                    continue
                else:
                    # field_value = getattr
                    table_html += "<th>{}</th>".format(str(field1.verbose_name).upper())
            table_html += "</tr>"
            
            # <TD>s:
            for instance in tqdm(table_data, "Creating table for email body..."):
                table_html += "<tr>"
                counter = 0
                for field2 in instance._meta.fields:
                    # Excluding column 'index' content:
                    if counter == 0 or counter % 16 == 0:
                        counter += 1
                        continue
                    # Excluding column 'ID' content:
                    elif counter == 1 or counter % 17 == 0:
                        counter += 1
                        continue
                    # Ordering datetime from 'year-month-day' to 'day-month-year':
                    elif counter == 10 or counter == 11 or counter % 26 == 0 or counter % 27 == 0:
                        field_value = getattr(instance, field2.name)
                        if field_value == None:
                            # print(field_value)
                            field_value = '-'
                            table_html += "<td style='text-align: center;'>{}</td>".format(field_value)
                            counter += 1
                        else:
                            field_value = getattr(instance, field2.name).strftime('%d-%m-%Y %H:%M:%S')
                            table_html += "<td style='text-align: center;'>{}</td>".format(field_value)
                            counter += 1
                    else:
                        table_html += "<td style='text-align: center;'>{}</td>".format(getattr(instance, field2.name))
                        counter += 1
                table_html += "</tr>"
            
            table_html += "</table>"
            # Insert table to mail body:
            table_to_mail = render_to_string('table_template.html', {'receiver_name': data['receiver_name'], 'table_data': table_html}
                                            #  , using='ISO-8859-1'
                                            )
            # print(table_to_mail)
            time.sleep(2)  # wait for file to be created

            send_mail(
                "Envio tabela  {a1} - Novelis".format(a1=data['receiver_name']),
                "",
                "{}".format(host_email), 
                [data['receiver_email']], 
                fail_silently=False,
                html_message=table_to_mail
            )
            
            # ipdb.set_trace()

            print("Email successfully sent! Check inbox.")

            return Response({"message": "Email successfully sent"}, status=status.HTTP_200_OK)
        
        except:
            return Exception({"error": "Something went wrong! Contact the dev!"})

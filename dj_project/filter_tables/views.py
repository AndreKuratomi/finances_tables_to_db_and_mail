import time

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from pathlib import Path

from rest_framework.views import APIView

from tqdm import tqdm

from filter_tables.models import TableName

from management_before_django.table_managements.modules.status_update import status_update
from robot_sharepoint.modules.robots.robot_for_login_and_download_from_sharepoint import robot_for_sharepoint
from robot_sharepoint.modules.robot_utils.join_reports import join_reports

from utils.functions.delete_elements import do_we_have_things_to_delete
from utils.variables.envs import username, password, sharepoint_medicoes_url, download_directory, host_email
from utils.variables.paths import edited_tables_path, raw_tables_path, reports_path
from utils.variables.report_files import not_found_list, sent_list, not_found_title, sent_title

import ipdb

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

# Table to work with:
table_data = TableName.objects.all()

print("Views:", __name__)


class EmailAttachByTable(APIView):
    def post(self, root_dir: str):
        print(f"root_dir: {root_dir}")
        try:

            # Not found list report creation:
            with reports_path.joinpath(not_found_list).open("w") as file:
                file.write(not_found_title)

            for row in tqdm(table_data, "Each line, each search and email"):

                cnpj = row.cnpj
                nfe = row.numero
                nome_do_cliente = row.nome_do_cliente
                status = row.status
                valor_liquido = row.valor_liquido
                vencimento = row.dt_vencto

                if status == "Não enviado":

                    row_data = {
                        "cnpj": cnpj, 
                        "nfe": nfe, 
                        "nome_do_cliente": nome_do_cliente, 
                        "valor_liquido": valor_liquido, 
                        "vencimento": vencimento, 
                        # "contact": contato,
                        # "competencia_por_ano": "competencia_por_ano",
                        "contact": "andrekuratomi@gmail.com"
                    }

                    # PLACING TABLE TO WORK WITH WITH SELENIUM ROBOT:
                    robot_for_sharepoint(
                        username,
                        password,
                        sharepoint_medicoes_url,
                        download_directory,
                        cnpj,
                        nfe,
                        # "11068167000453", # boleto
                        # "17774" # boleto
                        # "02390435000115",
                        # "17779"
                        # "61102778000872", # not_found
                        # "17757" # not_found
                    )

                    attachments_path = "/robot_sharepoint/attachments/"
                    full_attachments_path = root_dir + attachments_path

                    # Extract info from attachments:
                    path = Path(full_attachments_path)
                    tables_path_content = list(path.iterdir())

                    competencia_por_ano = "02/01/2024"
                    tipo_de_servico = ""
                    table_template = "table_template_deposito.html"
                    
                    # NOT FOUND CNPJ AND/OR NFE:
                    if len(tables_path_content) <= 1:
                        
                        # Fill element not found list:
                        not_found_elem = f"CNPJ: {cnpj} and/or NFE {nfe}. \n"
                        with reports_path.joinpath(not_found_list).open("a") as file:
                            file.write(not_found_elem)

                    else:
                        for file in tables_path_content:
                            print("Attachments:",file)
                            if file.is_file():
                                string_file = str(file)

                                if string_file.endswith('.pdf') or string_file.endswith('.xlsx'):
                                    prefix = full_attachments_path
                                    filtered = string_file[len(prefix):]

                                    if filtered.startswith("NFE"):

                                        specific_char_1 = "."
                                        specific_char_2 = " "

                                        tipo_de_servico = ""
                                        for charac in filtered[10:]:
                                            if charac == specific_char_1 or charac == specific_char_2:
                                                break
                                            else:
                                                tipo_de_servico += charac

                                    elif filtered.startswith("BOLETO"):
                                        table_template = "table_template_boleto.html"
                            
                            else:
                                print("Error! Verify the file.")

                        print("competencia_por_ano:", competencia_por_ano)
                        print("nome_do_cliente_data:", row_data['nome_do_cliente'])
                        print("table_template:", table_template)
                        print("tipo_de_servico:", tipo_de_servico)

                        # Insert table to mail body:
                        mail_content = render_to_string(
                            table_template, {
                                'competencia_por_ano': competencia_por_ano, 
                                'contact': row_data['contact'], 
                                'nfe': row_data['nfe'], 
                                'nome_do_cliente':  row_data['nome_do_cliente'],
                                'tipo_de_servico': tipo_de_servico,
                                'valor_liquido': row_data['valor_liquido'],
                                'vencimento': row_data['vencimento']
                            }
                        )

                        time.sleep(2)  # wait for file to be created

                        email = EmailMessage(
                            "Nota Fiscal Eletrônica - J&C Faturamento - {a1}  {a2}  ( {a3} )  NF -  -  - {a4}"
                            .format(
                                a1=tipo_de_servico, 
                                a2=competencia_por_ano,
                                a3=row_data['nome_do_cliente'], 
                                # a4='17774'
                                a4=row_data['nfe']
                            ),
                            mail_content,
                            "{}".format(host_email), 
                            [row_data['contact']],
                        )
                        
                        # Reading HTML tags:
                        email.content_subtype = 'html'

                        # Attach files to email:
                        for file in tables_path_content:
                            print(file)
                            stringfy = str(file)
                            if stringfy.endswith('.pdf') or stringfy.endswith('.xlsx'):
                                email.attach_file(file)

                        email.send()
                        print("Email successfully sent! Check inbox.")
                        
                        # Fill element sent list:
                        sent_elem = f"CNPJ: {cnpj} and/or NFE {nfe}. \n"
                        with reports_path.joinpath(sent_list).open("a") as file:
                            file.write(sent_elem)

                        # STATUS UPDATE:
                        status_update(edited_tables_path, row_data)

                else:
                    continue

            # Delete no more necessary raw table 
            do_we_have_things_to_delete(raw_tables_path, '.xlsx')

            print("Application finished its process succesfully!")

            # ONLY FIRST DAY OF THE MONTH!
            # Raw reports creation for new database spreadsheet:
            with reports_path.joinpath(sent_list).open("w") as file:
                file.write(sent_title)

        except Exception as e:
            print(f"error:Something went wrong: {e} ! Contact the dev!")

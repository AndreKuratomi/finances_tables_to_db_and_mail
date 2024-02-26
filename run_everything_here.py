import os
import sys

import django
import ipdb


# Preparing django to run outside its dir:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novelis_table_filter_mail_project.settings')
sys.path.append("./dj_project")
django.setup()

from dj_project.filter_tables.views import EmailAttachByTable

from management_before_django.table_managements.scripts import tables_to_db

from robot_sharepoint.modules.robot_to_upload_files import upload_files_to_sharepoint
from robot_sharepoint.modules.robot_for_login_and_download_raw_table import robot_for_raw_table
from robot_sharepoint.modules.download_directories_management import check_if_dir_is_empty_or_not

from utils.envs import download_directory, username_test, password_test, raw_table_directory, sharepoint_for_upload_url
from utils.paths import reports_path

root_directory = os.path.dirname(os.path.abspath(__file__))
root_directory = str(root_directory)
print(f"root_directory: {root_directory}")
# ipdb.set_trace()

tables_to_db.tables_to_db()

do_we_have_table_to_work_with = check_if_dir_is_empty_or_not(raw_table_directory)

if not do_we_have_table_to_work_with:
    print("Coming soon...")
    # robot_for_raw_table(download_directory, username_test, password_test, sharepoint_for_upload_url)
    
    # # Raw reports creation:
    # with reports_path.joinpath(final_not_found_list).open("w") as file:
    # file.write(not_found_list)
    
    # # ipdb.set_trace()
    # with reports_path.joinpath(final_sent_list).open("w") as file:
    #     file.write(sent_list)
else:
    try:
        EmailAttachByTable().post(root_directory)
    except Exception as e: 
        print(f"PROCESSO INTERROMPIDO! Error: {e} CONTATAR DEV RESPONSÁVEL \n Mas pode continuar.")
    finally: 
        upload_files_to_sharepoint(username_test, password_test, reports_path, sharepoint_for_upload_url)
    
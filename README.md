# finances_table_to_db_and_mail

- [Translations](#translations)
- [About](#About)
- [A brief description](#a-brief-description)
- [A detailed description](#a-detailed-description)
- [Application's behaviour by case](#application's-behaviour-by-case)
- [Instalation](#instalation)
- [Commands](#Commands)
- [References](#references)

<br>

## Translations

- [English](https://github.com/AndreKuratomi/finances_tables_to_db_and_mail)
- [Português Brasileiro / Brazilian portuguese](/.multilingual_readmes/README.pt-br.md)

<br>

## About

<p>The application <b>finances_table_to_db_and_mail</b> was developed to automatise monthly email sent of invoices and bills to a company clients. It works with the company <strong>sharepoint</strong>'s folders, emails elaboration with files attachment and reports elaboration of succesfull and non-successfull cases. This application is made to non-developers operate it and can be used once a month or more according to the demand. It is only runned manually for this version.

This application uses <strong>[Python](https://www.python.org/downloads/)</strong>'s framework <strong>[Django](https://www.djangoproject.com/)</strong>, the libs <strong>[OpenPyXl](https://openpyxl.readthedocs.io/en/stable/tutorial.html)</strong>, <strong>[Pandas](https://pandas.pydata.org/docs/)</strong> and <strong>[Selenium](https://pypi.org/project/selenium/)</strong>, the <strong>[SQLite3](https://docs.python.org/3/library/sqlite3.html)</strong> database and a windows .bat file that runs the whole application.

<br>

## A brief description

Everyone may operate this application, but its configuration may be done only after reading - [A detailed description](#a-detailed-description). 

This application is manually started by clicking twice the <strong>.bat</strong> file 'script_for_bat_file.bat' that can be placed anywhere in the user's computer. The user doesn't need to do anything else but he can occasionally open the terminal created by the .bat file during the process and read the messages displayed. 

Bellow a brief description of how this application works:

<b>finances_table_to_db_and_mail</b> application works with 3 different sharepoint's folders* (ordered by year and month):

    1. Client's data
    2. Client's monthly invoices and bills
    3. Reports

*This folder's links bust be provided in advance for configuration to make the application work.

<h3>Base tables' download:</h3>
The application first looks for 2 base spreadsheets (client's contact data (email) and other client's data (ID, invoice number, etc) respectively) of the current month in <b>Client's data</b> folder using <strong>Selenium</strong>. If found, these spreadsheets are downloaded in an application's specific folder called <b>'raw_table/'</b>.

<h3>Downloaded table's management:</h3>
After downloading it the application uses <strong>OpenPyXL</strong> to extract relevant data from specific columns of the downloaded spreadsheets. With these extractions a third spreadsheet is created also with some new columns and placed in another application folder called 'edited_table/'. From the edited_table's spreadsheet the application uses <strong>Pandas</strong> to insert it in a <strong>SQLite3</strong> database.

With a database created the <strong>Django</strong>* framework comes to scene. This framework will be responsible with the database lines' management. The command <strong>inspectdb</strong> extracts <strong>SQLite3</strong>'s content and creates a model from it and the view 'EmailAttachByTable' works with this model aligned with <strong>Selenium</strong>.

*The application <b>finances_table_to_db_and_mail</b> doesn't use Django's server or any endpoint or url from it, but just its model and a single view instantiated out of its projects' folder.

<h3>Client's invoices and bills download and email sent:</h3>
Now it is time to use <strong>Selenium</strong> again. From every single model's row Django's view takes specific data and feeds Selenium. From each line Selenium goes back to the company's sharepoint in <b>Client's monthly invoices and bills</b> folder and looks for this data, which are pdfs and another spreadsheets. 

If found, they're selected, downloaded and moved to an application's folder called 'attachments/'. Then, an email is created using django's <strong>EmailMessage</strong> with this files attached to it and sent to the client. A copy of this email may be sent to the company's email if configured in django's 'settings'. If the email is succesfully sent the successful cases ('Sent') report is fed with the client's ID (brazilian's CNPJ) and its invoice's number (brazilian's NFE) and a message is displayed in .bat's terminal: 

´´´
"Email successfully sent! Check inbox."
´´´

If not found or something else fails, the unsuccesful cases ('Not sent') report is fed with this same client's info and another message is displayed in .bat's terminal:

```
"No client found for {CNPJ}!"
```

or 

```
"No nfe found for {NFE}!"
```

Or another error identified.

This process is made for every single client. 

<h3>At the end of the process:</h3>
At the end of it, the tables inside 'raw_table/' are deleted and a message is displayed in .bat's terminal:

```
"Application finished its process succesfully!"
```

The successful and unsuccessful reports' info are extracted and placed in a third report which is sent to sharepoint's Reports folder by Selenium.

With the 'raw_table/' folder emptied the application will look for the 2 base spreadsheets in <b>Client's data</b> folder again when manually restarted. These 2 may have updated or new data.
If the new base spreadsheets contain new data the application already have files to compare what is new and what is not and feed the 'edited_table/''s spreadsheet, which is not deleted at the end of a process, with new data.

<h3>When the month changes:</h3>
This application is designed to operate at the beggining and during the month. When it changes something else must be done: in the application's folder there is a file named "DELETE_ME_BEFORE_FIRST_MONTH_OPERATION.txt" that must be deleted before starting the first process of the month. Its deletion will delete all the application's tables and its reports. More about that in 


<br>

## A detailed description

<h3>Summary process</h3>

The whole application can be runned at the root directory by the script './run_everything_here.py' or by the .bat file 'script_for_bat_file.bat'.

It firstly inserts in the given table in 'raw_table/' a 'STATUS' column using <b>OpenPyXl</b> and saves it in 'edited_table/', after that it transforms the edited spreadsheet into a dataframe using <b>Pandas</b> and it is filtered by specific columns and inserts a new column 'ID'. 

After manipulation the dataframe is inserido in a database <b>SQLite3</b> in 'db/' and transformed into a <b>Django</b> model using the command <strong>inspectdb</strong>. This makes <b>Django</b> able to use the container <b>EmailMessage</b> for attachimng and sending emails to clients. 

<h3>Spreadsheet</h3>

The aplication firstly searches for a spreadsheet in the directory './finances_table_to_db_and_mail/management_before_django/raw_table'. if found the aplication follows up looking for attachments. If not, it uses <b>selenium</b> to search for the spreadsheet on sharepoint.

<h3>Attachments</h3>

To obtain them, the application uses the lib <b>Selenium</b> for searching for attachments by CNPJ and NFE on <b>sharepoint</b>. 
If found, they are downloaded one by one on the directory './finances_table_to_db_and_mail/robot_sharepoint/attachments/'. The attachments are read with './finances_table_to_db_and_mail/dj_project/filter_tables/views.py' and according to the attachments amount the appropriate template is chosen for the email body in './finances_table_to_db_and_mail/dj_project/filter_tables/templates/'.

When not found, the application follows up looking for other attachments.

<h3>Reports</h3>

The found and not found attachments are registered in text files at './finances_table_to_db_and_mail/robot_sharepoint/reports/'. When the process is ended or interrupted it is automatically created a a third text file that gathers the first two. This third text file is sent to sharepoint as report of the operaion even if it is not finalized.

## Application's behaviour by case:

Bellow a resumed list of the application behaviour by case:

ERROR:

    1. Interrupted process (lack of light energy, lack of internet, user closes terminal accidentally):
        Procedure:
            Process finished.
        When restart process:
            Spreadsheet is maintaned;
            Spreadsheet downloaded remains;
            Spreadsheet edited remains;
            Sent elements report remains;
            Not sent elements report deleted;
            Final report recriated.

    2. Interrupted process (internal error or voluntairly interruption of process on terminal (ex: end of working day)):
        Procedure:
            Final report sent to sharepoint;
            Process finished.
        When restart process:
            Spreadsheet is maintaned;
            Downloaded spreadsheet remains;
            Edited spreadsheet remains;
            Sent elements report remains;
            Not sent elements report deleted;
            Final report recriated.

IDEAL:

    3. Process ended durante período faturamentos (will billings will come):
        Procedure:
            Final report sent to sharepoint;
            Delete downloaded spreadsheet;
            Edited spreadsheet remains;
            Process finished.
        When restart process:
            spreadsheet remains;
            Downloaded spreadsheet remains;
            Edited spreadsheet remains;
            Sent elements report remains;
            Not sent elements report deleted;
            Final report recriated.

    4. Process ended (end of billings period - all billings sent OR MONTH TURN*):
        Procedure:
            Apagar Spreadsheets;
            Apagar relatórios;
            Process finished.
        When restart process:
            Download spreadsheet;
            Spreadsheet downloaded is created;
            Spreadsheet edited is created;
            Sent elements report is created;
            Not sent elements report is created;
            Final report recriated.

<br>

## Instalation:

<h3>0. It is first necessary to have instaled the following devices:</h3>

- The code versioning <b>[Git](https://git-scm.com/downloads)</b>.

- A <b>code editor</b>, also known as <b>IDE</b>. For instance, <strong>[Visual Studio Code (VSCode)](https://code.visualstudio.com/)</strong>.

- A <b> client API REST </b> program. <strong>[Insomnia](https://insomnia.rest/download)</strong> or <b>[Postman](https://www.postman.com/product/rest-client/)</b>, for instance.

- <p> And versioning your directory to receive the aplication clone:</p>

```
git init
```

<br>
<h3>1. Clone the repository <b>finances_tables_to_db_and_mail</b> by your machine terminal or by the IDE:</h3>

```
git clone https://github.com/AndreKuratomi/finances_tables_to_db_and_mail.git
```

WINDOWS:

Obs: In case of any mistake similar to this one: 

```
unable to access 'https://github.com/AndreKuratomi/finances_tables_to_db_and_mail.git/': SSL certificate problem: self-signed certificate in certificate chain
```

Configure git to disable SSL certification:

```
git config --global http.sslVerify "false"
```

<p>Enter the directory:</p>

```
cd finances_tables_to_db_and_mail
```
<br>

<h3>2. After cloning the repository install:</h3>

<h4>Virtual enviroment and update its dependencies with the following command:</h4>


LINUX:
```
python3 -m venv venv --upgrade-deps
```

WINDOWS:
```
py -m venv env
```
<br>
<h4>Ativate your virtual enviroment with the command:</h4>

LINUX:
```
source/venv/bin/activate
```

WINDOWS:

On Windows operational system it is necessary to configure the Execution Policy at PowerShell:

```
Get-ExecutionPolicy # to check the Execution policy type
Set-ExecutionPolicy RemoteSigned # to change the type of policy if the command above shows 'Restricted'
```
Obs: It may often be necessary to open PowerShell as administrador for that.

```
.\env\Scripts\activate
```
<br>
<h4>Install its dependencies:</h4>

```
pip install -r requirements.txt
```
<br>


WINDOWS:

In case any error similar to the one bellow be returned:

```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory: 'C:\\Users\\andre.kuratomi\\OneDrive - JC Gestao de Riscos\\Área de Trabalho\\tables_to_db_mail_for_finances\\tables_to_db_and_mail_finances\\env\\Lib\\site-packages\\jedi\\third_party\\django-stubs\\django-stubs\\contrib\\contenttypes\\management\\commands\\remove_stale_contenttypes.pyi'
HINT: This error might have occurred since this system does not have Windows Long Path support enabled. You can find information on how to enable this at https://pip.pypa.io/warnings/enable-long-paths
```

Run cmd as adminstrador with the following command:

```
reg.exe add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```
<br>

<h3>3. And run the aplication:</h3>

```
code .
```
<br>


<h3>4. Create <b>.env</b> file:</h3>

./
```
touch .env
```

Inside it we need to put our enviroment variables taking as reference the given file <b>.env.example</b>:

```
# DJANGO:
SECRET_KEY=secret_key

# EMAIL VARIABLES:
EMAIL_HOST_USER=host_email
EMAIL_HOST_PASSWORD=host_password

# SHAREPOINT VARIABLES:
SHAREPOINT_FOR_UPLOAD_URL=sharepoint_for_upload_url
SHAREPOINT_FATURAMENTO_URL=faturamento
SHAREPOINT_MEDICOES_URL=medicoes

DOWNLOAD_DIRECTORY=download_directory
RAW_TABLE_DIRECTORY=raw_table_url
```

Obs: Do not share info from .env file. It is already mentioned in .gitignore for not being pushed to the repo.

<br>

## Commands:

For all the necessary procedures for running the aplication we may only run the command bellow:

./

WINDOWS:
```
py run_everything_here.py
```

LINUX:
```
python3 run_everything_here.py
```

<br>

## References

- [Django](https://www.djangoproject.com/)
- [DjangoMail](https://docs.djangoproject.com/en/4.1/topics/email/)
- [Dotenv](https://www.npmjs.com/package/dotenv)
- [Git](https://git-scm.com/downloads)
- [OpenPyXl](https://openpyxl.readthedocs.io/en/stable/tutorial.html)
- [Pandas](https://pandas.pydata.org/docs/)
- [Python](https://www.python.org/downloads/)
- [Selenium](https://pypi.org/project/selenium/)
- [SQLite3](https://docs.python.org/3/library/sqlite3.html)
- [Visual Studio Code (VSCode)](https://code.visualstudio.com/)



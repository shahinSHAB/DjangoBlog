
# Simple Django Blog


## virtual environment
for create virtual environment you have many choices. for example you can use *virtualenv* package
```cmd
# get virtualenv package and create a virtual environment
py -m pip install virtualenv
```
```cmd
# after you install virtualenv
virtualenv your_virtual_name path --python= some version(if you desire specific version)
```
**notice** : project made by python 3.8.10 then you must adjust python version to 3.8.10 while creating virtual environment.

after you create virtual environment then you can install anything in requirements file.
```cmd
pip install -r requirements.txt
```
## Run server
for running server you prompt like below caus of settings is modified :

for run project in **local** :

```cmd
py manage.py runserver --settings=config.local
```
and run project in **product** :
```cmd
py manage.py runserver --settings=config.product
```
##### * tip
you can continue and prompt like always and its working and run local server itself 
```cms
# this prompt work without error
py manage.py runserver
``` 
**but for run another settings you must prompt it explicit**

## endpoints
in this project you can see endpoint with redoc, awagger and just simple schema.yml file

##### 1- **schema**
you must go to http://localhost:port/api/schema/
`http://localhost:port/api/schema
`
*if you get this endpoint its automatically create an update schema.yml to download*
##### 2- **Reduc**
you must go to http://localhost:port/api/reduc/
`http://localhost:port/api/reduc
`
##### 3- **Swagger-ui**
you must go to http://localhost:port/api/swagger-ui/
`http://localhost:port/api/swagger-ui
`

## .env
**dont forget to create .env file in your project root and define variables**
```.env
SECRET_KEY = your secret key
DATATBASE_URL = sqlite:///db.sqlite3 (or your another database that you connect in your local state project)
DEBUG = True
```
##### * tip
remember that you must create new secret key and keep secure that(for some reasons like if you use git)
one simple way is using python built-in module like secrets like :
```cmd
py -c 'import secrets; print(secrets.token_urlsafe())'
```
then you can copy generated token and pate it into .env file for SECRET_KEY

## whitenoise
for change state to product and handle or serve static files better installed whitenoise package
configs and any edit or modify was done and just run server in product.py setting


## Gunicorn
gunicorn is very strong and efficient than default django wsgi.
for using it you must first install it and prompt in terminal and create procfile to your project for using in production state
```cmd
#procfile
web: gunicorn (yourdjango_project).wsgi --log-file -
```


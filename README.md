# Sistema médico


## Descripción
Este proyecto tiene como objetivo crear un sistema web que facilite la realización de consultas médicas


## Requisitos
- XAMPP
- asgiref
- Django
- django-environ
- PyMySQL
- sqlparse
- tzdata


## Instalación
1. Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/brianrscode/sistema_medico.git
```

2. Crea un entorno virtual
```bash
python -m venv venv
```

3. Activa el entorno virtual
    - En Windows:

    ```bash
    venv\Scripts\activate
    ```

    - En macOS y Linux:

    ```bash
    source venv/bin/activate
    ```

4. Instala las librerías a través de `pip`:
```bash
pip install -r requirements.txt
```

5. Agrega tú archivo .env que contenga las variables de entorno de tu proyecto
```bash
SECRET_KEY=
DEBUG=True
NAME_BD=nombre_bd
USER_BD=usuario
PASSWORD_BD=contraseña
HOST_BD=localhost
PORT_BD=3306
LANGUAGE_CODE=
TIME_ZONE=
```

6. Activa Apache y MySQL en XAMPP

7. Crea la base de datos en XAMPP

8. Realiza las migraciones
```bash
python manage.py migrate
```

9. Ejecuta el proyecto
```bash
python manage.py runserver
```
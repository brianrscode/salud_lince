# Salud lince


## Descripción
Este proyecto tiene como objetivo crear un sistema medico web que facilite la realización de consultas médicas

## Instalación
1. Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/brianrscode/salud_lince.git
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
DEBUG=
NAME_BD=
USER_BD=
PASSWORD_BD=
HOST_BD=
PORT_BD=
TIME_ZONE=
```

6. Inicia tu administrador de base de datos

7. Crea la base de datos

8. Realiza las migraciones
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```

9. Ejecuta el proyecto
```bash
python manage.py runserver
```

## Vistas del sistema
<table>
    <tr>
        <td>
            <img src="imgs_proyecto/login.png" width=800>
        </td>
        <td>
            <img src="imgs_proyecto/dashboard_paciente.png" width=800>
        </td>
    </tr>
    <tr>
        <td>
            <img src="imgs_proyecto/historial_paciente.png" width=800>
        </td>
        <td>
            <img src="imgs_proyecto/consultas_medico.png" width=800>
        </td>
    </tr>
</table>
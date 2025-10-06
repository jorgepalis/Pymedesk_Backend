Despliegue en AWS EC2
======================

Sigue estos pasos para poner en línea el backend de Pymedesk en una instancia EC2 con Ubuntu.

1. **Crear y preparar la instancia**
	- Inicia sesión en AWS y crea una instancia EC2 (Ubuntu 22.04 LTS es una buena opción) con al menos 1 vCPU y 1 GB de RAM.
	- Abre los puertos necesarios en el Security Group: `22` (SSH) y `8000` para pruebas; más adelante podrás usar `80/443` detrás de un proxy.
	- Descarga el par de llaves `.pem` y conecta vía SSH: `ssh -i ruta/llave.pem ubuntu@<ip-publica>`.

2. **Actualizar paquetes del sistema**
	```bash
	sudo apt update && sudo apt upgrade -y
	sudo apt install python3.12 python3.12-venv python3-pip git -y
	```

3. **Clonar el proyecto**
	- `git clone https://github.com/jorgepalis/Pymedesk_Backend.git`
	- `cd Pymedesk_Backend`

4. **Crear entorno virtual e instalar dependencias**
	```bash
	python3.12 -m venv env
	source env/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt
	```

5. **Configurar variables de entorno**
	- Define variables de entorno en un .env.
	- Si usarás PostgreSQL u otra base, exporta las variables correspondientes (por defecto SQLite funciona sin configurar nada más).

6. **Aplicar migraciones y crear usuario admin**
	```bash
	python manage.py migrate
	python manage.py createsuperuser
	```

7. **Probar el servidor en modo desarrollo**
	```bash
	python manage.py runserver 0.0.0.0:8000
	```
	- Verifica desde tu navegador: `http://<ip-publica>:8000/swagger/`.

8. **Configurar Gunicorn y Nginx para producción**
	- Instala Gunicorn: `pip install gunicorn`.
	- Crea un servicio systemd para Gunicorn y configura Nginx como proxy reverso para servir en los puertos 80/443.
	- Asegura el sitio con certificados (Let’s Encrypt).

9. **Ejecutar pruebas automatizadas antes del despliegue**
	```bash
	python -m pytest
	```

10. **Automatizar tareas recurrentes**
	 - Usa `systemd` para mantener el proceso activo después de cerrar la sesión SSH.
	 - Configura backups de base de datos si usas una externa.

Con estos pasos tendrás el backend corriendo en EC2 listo para ser consumido por el frontend o por clientes externos.

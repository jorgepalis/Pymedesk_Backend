Pymedesk Backend
=================

API REST construida con Django 4.2 y Django REST Framework para autenticar usuarios mediante JWT, administrar productos y generar órdenes de compra consumidas por el frontend de Pymedesk.

Requisitos previos
------------------

- Python 3.12 (o compatible con el virtualenv incluido).
- Pip.

Configuración rápida
--------------------

```bash
# crear y activar entorno si aún no existe
python -m venv env
env\Scripts\activate

# instalar dependencias
pip install -r requirements.txt

# aplicar migraciones y crear superusuario opcional
python manage.py migrate
python manage.py createsuperuser

# ejecutar el servidor
python manage.py runserver
```

El servidor queda disponible en `http://127.0.0.1:8000/`. La documentación interactiva generada con drf-spectacular se expone en:

- `http://127.0.0.1:8000/swagger/`
- `http://127.0.0.1:8000/redoc/`
- Esquema OpenAPI: `http://127.0.0.1:8000/api/schema/`

Dependencias principales
------------------------

- `django`: marco principal.
- `djangorestframework`: serialización y vistas REST.
- `djangorestframework-simplejwt`: emisión y refresco de tokens JWT.
- `drf-spectacular`: generación del esquema OpenAPI y documentación.
- `django-cors-headers`: manejo de CORS para permitir peticiones del frontend.

Estructura de aplicaciones
--------------------------

- `core`: configuración global, middleware de CORS, integración de SimpleJWT y ruteo de la documentación.
- `users`: modelo personalizado basado en email, roles (`Role`), registro de usuarios, obtención de perfil (`/api/users/me/`) y endpoints JWT (`/api/users/login/`, `/api/users/register/`, `/api/users/refresh/`). Expone serializadores que retornan el rol y datos básicos para el frontend.
- `products`: catálogo CRUD. Cualquier usuario puede listar y ver (`GET /api/products/`), mientras que sólo administradores autenticados pueden crear, actualizar o eliminar (`POST/PUT/PATCH/DELETE /api/products/<id>/`).
- `orders`: órdenes y detalles de items. Los clientes autenticados crean pedidos (`POST /api/orders/`) y sólo ven los propios; los administradores pueden listar y gestionar todas las órdenes.

Lógica relevante
----------------

- El modelo `User` reemplaza al usuario estándar de Django y relaciona cada cuenta con un `Role` (por ejemplo, `admin` o `client`).
- Al registrar o iniciar sesión se devuelven tokens `access` y `refresh`; el perfil puede obtenerse con `GET /api/users/me/` usando el token de acceso.
- `Order` y `OrderItem` recalculan el total automáticamente cada vez que se guarda un item, garantizando consistencia de precios.
- `ProductViewSet` y `OrderViewSet` utilizan permisos personalizados (`users.permissions`) para restringir operaciones de administración.
- Base de datos por defecto: SQLite (`db.sqlite3`). Puedes configurar otra base editando `core/settings.py`.

Comandos útiles
---------------

- Ejecutar pruebas con pytest:

	```bash
	env\Scripts\activate
	python -m pytest
	```

	Las suites incluidas validan que solo administradores puedan crear o editar productos y que los clientes únicamente vean sus órdenes, mientras que los administradores listan todas. Los casos residen en `tests/test_products_permissions.py` y `tests/test_orders_access.py`.

- Crear roles iniciales:

	```bash
	python manage.py shell
	>>> from users.models import Role
	>>> Role.objects.get_or_create(name='admin')
	>>> Role.objects.get_or_create(name='client')
	```

Con esto el backend queda listo para atender al frontend y exponer la API necesaria para usuarios, productos y órdenes.

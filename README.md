# ✂ BarberSoft

Plataforma web para barberías: comunidad estilo Instagram/Facebook (publicaciones, fotos, videos, comentarios y me gusta), perfil de barberos con mapa y WhatsApp, CRM de clientes, facturación con ticket de 80 mm y chatbot.

**Tecnologías:** Python (Flask), SQLite, HTML, CSS y JavaScript.

## Cómo ejecutarlo
```
pip install -r requirements.txt
python app.py
```
Abre http://127.0.0.1:5000 (en Windows también puedes hacer doble clic en `INICIAR_WINDOWS.bat`).

## Cuentas de prueba
| Tipo | Entrada | Correo | Clave |
|---|---|---|---|
| Barbero | /admin/login | barbero@demo.do | demo1234 |
| Cliente | /login | cliente@demo.do | demo1234 |

## Antes de publicarlo en internet
- Define la variable de entorno `SECRET_KEY` con un valor largo y secreto.
- Elimina o cambia las cuentas demo.
- Desactiva `debug=True` al final de `app.py`.

import sqlite3, json, os, time, re
from functools import wraps
from flask import Flask, jsonify, g, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave")
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "barbersoft.db")
UP = os.path.join(BASE, "static", "uploads")
os.makedirs(UP, exist_ok=True)

PAGES = {
 "organizada": dict(icon="🏠", t="Tu barbería, mejor organizada", p=[
  "BarberSoft es una propuesta de negocio creada para ayudar a los propietarios de barberías a trabajar con más orden, aprovechar mejor su tiempo y tener una visión más clara de cómo marcha su negocio. En una barbería cada cita cuenta, cada producto tiene valor y cada cliente puede convertirse en un cliente frecuente.",
  "La idea es ofrecer en un solo sistema herramientas para organizar las citas, mantener un registro de los clientes, controlar los productos disponibles, administrar las comisiones y revisar las ventas. En lugar de depender de notas dispersas, el barbero o propietario consulta la información que necesita de manera más sencilla.",
  "Nuestra propuesta no consiste solamente en vender un programa: consiste en ofrecer una forma más práctica de administrar la barbería para dedicar más atención al servicio, al crecimiento y a la satisfacción de los clientes."]),
 "nosotros": dict(icon="👥", t="¿Quiénes somos?", p=[
  "BarberSoft es un emprendimiento tecnológico enfocado en las necesidades reales de las barberías. Nace con la intención de poner la organización al alcance de negocios de distintos tamaños, desde una barbería pequeña hasta un establecimiento con varios barberos.",
  "Queremos que la tecnología sea una ayuda, no una complicación. Por eso la propuesta contempla planes adaptables a las necesidades y al presupuesto de cada negocio, además de una atención cercana para orientar, resolver dudas y acompañar en el uso del sistema.",
  "La meta es construir relaciones duraderas con las barberías, ofreciendo una herramienta útil, una comunicación clara y un servicio en el que puedan confiar.",
  "Presentado por: Junior Eloi Santos Jorge · MT: 2020-3300040"]),
 "necesidad": dict(icon="🎯", t="¿Qué necesidad atendemos?", p=[
  "En el trabajo diario de una barbería, llevar las citas, recordar las preferencias de los clientes, saber qué productos quedan y revisar las ventas puede tomar tiempo. Cuando esa información no está organizada, es más difícil detectar oportunidades, evitar descuidos y saber cómo funciona el negocio.",
  "BarberSoft responde reuniendo en un mismo lugar funciones que ayuden a organizar la operación, para que el propietario tenga una mejor referencia al decidir y ofrezca una atención más consistente.",
  "El beneficio esperado es trabajar con mayor organización y visibilidad del negocio. Los resultados concretos dependerán de las funciones implementadas y de cómo cada barbería utilice el sistema."]),
 "beneficios": dict(icon="💈", t="¿Qué gana una barbería?", li=[
  "Citas más organizadas: consultar y administrar las reservas con mayor facilidad.",
  "Clientes mejor atendidos: datos registrados para un servicio más personal y que regresen.",
  "Mayor control de productos: revisar el inventario y saber qué reponer.",
  "Cuentas más claras: registro de ventas y seguimiento de comisiones.",
  "Información para decidir: datos organizados que ayuden a entender el movimiento del negocio.",
  "Una solución adaptable: opciones según el tamaño, prioridades y presupuesto."],
  p=["En pocas palabras: BarberSoft busca ayudar a que el negocio funcione con menos desorden y más información útil para tomar decisiones."]),
 "mision": dict(icon="🚀", t="Misión", p=["Ayudar a las barberías a organizar y administrar mejor su negocio mediante un software práctico, acompañado de una atención cercana y opciones que respondan a las necesidades de cada cliente."]),
 "vision": dict(icon="👁", t="Visión", p=["Convertirnos en una marca reconocida en la República Dominicana por aportar soluciones de gestión útiles y accesibles a las barberías, destacándonos por la confianza, la calidad del servicio y la mejora continua."]),
 "valores": dict(icon="⭐", t="Valores", li=[
  "Responsabilidad: cumplir los compromisos y atender las necesidades de nuestros clientes.",
  "Honestidad: explicar con claridad las funciones, los precios y el alcance de cada plan.",
  "Cercanía: tratar a cada cliente con respeto, paciencia y disposición para ayudar.",
  "Compromiso: que cada barbería encuentre una alternativa que se ajuste a su realidad.",
  "Calidad: una solución útil, clara y fácil de aprovechar.",
  "Confianza: relaciones transparentes y duraderas con los negocios que nos elijan."]),
 "estrategia": dict(icon="📣", t="Cómo daremos a conocer y venderemos BarberSoft", p=[
  "La estrategia comercial mostrará a los propietarios cómo BarberSoft puede ayudarles en su trabajo diario. En vez de una lista de características, presentaremos situaciones habituales y cómo el sistema podría resolverlas."],
  li=["Redes sociales: demostraciones, ejemplos de uso y mensajes centrados en beneficios.",
  "WhatsApp: responder preguntas, presentar planes y dar seguimiento a interesados.",
  "Contacto directo: conocer cómo se organizan hoy las barberías y cuáles son sus necesidades.",
  "Presentaciones del sistema: citas, clientes, inventario y ventas de forma sencilla.",
  "Seguimiento comercial: mantener el contacto con quien pida información o cotización, respetando sus tiempos."],
  p2=["El mensaje es claro: BarberSoft quiere ayudar al barbero a tener más control sobre su negocio y menos preocupaciones con la organización. La conversación comienza escuchando qué necesita cada barbería."]),
 "crm": dict(icon="🤝", t="Uso del CRM para convertir interesados en clientes", p=[
  "Para organizar las ventas se propone un CRM: una herramienta que mantiene ordenada la relación con clientes actuales y potenciales. Se registran datos de contacto, funciones que necesitan, cotizaciones enviadas y el estado de cada oportunidad.",
  "Por ejemplo, si el dueño de una barbería pregunta por citas e inventario, esa información se guarda para preparar una propuesta adecuada y darle seguimiento, reduciendo el riesgo de olvidar solicitudes.",
  "El CRM también ayuda a ofrecer una experiencia comercial más atenta. Dentro de esta plataforma, los barberos tienen su propio CRM en el panel administrativo."]),
 "objetivo": dict(icon="🏁", t="Objetivo general", p=["Desarrollar una propuesta comercial viable para BarberSoft, orientada a la promoción y venta de un software de gestión para barberías, mediante una oferta de valor centrada en las necesidades del cliente, una estrategia de comunicación y ventas y el uso de un CRM para organizar las relaciones comerciales y dar seguimiento a futuras oportunidades."]),
 "propuesta": dict(icon="💎", t="Nuestra propuesta de valor", p=[
  "BarberSoft te ayuda a poner tu barbería en orden para que puedas concentrarte en lo que mejor sabes hacer: ofrecer buenos cortes y atender a tus clientes.",
  "Con herramientas para organizar citas, clientes, productos, comisiones y ventas, buscamos hacer más sencilla la administración diaria. Como cada barbería es diferente, escuchamos primero, recomendamos las opciones adecuadas y mantenemos una comunicación clara.",
  "BarberSoft: menos desorden en la gestión, más claridad para crecer.",
  "Mensaje: «¿Tienes una barbería y quieres llevar tu negocio con más organización? Con BarberSoft tendrás en un solo lugar herramientas para administrar tus citas, registrar tus clientes, controlar tus productos y revisar tus ventas. Escríbenos para conocer la propuesta.»"]),
 "crecimiento": dict(icon="📈", t="Enfoque de crecimiento", p=[
  "BarberSoft se plantea como una oportunidad que puede crecer a medida que conozca mejor a sus clientes y valide cuáles funciones tienen mayor demanda. Próximos pasos: conversar con propietarios, probar la propuesta, definir planes y precios, preparar una demostración funcional y recoger opiniones.",
  "Las funciones, los precios y los resultados comerciales deberán confirmarse antes del lanzamiento. La prioridad es construir una solución que responda a necesidades reales y que los clientes perciban como útil."]),
}
SLUGS = list(PAGES)

SCHEMA = """
create table if not exists users(id integer primary key, name text, email text unique, pw text, role text,
 shop text, phone text, whatsapp text, address text, bio text, avatar text);
create table if not exists posts(id integer primary key, user_id integer, kind text, title text, body text, img text, created text);
create table if not exists clients(id integer primary key, owner_id integer, name text, phone text, email text, status text, notes text);
create table if not exists comments(id integer primary key, post_id integer, user_id integer, body text, created text);
create table if not exists likes(post_id integer, user_id integer, primary key(post_id,user_id));
create table if not exists invoices(id integer primary key, owner_id integer, client_name text, items text, itbis integer, total real, created text);
"""

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db
@app.teardown_appcontext
def close(e):
    d = g.pop("db", None)
    if d: d.close()
def q(sql, a=(), one=False):
    r = db().execute(sql, a).fetchall(); db().commit()
    return (r[0] if r else None) if one else r
def run(sql, a=()):
    c = db().execute(sql, a); db().commit(); return c.lastrowid

def init():
    with sqlite3.connect(DB) as c:
        c.executescript(SCHEMA)
        if not c.execute("select 1 from users").fetchone():
            c.execute("insert into users(name,email,pw,role,shop,whatsapp,address,bio) values(?,?,?,?,?,?,?,?)",
              ("Demo Barbero", "barbero@demo.do", gph("demo1234"), "barbero", "Demo Barber Shop", "18095550000",
               "Av. Winston Churchill, Santo Domingo", "Cortes clásicos y modernos. Reserva por WhatsApp."))
            c.execute("insert into posts(user_id,kind,title,body,created) values(1,'oferta','2x1 en cortes los martes','Trae a un amigo y paga un solo corte.',?)", (time.strftime("%Y-%m-%d %H:%M"),))
def migrate():
    with sqlite3.connect(DB) as c:
        if "video" not in [r[1] for r in c.execute("pragma table_info(posts)")]:
            c.execute("alter table posts add column video text")
def seed_cliente():
    with sqlite3.connect(DB) as c:
        if not c.execute("select 1 from users where email='cliente@demo.do'").fetchone():
            c.execute("insert into users(name,email,pw,role) values(?,?,?,?)", ("Cliente Demo", "cliente@demo.do", gph("demo1234"), "cliente"))
init(); migrate(); seed_cliente()

def me():
    return q("select * from users where id=?", (session["uid"],), one=True) if "uid" in session else None
@app.context_processor
def inject():
    return dict(me=me(), pages=PAGES)
@app.template_filter("wa")
def wa(n): return re.sub(r"\D", "", n or "")
@app.template_filter("items")
def items(s): return json.loads(s or "[]")

def barbero(f):
    @wraps(f)
    def w(*a, **k):
        u = me()
        if not u or u["role"] != "barbero":
            flash("Acceso administrativo solo para barberos."); return redirect(url_for("login", role="barbero"))
        return f(*a, **k)
    return w

VIDEO_EXT = {"mp4", "webm", "mov", "m4v"}
app.config["MAX_CONTENT_LENGTH"] = 150 * 1024 * 1024  # 150 MB por envío

@app.errorhandler(413)
def too_big(e):
    flash("El archivo es muy pesado (máximo 150 MB). Comprime el video e inténtalo de nuevo.")
    return redirect(url_for("posts"))

def save_video(field="video"):
    f = request.files.get(field)
    if f and f.filename:
        if f.filename.rsplit(".", 1)[-1].lower() not in VIDEO_EXT:
            flash("Formato de video no permitido. Usa MP4, WebM o MOV."); return None
        n = f"{int(time.time()*1000)}_{secure_filename(f.filename)}"; f.save(os.path.join(UP, n))
        return "uploads/" + n
    return None

def save_img(field="img"):
    f = request.files.get(field)
    if f and f.filename:
        n = f"{int(time.time()*1000)}_{secure_filename(f.filename)}"; f.save(os.path.join(UP, n))
        return "uploads/" + n
    return None

# ---------- público ----------
POSTSQL = "select p.*,u.shop,u.name,u.whatsapp,u.avatar,u.id uid from posts p join users u on u.id=p.user_id"
def enrich(rows):
    rows = [dict(r) for r in rows]; ids = [r["id"] for r in rows]
    if not ids: return rows
    m = ",".join("?" * len(ids)); uid = session.get("uid", 0)
    cm = q(f"select c.*,u.name,u.role,u.shop from comments c join users u on u.id=c.user_id where post_id in ({m}) order by c.id", ids)
    lk = {r["post_id"]: r["n"] for r in q(f"select post_id,count(*) n from likes where post_id in ({m}) group by post_id", ids)}
    mine = {r["post_id"] for r in q(f"select post_id from likes where user_id=? and post_id in ({m})", [uid] + ids)}
    for r in rows:
        r["comments"] = [c for c in cm if c["post_id"] == r["id"]]; r["likes"] = lk.get(r["id"], 0); r["liked"] = r["id"] in mine
    return rows

@app.route("/")
def home():
    n = lambda t: q(f"select count(*) c from {t}", one=True)["c"]
    st = dict(b=q("select count(*) c from users where role='barbero'", one=True)["c"], p=n("posts"), c=n("comments"), l=n("likes"))
    tk = [r["title"] for r in q("select title from posts where kind='oferta' order by id desc limit 6")]
    return render_template("home.html", posts=enrich(q(POSTSQL + " order by p.id desc limit 3")), st=st, tk=tk)

@app.route("/p/<slug>")
def pagina(slug):
    if slug not in PAGES: abort(404)
    i = SLUGS.index(slug)
    return render_template("page.html", p=PAGES[slug], slug=slug, prev=SLUGS[i-1] if i else None, nxt=SLUGS[i+1] if i < len(SLUGS)-1 else None)

@app.route("/ganancias")
def promo(): return render_template("promo.html")

@app.route("/comunidad")
def feed():
    k = request.args.get("k", "")
    posts = enrich(q(POSTSQL + (" where kind=?" if k else "") + " order by p.id desc", (k,) if k else ()))
    return render_template("feed.html", posts=posts, k=k, stories=q("select id,shop,name,avatar from users where role='barbero' order by id desc limit 12"))

@app.route("/barberos")
def barberos():
    return render_template("barberos.html", bs=q("select * from users where role='barbero' order by shop"))

@app.route("/barbero/<int:i>")
def barbero_perfil(i):
    b = q("select * from users where id=? and role='barbero'", (i,), one=True) or abort(404)
    return render_template("barbero.html", b=b, posts=enrich(q(POSTSQL + " where p.user_id=? order by p.id desc", (i,))))

# ---------- interacción (me gusta y comentarios) ----------
def need_login():
    return None if "uid" in session else (jsonify(error="Inicia sesión para participar"), 401)

@app.post("/api/like/<int:i>")
def api_like(i):
    if (r := need_login()): return r
    u = session["uid"]
    if q("select 1 from likes where post_id=? and user_id=?", (i, u)): run("delete from likes where post_id=? and user_id=?", (i, u)); on = False
    else: run("insert into likes values(?,?)", (i, u)); on = True
    return jsonify(liked=on, n=q("select count(*) c from likes where post_id=?", (i,), one=True)["c"])

@app.post("/api/comentar/<int:i>")
def api_comentar(i):
    if (r := need_login()): return r
    t = (request.get_json(silent=True) or {}).get("body", "").strip()[:300]
    if not t or not q("select 1 from posts where id=?", (i,)): return jsonify(error="Comentario vacío"), 400
    now = time.strftime("%Y-%m-%d %H:%M"); u = me()
    cid = run("insert into comments(post_id,user_id,body,created) values(?,?,?,?)", (i, u["id"], t, now))
    return jsonify(id=cid, name=u["shop"] or u["name"], role=u["role"], body=t, created=now)

@app.post("/api/comentario/<int:i>/borrar")
def api_cdel(i):
    if (r := need_login()): return r
    c = q("select c.*,p.user_id owner from comments c join posts p on p.id=c.post_id where c.id=?", (i,), one=True)
    if not c or session["uid"] not in (c["user_id"], c["owner"]): return jsonify(error="No permitido"), 403
    run("delete from comments where id=?", (i,)); return jsonify(ok=True)

# ---------- cuentas ----------
@app.route("/login", methods=["GET", "POST"], defaults={"role": "cliente"})
@app.route("/admin/login", methods=["GET", "POST"], defaults={"role": "barbero"})
def login(role):
    if request.method == "POST":
        u = q("select * from users where email=?", (request.form["email"].lower().strip(),), one=True)
        if u and cph(u["pw"], request.form["pw"]) and u["role"] == role:
            session["uid"] = u["id"]
            return redirect(url_for("admin") if role == "barbero" else url_for("feed"))
        flash("Credenciales incorrectas o tipo de cuenta equivocado.")
    return render_template("auth.html", role=role, mode="login")

@app.route("/registro", methods=["GET", "POST"], defaults={"role": "cliente"})
@app.route("/admin/registro", methods=["GET", "POST"], defaults={"role": "barbero"})
def registro(role):
    if request.method == "POST":
        f = request.form
        if len(f["pw"]) < 6: flash("La contraseña debe tener al menos 6 caracteres.")
        elif q("select 1 from users where email=?", (f["email"].lower().strip(),)): flash("Ese correo ya está registrado.")
        else:
            session["uid"] = run("insert into users(name,email,pw,role,shop,whatsapp,address) values(?,?,?,?,?,?,?)",
                (f["name"], f["email"].lower().strip(), gph(f["pw"]), role, f.get("shop", ""), f.get("whatsapp", ""), f.get("address", "")))
            return redirect(url_for("admin") if role == "barbero" else url_for("feed"))
    return render_template("auth.html", role=role, mode="registro")

@app.route("/salir")
def salir(): session.clear(); return redirect(url_for("home"))

# ---------- panel barbero ----------
@app.route("/admin")
@barbero
def admin():
    u = me()["id"]
    s = dict(posts=q("select count(*) c from posts where user_id=?", (u,), one=True)["c"],
             clients=q("select count(*) c from clients where owner_id=?", (u,), one=True)["c"],
             inv=q("select count(*) c, coalesce(sum(total),0) t from invoices where owner_id=?", (u,), one=True))
    return render_template("admin.html", s=s)

@app.route("/admin/perfil", methods=["GET", "POST"])
@barbero
def perfil():
    if request.method == "POST":
        f = request.form; av = save_img("avatar") or me()["avatar"]
        run("update users set name=?,shop=?,phone=?,whatsapp=?,address=?,bio=?,avatar=? where id=?",
            (f["name"], f["shop"], f["phone"], f["whatsapp"], f["address"], f["bio"], av, session["uid"]))
        flash("Perfil actualizado."); return redirect(url_for("perfil"))
    return render_template("perfil.html")

@app.route("/admin/publicaciones", methods=["GET", "POST"])
@barbero
def posts():
    u = session["uid"]; e = request.args.get("edit", type=int)
    if request.method == "POST":
        f = request.form; img = save_img(); vid = save_video()
        if f.get("id"):
            run("update posts set kind=?,title=?,body=?,img=coalesce(?,img),video=coalesce(?,video) where id=? and user_id=?", (f["kind"], f["title"], f["body"], img, vid, f["id"], u))
        else:
            run("insert into posts(user_id,kind,title,body,img,video,created) values(?,?,?,?,?,?,?)", (u, f["kind"], f["title"], f["body"], img, vid, time.strftime("%Y-%m-%d %H:%M")))
        return redirect(url_for("posts"))
    return render_template("posts.html", rows=q("select * from posts where user_id=? order by id desc", (u,)),
        ed=q("select * from posts where id=? and user_id=?", (e, u), one=True) if e else None)

@app.post("/admin/publicaciones/<int:i>/borrar")
@barbero
def post_del(i):
    if q("select 1 from posts where id=? and user_id=?", (i, session["uid"])):
        run("delete from comments where post_id=?", (i,)); run("delete from likes where post_id=?", (i,)); run("delete from posts where id=?", (i,))
    return redirect(url_for("posts"))

@app.route("/admin/crm", methods=["GET", "POST"])
@barbero
def crm():
    u = session["uid"]; e = request.args.get("edit", type=int)
    if request.method == "POST":
        f = request.form; v = (f["name"], f["phone"], f["email"], f["status"], f["notes"])
        if f.get("id"): run("update clients set name=?,phone=?,email=?,status=?,notes=? where id=? and owner_id=?", v + (f["id"], u))
        else: run("insert into clients(name,phone,email,status,notes,owner_id) values(?,?,?,?,?,?)", v + (u,))
        return redirect(url_for("crm"))
    return render_template("crm.html", rows=q("select * from clients where owner_id=? order by id desc", (u,)),
        ed=q("select * from clients where id=? and owner_id=?", (e, u), one=True) if e else None)

@app.post("/admin/crm/<int:i>/borrar")
@barbero
def crm_del(i): run("delete from clients where id=? and owner_id=?", (i, session["uid"])); return redirect(url_for("crm"))

def calc(f):
    its = [dict(d=d, c=float(c or 0), p=float(p or 0)) for d, c, p in zip(f.getlist("d"), f.getlist("c"), f.getlist("p")) if d.strip()]
    sub = sum(i["c"] * i["p"] for i in its); tax = 1 if f.get("itbis") else 0
    return json.dumps(its), tax, round(sub * (1.18 if tax else 1), 2)

@app.route("/admin/facturas")
@barbero
def facturas():
    return render_template("facturas.html", rows=q("select * from invoices where owner_id=? order by id desc", (session["uid"],)))

@app.route("/admin/facturas/nueva", methods=["GET", "POST"])
@app.route("/admin/facturas/<int:i>/editar", methods=["GET", "POST"])
@barbero
def factura_form(i=None):
    u = session["uid"]
    inv = q("select * from invoices where id=? and owner_id=?", (i, u), one=True) if i else None
    if i and not inv: abort(404)
    if request.method == "POST":
        its, tax, tot = calc(request.form); n = request.form["client_name"]
        if i: run("update invoices set client_name=?,items=?,itbis=?,total=? where id=?", (n, its, tax, tot, i))
        else: i = run("insert into invoices(owner_id,client_name,items,itbis,total,created) values(?,?,?,?,?,?)", (u, n, its, tax, tot, time.strftime("%Y-%m-%d %H:%M")))
        return redirect(url_for("ticket", i=i))
    return render_template("factura_form.html", inv=inv, cl=q("select name from clients where owner_id=?", (u,)))

@app.post("/admin/facturas/<int:i>/borrar")
@barbero
def factura_del(i): run("delete from invoices where id=? and owner_id=?", (i, session["uid"])); return redirect(url_for("facturas"))

@app.route("/admin/facturas/<int:i>/ticket")
@barbero
def ticket(i):
    inv = q("select * from invoices where id=? and owner_id=?", (i, session["uid"]), one=True) or abort(404)
    return render_template("ticket.html", inv=inv)

if __name__ == "__main__":
    app.run(debug=True)

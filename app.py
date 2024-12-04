from flask import Flask,request,render_template,session,redirect
from flask_mail import Mail, Message
import os
from werkzeug.utils import secure_filename
import mysql.connector

cnx = mysql.connector.connect(host='127.0.0.1', user='root', password='', database='Login_facebook')
cursor =  cnx.cursor(dictionary=True)


app = Flask(__name__)
# Establecer la clave secreta para las sesiones
app.config['SECRET_KEY'] = 'leopardo123'

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587  
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'aaronlurita123@gmail.com'
app.config['MAIL_PASSWORD'] = 'hkcbrljxanchiywd'  
app.config['MAIL_DEFAULT_SENDER'] = ('Facebook Clone', 'aaronlurita123@gmail.com') 

mail = Mail(app)

# Ruta para renderizar la página de inicio de sesión
@app.route("/")
def home():
    return render_template("InicioSesion.html")


# Ruta para manejar el inicio de sesión
@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario")
    passwordd = request.form.get("password")

    try:
        # Llamar al procedimiento almacenado
        cursor.callproc("sp_Usuario_Login", (usuario, passwordd))
        for resultados in cursor.stored_results():
            usuario_data = resultados.fetchall()

            
            if usuario_data:
                session['id'] = usuario_data[0]['id']  # ID del usuario
                session['Nombres'] = usuario_data[0]['Nombres']  # Nombres del usuario
                session['Apellidos'] = usuario_data[0]['Apellidos'] 
                
                # Obtener solicitudes de amistad pendientes
                id_usuario = usuario_data[0]['id']
                query_solicitudes = """
                    SELECT sa.id AS id_solicitud, sa.estado, sa.fecha_solicitud, 
                           u.Nombres AS nombre_emisor, u.Apellidos AS apellido_emisor
                    FROM SolicitudAmistad sa
                    JOIN Usuario u ON sa.idUsuarioEmisor = u.id
                    WHERE sa.idUsuarioReceptor = %s AND sa.estado = 'pendiente'
                """
                cursor.execute(query_solicitudes, (id_usuario,))
                solicitudes = cursor.fetchall()
                
                 # Obtener amigos aceptados
                query_amigos = """
                    SELECT u.id AS id_amigo, u.Nombres, u.Apellidos
                    FROM SolicitudAmistad sa
                    JOIN Usuario u ON (sa.idUsuarioEmisor = u.id OR sa.idUsuarioReceptor = u.id)
                    WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s)
                      AND sa.estado = 'aceptada'
                      AND u.id != %s
                """
                cursor.execute(query_amigos, (id_usuario, id_usuario, id_usuario))
                amigos = cursor.fetchall()
                
                 # Historias propias
                query_mis_historias = "SELECT contenido, fecha_publicacion FROM Historias WHERE idUsuario = %s"
                cursor.execute(query_mis_historias, (id_usuario,))
                mis_historias = cursor.fetchall()

                # Historias de amigos
                query_amigos_historias = """
                    SELECT h.contenido, h.fecha_publicacion, u.Nombres, u.Apellidos
                    FROM Historias h
                    JOIN Usuario u ON h.idUsuario = u.id
                    WHERE h.idUsuario IN (
                        SELECT CASE WHEN sa.idUsuarioEmisor = %s THEN sa.idUsuarioReceptor ELSE sa.idUsuarioEmisor END
                        FROM SolicitudAmistad sa
                        WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s) AND sa.estado = 'aceptada'
                    )
                """
                cursor.execute(query_amigos_historias, (id_usuario, id_usuario, id_usuario))
                historias_amigos = cursor.fetchall()
                
                query_publicaciones = """
                    SELECT p.contenido, p.foto, p.fecha_publicacion, u.Nombres, u.Apellidos
                    FROM Publicacion p
                    JOIN Usuario u ON p.idUsuario = u.id
                    WHERE p.idUsuario = %s OR p.idUsuario IN (
                        SELECT CASE WHEN sa.idUsuarioEmisor = %s THEN sa.idUsuarioReceptor ELSE sa.idUsuarioEmisor END
                        FROM SolicitudAmistad sa
                        WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s) AND sa.estado = 'aceptada'
                    )
                    ORDER BY p.fecha_publicacion DESC
                """
                cursor.execute(query_publicaciones, (id_usuario, id_usuario, id_usuario, id_usuario))
                publicaciones = cursor.fetchall()

                # Redirige a la página inicio
                return render_template("Inicio.html", usuario=usuario_data[0], solicitudes=solicitudes, amigos=amigos,mis_historias=mis_historias, historias_amigos=historias_amigos,publicaciones=publicaciones) 
            else:
                return render_template("InicioSesion.html", error="Credenciales incorrectas.")
    except Exception as e:
        return render_template("InicioSesion.html", error=f"Error en el sistema: {str(e)}")


# Ruta para renderizar la página de registro
@app.route("/registro")
def registro():
    return render_template("registro.html")

# Ruta para manejar el registro de usuarios
@app.route("/registros", methods=["POST"])
def registros():
    nombres = request.form.get("nombres")
    apellidos = request.form.get("apellidos")
    dianacimiento = request.form.get("diaNacimiento")
    mesnacimiento = request.form.get("mesNacimiento")
    anonacimiento = request.form.get("anoNacimiento")
    genero = request.form.get("genero")
    telefono = request.form.get("telefono")
    correo = request.form.get("correo")
    password = request.form.get("password")

    try:
        # Llamar al procedimiento almacenado
        cursor.callproc("sp_Usuario_Insert", (nombres, apellidos,dianacimiento,mesnacimiento,anonacimiento,genero,telefono,correo,password))
        cnx.commit()
            # Redirige a la página inicio
        return render_template("InicioSesion.html", success="Usuario registrado exitosamente.")
               
    except Exception as e:
        return render_template("registro.html", error=f"Error en el sistema: {str(e)}")

@app.route("/inicio")
def inicio():
    if "id" in session:  # Verifica si la sesión está activa
        id_usuario = session['id']
        try:
            # Obtener solicitudes de amistad pendientes
            query_solicitudes = """
                SELECT sa.id AS id_solicitud, sa.estado, sa.fecha_solicitud, 
                       u.Nombres AS nombre_emisor, u.Apellidos AS apellido_emisor
                FROM SolicitudAmistad sa
                JOIN Usuario u ON sa.idUsuarioEmisor = u.id
                WHERE sa.idUsuarioReceptor = %s AND sa.estado = 'pendiente'
            """
            cursor.execute(query_solicitudes, (id_usuario,))
            solicitudes = cursor.fetchall()

            # Obtener amigos aceptados
            query_amigos = """
                SELECT u.id AS id_amigo, u.Nombres, u.Apellidos
                FROM SolicitudAmistad sa
                JOIN Usuario u ON (sa.idUsuarioEmisor = u.id OR sa.idUsuarioReceptor = u.id)
                WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s)
                  AND sa.estado = 'aceptada'
                  AND u.id != %s
            """
            cursor.execute(query_amigos, (id_usuario, id_usuario, id_usuario))
            amigos = cursor.fetchall()
            query_publicaciones = """
                    SELECT p.contenido, p.foto, p.fecha_publicacion, u.Nombres, u.Apellidos
                    FROM Publicacion p
                    JOIN Usuario u ON p.idUsuario = u.id
                    WHERE p.idUsuario = %s OR p.idUsuario IN (
                        SELECT CASE WHEN sa.idUsuarioEmisor = %s THEN sa.idUsuarioReceptor ELSE sa.idUsuarioEmisor END
                        FROM SolicitudAmistad sa
                        WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s) AND sa.estado = 'aceptada'
                    )
                    ORDER BY p.fecha_publicacion DESC
                """
            cursor.execute(query_publicaciones, (id_usuario, id_usuario, id_usuario, id_usuario))
            publicaciones = cursor.fetchall()
            
            # Obtener amigos aceptados
            query_amigos = """
                    SELECT u.id AS id_amigo, u.Nombres, u.Apellidos
                    FROM SolicitudAmistad sa
                    JOIN Usuario u ON (sa.idUsuarioEmisor = u.id OR sa.idUsuarioReceptor = u.id)
                    WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s)
                      AND sa.estado = 'aceptada'
                      AND u.id != %s
                """
            cursor.execute(query_amigos, (id_usuario, id_usuario, id_usuario))
            amigos = cursor.fetchall()
                
                 # Historias propias
            query_mis_historias = "SELECT contenido, fecha_publicacion FROM Historias WHERE idUsuario = %s"
            cursor.execute(query_mis_historias, (id_usuario,))
            mis_historias = cursor.fetchall()

                # Historias de amigos
            query_amigos_historias = """
                    SELECT h.contenido, h.fecha_publicacion, u.Nombres, u.Apellidos
                    FROM Historias h
                    JOIN Usuario u ON h.idUsuario = u.id
                    WHERE h.idUsuario IN (
                        SELECT CASE WHEN sa.idUsuarioEmisor = %s THEN sa.idUsuarioReceptor ELSE sa.idUsuarioEmisor END
                        FROM SolicitudAmistad sa
                        WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s) AND sa.estado = 'aceptada'
                    )
                """
            cursor.execute(query_amigos_historias, (id_usuario, id_usuario, id_usuario))
            historias_amigos = cursor.fetchall()
            
            # Renderiza la página de inicio con los datos de sesión
            return render_template("Inicio.html", 
                                   usuario={"id": session['id'], 
                                            "Nombres": session['Nombres'], 
                                            "Apellidos": session['Apellidos']}, 
                                   solicitudes=solicitudes, amigos=amigos,publicaciones=publicaciones,mis_historias=mis_historias, historias_amigos=historias_amigos)
        except Exception as e:
            return f"Error: {str(e)}" 
    else:
        return render_template("InicioSesion.html")



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/publicar", methods=["POST"])
def publicar():
    if 'id' not in session:
        return redirect("/login")
    
    id_usuario = session['id']
    contenido = request.form.get("contenido")
    foto = None

    # Manejar la subida de la foto
    if 'foto' in request.files:
        file = request.files['foto']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            foto = f"img/{filename}"

    # Insertar la publicación en la base de datos
    query = "INSERT INTO Publicacion (idUsuario, contenido, foto) VALUES (%s, %s, %s)"
    cursor.execute(query, (id_usuario, contenido, foto))
    cnx.commit()

    return redirect("/inicio")

@app.route('/add_story', methods=['POST'])
def add_story():
    if 'id' not in session:
        return redirect("/login")
    
    archivo = request.files.get('archivo')
    contenido = request.form.get('contenido') 
    id_usuario = session['id']
    
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        archivo_url = f"img/{filename}"

        try:
            query = "INSERT INTO Historias (idUsuario, contenido, archivo_url) VALUES (%s, %s, %s)"
            cursor.execute(query, (id_usuario, contenido, archivo_url))
            cnx.commit()
            return redirect("/inicio")
        except Exception as e:
            return render_template("Inicio.html", error=f"Error al añadir historia: {str(e)}")
    else:
        return render_template("Inicio.html", error="Archivo no válido.")

# Ruta para renderizar la página de olvidaste passwordd
@app.route("/olvidaste")
def olvidaste():
    return render_template("olvidaste_password.html")

@app.route("/olvidastePassword", methods=["POST"])
def olvide():
    usuario = request.form.get("usuario")
    try:
        # Llamar al procedimiento almacenado
        cursor.callproc("sp_Usuario_RecuperarPassword", (usuario,))
        for resultados in cursor.stored_results():
            usuario = resultados.fetchall()
            
            if usuario:
                # Redirige a la página inicio
                return render_template("cuenta_identificada.html", usuario=usuario[0]) 
            else:
                return render_template("olvidaste_password.html", error="Correo o telefono no encontrado.")
    except Exception as e:
        return render_template("olvidaste_password.html", error=f"Error en el sistema: {str(e)}")


def enviar_correo_recuperacion(correo):  
    try:
        # Crear un enlace de restablecimiento
        enlace = f"http://127.0.0.1:5000/restablecer?correo={correo}"
        
        # Crear el mensaje
        msg = Message("Restablecer Contraseña",recipients=[correo],)
        msg.body = f"""Hola,Hemos recibido una solicitud para restablecer tu contraseña.
        Por favor, haz clic en el siguiente enlace para restablecerla:
        {enlace}

        Si no realizaste esta solicitud, ignora este correo.
        Saludos,
        Facebook Clone
        """
        mail.send(msg)
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        raise

@app.route("/enviarCorreoRecuperacion", methods=["POST"])
def enviarCorreoRecuperacion():
    correo = request.form.get("correo")
    try:
        # Enviar el correo de recuperación
        enviar_correo_recuperacion(correo)

        # Redirigir al usuario con un mensaje de éxito
        return render_template("cuenta_identificada.html",usuario={"Correo": correo},success="Correo de recuperación enviado exitosamente. Revisa tu bandeja de entrada."
        )
    except Exception as e:
        return render_template("cuenta_identificada.html",usuario={"Correo": correo},error=f"Error al enviar el correo: {str(e)}")
    
@app.route("/restablecer", methods=["GET", "POST"])
def procesar_restablecimiento():
    if request.method == "GET":
        # Obtener el correo desde la URL
        correo = request.args.get("correo")
        return render_template("restablecer.html", correo=correo)

    if request.method == "POST":
        correo = request.form.get("correo")
        nueva_contraseña = request.form.get("password")
       
        try:
            # Actualizar la contraseña en la base de datos
            cursor.callproc("sp_Usuario_Update", (correo, nueva_contraseña))
            cnx.commit()
            return render_template("InicioSesion.html", success="Contraseña restablecida con éxito.")
        except Exception as e:
            return render_template("restablecer.html", error=f"Error: {str(e)}", correo=correo)
        
# Ruta para renderizar la página de solicitudes
@app.route("/solicitudes")
def solicitudes():
    # Verifica si el usuario está autenticado
    if 'id' not in session:
        return render_template("InicioSesion.html", error="Debes iniciar sesión para ver tus solicitudes.")
    
    try:
        id_usuario = session['id'] 
        # obtener las solicitudes de amistad pendientes
        query = """
            SELECT sa.id AS id_solicitud, sa.estado, sa.fecha_solicitud, 
                   u.Nombres AS nombre_emisor, u.Apellidos AS apellido_emisor
            FROM SolicitudAmistad sa
            JOIN Usuario u ON sa.idUsuarioEmisor = u.id
            WHERE sa.idUsuarioReceptor = %s
        """
        cursor.execute(query, (id_usuario,))
        solicitudes = cursor.fetchall()
        
        # Obtener sugerencias de amistad
        query_sugerencias = """
            SELECT u.id, u.Nombres, u.Apellidos
            FROM Usuario u
            LEFT JOIN SolicitudAmistad sa1 ON sa1.idUsuarioEmisor = u.id AND sa1.idUsuarioReceptor = %s
            LEFT JOIN SolicitudAmistad sa2 ON sa2.idUsuarioReceptor = u.id AND sa2.idUsuarioEmisor = %s
            WHERE u.id != %s
              AND (sa1.estado IS NULL AND sa2.estado IS NULL);
        """
        cursor.execute(query_sugerencias, (id_usuario, id_usuario, id_usuario))
        sugerencias = cursor.fetchall()

        # Renderiza la plantilla con las solicitudes
        return render_template("solicitudes.html", solicitudes=solicitudes ,sugerencias=sugerencias)
    except Exception as e:
        return render_template("Inicio.html", error=f"Error al cargar las solicitudes: {str(e)}")

@app.route("/enviar_solicitud/<int:amigo_id>", methods=["POST"])
def enviar_solicitud(amigo_id):
    if 'id' not in session:
        return render_template("InicioSesion.html", error="Debes iniciar sesión para realizar esta acción.")
    try:
        id_usuario = session['id']
        cursor.callproc("EnviarSolicitudAmistad", (id_usuario, amigo_id))
        cnx.commit()
        return redirect("/solicitudes")
    except Exception as e:
        return render_template("solicitudes.html", error=f"Error al enviar la solicitud: {str(e)}")
    

@app.route("/solicitud/aceptar/<int:id>", methods=["POST"])
def aceptar_solicitud(id):
    if 'id' not in session:
        return render_template("InicioSesion.html", error="Debes iniciar sesión para realizar esta acción.")
    try:
        # Llamar al procedimiento almacenado para aceptar la solicitud
        cursor.callproc("AceptarSolicitudAmistad", (id,))
        cnx.commit()
        return redirect("/solicitudes")
    except Exception as e:
        return render_template("solicitudes.html", error=f"Error al aceptar la solicitud: {str(e)}")


@app.route("/solicitud/rechazar/<int:id>", methods=["POST"])
def rechazar_solicitud(id):
    if 'id' not in session:
        return render_template("InicioSesion.html", error="Debes iniciar sesión para realizar esta acción.")
    try:
        # Llamar al procedimiento almacenado para rechazar la solicitud
        cursor.callproc("RechazarSolicitudAmistad", (id,))
        cnx.commit()
        return render_template("solicitudes.html")
    except Exception as e:
        return render_template("solicitudes.html", error=f"Error al rechazar la solicitud: {str(e)}")
    
@app.route("/amigos")
def amigos():
    if 'id' not in session:
        return render_template("InicioSesion.html", error="Debes iniciar sesión para ver tus amigos.")
    try:
        id_usuario = session['id']
        query_amigos = """
            SELECT u.id AS id_amigo, u.Nombres, u.Apellidos
            FROM SolicitudAmistad sa
            JOIN Usuario u ON (sa.idUsuarioEmisor = u.id OR sa.idUsuarioReceptor = u.id)
            WHERE (sa.idUsuarioEmisor = %s OR sa.idUsuarioReceptor = %s) 
              AND sa.estado = 'aceptada'
              AND u.id != %s
        """
        cursor.execute(query_amigos, (id_usuario, id_usuario, id_usuario))
        amigos = cursor.fetchall()
        return render_template("amigos.html", amigos=amigos)
    except Exception as e:
        return render_template("Inicio.html", error=f"Error al cargar los amigos: {str(e)}")
    
    
@app.route("/mensajes/<int:amigo_id>", methods=["GET", "POST"])
def mensajes(amigo_id):
    if 'id' not in session:
        return render_template("InicioSesion.html", error="Debes iniciar sesión para enviar mensajes.")
    try:
        id_usuario = session['id']

        # Obtener información del amigo
        query_amigo = "SELECT Nombres, Apellidos FROM Usuario WHERE id = %s"
        cursor.execute(query_amigo, (amigo_id,))
        amigo = cursor.fetchone()

        if not amigo:
            return render_template("Inicio.html", error="Amigo no encontrado.")

        # Si se envía un mensaje (POST)
        if request.method == "POST":
            contenido = request.form.get("contenido")

            if contenido.strip():  # Verificar que no esté vacío
                query_procedure = "CALL EnviarMensaje(%s, %s, %s)"
                cursor.execute(query_procedure, (id_usuario, amigo_id, contenido))
                cnx.commit()
            else:
                return render_template("mensajes.html", amigo=amigo, error="El mensaje no puede estar vacío.")

        # Obtener el historial de mensajes (para GET y después de POST)
        query_mensajes = """
            SELECT contenido, idUsuarioEmisor AS emisor, fecha_envio
            FROM Mensaje
            WHERE (idUsuarioEmisor = %s AND idUsuarioReceptor = %s)
            OR (idUsuarioEmisor = %s AND idUsuarioReceptor = %s)
            ORDER BY fecha_envio ASC
        """
        cursor.execute(query_mensajes, (id_usuario, amigo_id, amigo_id, id_usuario))
        mensajes = cursor.fetchall()

        return render_template("mensajes.html", amigo=amigo, mensajes=mensajes)

    except Exception as e:
        return render_template("Inicio.html", error=f"Error al cargar la ventana de mensajes: {str(e)}")

if __name__ == "__main__":
    app.run(debug=False, port=5000)

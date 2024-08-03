from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'proyecto'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'mysecretkey'

mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['txtUsuario']
        password = request.form['txtPass']
        role = request.form.get('role')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s AND role = %s', (usuario, password, role))
        account = cursor.fetchone()

        if account:
            if role == 'admin':
                return redirect(url_for('vistaadmin'))
            else:
                return redirect(url_for('inicio'))
        else:
            flash('Usuario, contraseña o perfil incorrectos', 'danger')

    return render_template('login.html')

@app.route('/admin_usuarios')
def admin_usuarios():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['txtNombre']
        fecha_nacimiento = request.form['txtFechaNacimiento']
        direccion = request.form['txtDireccion']
        telefono = request.form['txtTelefono']
        usuario = request.form['txtUsuario']
        email = request.form['txtEmail']
        contraseña = request.form['txtPass']
        role = request.form['role']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO usuarios (nombre, fecha_nacimiento, direccion, telefono, usuario, email, contraseña, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                       (nombre, fecha_nacimiento, direccion, telefono, usuario, email, contraseña, role))
        mysql.connection.commit()
        flash('Usuario registrado satisfactoriamente', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edituser(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nombre = request.form['txtNombre']
        fecha_nacimiento = request.form['txtFechaNacimiento']
        direccion = request.form['txtDireccion']
        telefono = request.form['txtTelefono']
        usuario = request.form['txtUsuario']
        email = request.form['txtEmail']
        contraseña = request.form['txtPass']
        role = request.form['role']

        cursor.execute('UPDATE usuarios SET nombre = %s, fecha_nacimiento = %s, direccion = %s, telefono = %s, usuario = %s, email = %s, contraseña = %s, role = %s WHERE id = %s',
                       (nombre, fecha_nacimiento, direccion, telefono, usuario, email, contraseña, role, id))
        mysql.connection.commit()
        flash('Usuario actualizado satisfactoriamente')
        return redirect(url_for('admin_usuarios'))

    cursor.execute('SELECT * FROM usuarios WHERE id = %s', [id])
    usuario = cursor.fetchone()
    return render_template('edituser.html', usuario=usuario)

@app.route('/delete/<id>', methods=['POST'])
def delete_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM usuarios WHERE id = %s', [id])
    mysql.connection.commit()
    flash('Usuario eliminado satisfactoriamente')
    return redirect(url_for('admin_usuarios'))

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM plantas WHERE nombre LIKE %s OR descripcion LIKE %s', ('%' + query + '%', '%' + query + '%'))
    resultados = cursor.fetchall()
    return render_template('Plantas.html', query=query, plantas=resultados)

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

@app.route('/huertos2')
def huertos2():
    return render_template('huertos2.html')

@app.route('/plantas2')
def plantas2():
    return render_template('plantas2.html')

@app.route('/articulos2')
def articulos2():
    return render_template('articulos2.html')

@app.route('/herramientas2')
def herramientas2():
    return render_template('herramientas2.html')

@app.route('/Plantas')
def plantas():
    return render_template('Plantas.html')

@app.route('/Herramientas')
def herramientas():
    return render_template('Herramientas.html')

@app.route('/vistaadmin')
def vistaadmin():
    return render_template('vistaadmin.html')


@app.route('/Foro', methods=['GET', 'POST'])
def foro():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        contenido = request.form['contenido']
        autor = "Anonimo"  # Reemplaza con el nombre del usuario logueado si tienes un sistema de autenticación
        cursor.execute('INSERT INTO publicaciones (contenido, autor) VALUES (%s, %s)', (contenido, autor))
        mysql.connection.commit()
        flash('Publicación exitosa', 'success')
        return redirect(url_for('foro'))

    cursor.execute('SELECT * FROM publicaciones ORDER BY fecha_publicacion DESC')
    publicaciones = cursor.fetchall()
    return render_template('foro.html', publicaciones=publicaciones)

@app.route('/Articulos')
def articulos():
    return render_template('Articulos.html')

@app.route('/Huertos')
def huertos():
    return render_template('Huertos.html')

@app.route('/Citas')
def citas():
    return render_template('Citas.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/get_publicaciones')
def get_publicaciones():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM publicaciones ORDER BY fecha_publicacion DESC')
    publicaciones = cursor.fetchall()
    return jsonify(publicaciones)

@app.route('/Huertos', methods=['GET', 'POST'])
def gestionar_huertos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        imagen = request.files['imagen']

        # Verifica si hay un archivo de imagen
        if imagen and imagen.filename != '':
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_path = f"uploads/{filename}"
        else:
            imagen_path = None

        # Asegúrate de usar el campo correcto en la base de datos
        cursor.execute('INSERT INTO huertas (nombre, descripcion, imagen_path) VALUES (%s, %s, %s)',
                       (nombre, descripcion, imagen_path))
        mysql.connection.commit()
        flash('Huerta añadida exitosamente', 'success')
        return redirect(url_for('gestionar_huertos'))

    cursor.execute('SELECT * FROM huertas')
    huertas = cursor.fetchall()
    return render_template('gestionar_huertos.html', huertas=huertas)


@app.route('/huertos/delete/<int:id>', methods=['POST'])
def delete_huerto(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM huertas WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Huerto eliminada exitosamente', 'success')
    return redirect(url_for('gestionar_huertos'))

@app.route('/huertos/edit/<int:id>', methods=['POST'])
def edit_huerto(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    cursor.execute('UPDATE huertas SET nombre = %s, descripcion = %s WHERE id = %s', 
                   (nombre, descripcion, id))
    mysql.connection.commit()
    flash('Huerta actualizada exitosamente', 'success')
    return redirect(url_for('gestionar_huertos'))

@app.route('/inicio2')
def inicio2():
    return render_template('inicio2.html')

@app.route('/admin/usuarios')
def admin_usuario():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/plantas')
def admin_plantas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM plantas')
    plantas = cursor.fetchall()
    return render_template('admin_plantas.html', plantas=plantas)

@app.route('/admin/herramientas')
def admin_herramientas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM herramientas')
    herramientas = cursor.fetchall()
    return render_template('admin_herramientas.html', herramientas=herramientas)

@app.route('/admin/articulos')
def admin_articulos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM articulos')
    articulos = cursor.fetchall()
    return render_template('admin_articulos.html', articulos=articulos)

@app.route('/admin/huertos')
def admin_huertos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM huertas')
    huertas = cursor.fetchall()
    return render_template('admin_huertos.html', huertas=huertas)

@app.route('/admin/citas')
def admin_citas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM citas')
    citas = cursor.fetchall()
    return render_template('admin_citas.html', citas=citas)

@app.route('/admin/foro')
def admin_foro():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM foro')
    foro = cursor.fetchall()
    return render_template('admin_foro.html', foro=foro)

if __name__ == '__main__':
    app.run(port=3000, debug=True)

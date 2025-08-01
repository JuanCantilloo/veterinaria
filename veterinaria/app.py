from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import pymysql.cursors
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['UPLOAD_FOLDER'] = 'static/img'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def connect_to_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='veterinaria',
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True
    )


@app.route('/')
def inicio():
    return render_template('index.html')




@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, telefono, direccion) VALUES (%s, %s, %s)",
                    (nombre, telefono, direccion))
        conn.commit()
        cur.close()
        conn.close()
        flash('Usuario registrado.')
        return redirect(url_for('listar_usuarios'))
    return render_template('registrar_usuario.html')





@app.route('/listar_usuarios')
def listar_usuarios():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('listar_usuarios.html', usuarios=usuarios)





@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    conn = connect_to_db()
    cur = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        cur.execute("UPDATE usuarios SET nombre=%s, telefono=%s, direccion=%s WHERE id=%s",
                    (nombre, telefono, direccion, id))
        conn.commit()
        flash('Usuario actualizado.')
        return redirect(url_for('listar_usuarios'))
    cur.execute("SELECT * FROM usuarios WHERE id=%s", (id,))
    usuario = cur.fetchone()
    return render_template('editar_usuario.html', usuario=usuario)





@app.route('/eliminar_usuario/<int:id>')
def eliminar_usuario(id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    flash('Usuario eliminado.')
    return redirect(url_for('listar_usuarios'))




@app.route('/registrar_mascota', methods=['GET', 'POST'])
def registrar_mascota():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form.get('tipo')
        if not tipo:
            # Manejar el error, por ejemplo:
            flash('El campo tipo es obligatorio.')
            return redirect(request.url)
        raza = request.form['raza']
        fecha_nacimiento = request.form['fecha_nacimiento']
        peso = request.form['peso']
        color = request.form['color']
        fecha_ingreso = request.form['fecha_ingreso']
        usuario_id = request.form['usuario_id']
        foto = request.files['foto']


        if foto and allowed_file(foto.filename):
            filename = foto.filename
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto_path = filename
        else:
            foto_path = None

            
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO mascotas (nombre,tipo, raza, fecha_nacimiento, peso, color, fecha_ingreso, usuario_id, foto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre,tipo, raza, fecha_nacimiento, peso, color, fecha_ingreso, usuario_id, foto_path))
        conn.commit()
        cur.close()
        conn.close()
        flash('Mascota registrada.')
        return redirect(url_for('listar_mascotas'))
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('registrar_mascota.html', usuarios=usuarios)




@app.route('/listar_mascotas')
def listar_mascotas():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT mascotas.*, usuarios.nombre AS propietario 
        FROM mascotas 
        JOIN usuarios ON mascotas.usuario_id = usuarios.id
    """)
    mascotas = cur.fetchall()
    return render_template('listar_mascotas.html', mascotas=mascotas)




@app.route('/detalle_mascota/<int:id>')
def detalle_mascota(id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT mascotas.*, usuarios.nombre AS propietario 
        FROM mascotas 
        JOIN usuarios ON mascotas.usuario_id = usuarios.id
        WHERE mascotas.id = %s
    """, (id,))
    mascota = cur.fetchone()
    return render_template('detalle_mascota.html', mascota=mascota)




@app.route('/editar_mascota/<int:id>', methods=['GET', 'POST'])
def editar_mascota(id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM usuarios")
    usuarios = cur.fetchall()
    if request.method == 'POST':
        data = request.form
        cur.execute("""
            UPDATE mascotas SET nombre=%s, raza=%s, fecha_nacimiento=%s, peso=%s,
            color=%s, fecha_ingreso=%s, usuario_id=%s WHERE id=%s
        """, (data['nombre'], data['raza'], data['fecha_nacimiento'], data['peso'],
              data['color'], data['fecha_ingreso'], data['usuario_id'], id))
        conn.commit()
        flash('Mascota actualizada.')
        return redirect(url_for('listar_mascotas'))
    cur.execute("SELECT * FROM mascotas WHERE id=%s", (id,))
    mascota = cur.fetchone()
    return render_template('editar_mascota.html', mascota=mascota, usuarios=usuarios)





@app.route('/eliminar_mascota/<int:id>')
def eliminar_mascota(id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM mascotas WHERE id = %s", (id,))
    conn.commit()
    flash('Mascota eliminada.')
    return redirect(url_for('listar_mascotas'))





@app.route('/adoptar_mascota/<int:id>', methods=['POST'])
def adoptar_mascota(id):
    from datetime import date
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO mascotas_adoptadas (mascota_id, fecha_adopcion) VALUES (%s, %s)", (id, date.today()))
    conn.commit()
    flash('Mascota marcada como adoptada.')
    return redirect(url_for('listar_adoptadas'))




@app.route('/mascotas_adoptadas')
def listar_adoptadas():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, u.nombre AS propietario, a.fecha_adopcion
        FROM mascotas_adoptadas a
        JOIN mascotas m ON a.mascota_id = m.id
        JOIN usuarios u ON m.usuario_id = u.id
    """)
    mascotas = cur.fetchall()
    return render_template('listar_adoptadas.html', mascotas=mascotas)

@app.route('/info_mascota/<int:id>')
def info_mascota(id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT mascotas.*, usuarios.nombre AS propietario 
        FROM mascotas 
        JOIN usuarios ON mascotas.usuario_id = usuarios.id
        WHERE mascotas.id = %s
    """, (id,))
    mascota = cur.fetchone()
    if not mascota:
        flash('Mascota no encontrada.')
        return redirect(url_for('listar_mascotas'))
    return render_template('Info_mascota.html', mascota=mascota)





if __name__ == '__main__':
    app.run(debug=True)

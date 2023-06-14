from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5433/perpustakaan'
db = SQLAlchemy(app)

class Pengguna(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String())
    jenis_kelamin = db.Column(db.String())
    kontak = db.Column(db.String())
    alamat = db.Column(db.String())
    tipe = db.Column(db.String())
    # relation_kelas_ampu = db.relationship('KelasAmpu', backref='mahasiswa', lazy='dynamic')

    def __init__(self, nama, jenis_kelamin, kontak, alamat, tipe):
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.kontak = kontak
        self.alamat = alamat
        self.tipe = tipe

    def __repr__(self):
        return f'<Pengguna {self.nama}, tipe: {self.tipe}>'

class Penulis(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String())
    kewarganegaraan = db.Column(db.String())
    # relation_kelas_ampu = db.relationship('KelasAmpu', backref='mahasiswa', lazy='dynamic')

    def __init__(self, nama, jenis_kelamin, kewarganegaraan):
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.kewarganegaraan = kewarganegaraan

    def __repr__(self):
        return f'<Penulis {self.nama}'

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String())
    # relation_kelas_ampu = db.relationship('KelasAmpu', backref='mahasiswa', lazy='dynamic')

    def __init__(self, nama, jenis_kelamin, kewarganegaraan):
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin

    def __repr__(self):
        return f'<Genre {self.nama}'

class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    judul = db.Column(db.String())
    id_penulis = db.Column(db.Integer, unique=True, nullable=False)
    tanggal_terbit = db.Column(db.Date)
    # relation_kelas_ampu = db.relationship('KelasAmpu', backref='mahasiswa', lazy='dynamic')

    def __init__(self, judul, id_penulis, tanggal_terbit):
        self.judul = judul
        self.id_penulis = id_penulis
        self.tanggal_terbit = tanggal_terbit

    def __repr__(self):
        return f'<Buku {self.judul}'

@app.get('/')
def login():
    auth = request.headers.get('Authorization')
    auth_type, code = auth.split(' ')
    decoded_string = (base64.b64decode(code).decode())
    username, password = decoded_string.split(':')

    try:
        user = Pengguna.query.get(username)

        if user.tipe == 'pustakawan':                   # AUTH:
            return 'pustakawan'                         # N/A
        elif user.tipe == 'anggota':                    # N/A 
            return 'anggota'                            # N/A
    except:
        return {
            'error': '404 Not Found',
            'message': 'User tidak dikenali'
        }

@app.get('/pengguna')
def getUser():
    data = Pengguna.query.all()
    response = [
        {
            'id':p.id,
            'nama':p.nama,
            'jenis_kelamin':p.jenis_kelamin,
            'kontak':p.kontak,
            'alamat':p.alamat,
            'tipe':p.tipe
        } for p in data
    ]
    return {'count': len(response), 'data':response}

@app.post('/pengguna')
def addUser():
    if login() == 'pustakawan':
        data = request.get_json()
        new_user = Pengguna(
            data.get('nama'),
            data.get('jenis_kelamin'),
            data.get('kontak'),
            data.get('alamat'),
            data.get('tipe')
        )
        db.session.add(new_user)
        db.session.commit()
        return {"message":f"Mahasiswa {new_user.nama} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.route('/pengguna/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handlePengguna(id):
    user = Pengguna.query.get(id)

    if request.method == 'GET':
        response = {
            'id':user.id,
            'nama':user.nama,
            'jenis_kelamin':user.jenis_kelamin,
            'kontak':user.kontak,
            'alamat':user.alamat,
            'tipe':user.tipe
        }
        return {'message':'success', 'data':response}
    
    if login() == 'pustakawan':
        if request.method == 'PUT':
            data = request.get_json()
            user.nama = data.get('nama')
            user.jenis_kelamin = data.get('jenis_kelamin')
            user.kontak = data.get('kontak')
            user.alamat = data.get('alamat')
            user.tipe = data.get('tipe')
            db.session.add(user)
            db.session.commit()
            return {'message': f'Pengguna {user.nama} berhasil diupdate'}
        
        elif request.method == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            return {'message': f'Pengguna {user.nama} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

if __name__ == '__main__':
	app.run(debug=True)
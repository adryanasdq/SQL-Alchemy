from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
# import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5433/perpustakaan'
db = SQLAlchemy(app)

class Pengguna(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    nama = db.Column(db.String())
    kontak = db.Column(db.String())
    tipe = db.Column(db.String())
    relation_transaksi = db.relationship('Transaksi', backref='pengguna', lazy='dynamic')

    def __init__(self, email, password, nama, kontak, tipe):
        self.email = email
        self.password =password
        self.nama = nama
        self.kontak = kontak
        self.tipe = tipe

    def __repr__(self):
        return f'<Pengguna {self.nama}, tipe: {self.tipe}>'


class Penulis(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String())
    kewarganegaraan = db.Column(db.String())

    def __init__(self, nama, kewarganegaraan):
        self.nama = nama
        self.kewarganegaraan = kewarganegaraan

    def __repr__(self):
        return f'<Penulis {self.nama}>'


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String())

    def __init__(self, nama):
        self.nama = nama

    def __repr__(self):
        return f'<Genre {self.nama}>'


class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    judul = db.Column(db.String())
    id_penulis = db.Column(db.Integer, unique=True, nullable=False)
    tanggal_terbit = db.Column(db.Date)
    relation_transaksi = db.relationship('Transaksi', backref='buku', lazy='dynamic')

    def __init__(self, judul, id_penulis, tanggal_terbit):
        self.judul = judul
        self.id_penulis = id_penulis
        self.tanggal_terbit = tanggal_terbit

    def __repr__(self):
        return f'<Buku {self.judul}'


class GenreBuku(db.Model):
    __tablename__ = 'genre_buku'

    id_buku = db.Column(db.Integer, db.ForeignKey('buku.id'), primary_key=True, nullable=False)
    id_genre = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)

    def __init__(self, id_buku, id_genre):
        self.id_buku = id_buku
        self.id_genre = id_genre


class Transaksi(db.Model):
    id_buku = db.Column(db.Integer, db.ForeignKey('buku.id'), primary_key=True, unique=True, nullable=False)
    id_pengguna = db.Column(db.Integer, db.ForeignKey('pengguna.id'), primary_key=True, unique=True, nullable=False)
    status = db.Column(db.String(), nullable=False)
    penerima_permintaan = db.Column(db.String(), nullable=False)
    tanggal_diterima = db.Column(db.Date, nullable=False)
    penerima_pengembalian = db.Column(db.String(), nullable=False)
    tanggal_dikembalikan = db.Column(db.Date, nullable=False)

    def __init__(self, id_buku, id_pengguna, status, penerima_permintaan, tanggal_diterima, penerima_pengembalian, tanggal_dikembalikan):
        self.id_buku = id_buku
        self.id_pengguna = id_pengguna
        self.status = status
        self.penerima_permintaan = penerima_permintaan
        self.tanggal_diterima = tanggal_diterima
        self.penerima_pengembalian = penerima_pengembalian
        self.tanggal_dikembalikan = tanggal_dikembalikan
    
    def __repr__(self):
        return f'<Transaksi {self.judul}'


# @app.get('/')
# def login():
#     auth = request.headers.get('Authorization')
#     auth_type, code = auth.split(' ')
#     decoded_string = (base64.b64decode(code).decode())
#     username, password = decoded_string.split(':')

#     try:
#         user = Pengguna.query.get(username)       # login pakai email dan password
#         key = Pengguna.query.get(password)

#         if user.tipe == 'pustakawan':             # AUTH:
#             return 'pustakawan'                   # N/A
#         elif user.tipe == 'anggota':              # N/A 
#             return 'anggota'                      # N/A
#     except:
#         return {
#             'error': '404 Not Found',
#             'message': 'User tidak dikenali'
#         }

@app.get('/pengguna')
def getPengguna():
    data = Pengguna.query.all()
    response = [
        {
            'id':p.id,
            'email':p.email,
            'nama':p.nama,
            'kontak':p.kontak,
            'tipe':p.tipe
        } for p in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/pengguna/<int:id>')
def getPenggunaSpesifik(id):
    user = Pengguna.query.get(id)
    response = {
        'id':user.id,
        'email':user.email,
        'nama':user.nama,
        'kontak':user.kontak,
        'tipe':user.tipe
    }
    return {'message':'success', 'response':response}

@app.post('/pengguna')
def addPengguna():
    # if login() == 'pustakawan':
    data = request.get_json()
    new_user = Pengguna(
        data.get('email'),
        data.get('password'),
        data.get('nama'),
        data.get('kontak'),
        data.get('tipe', 'anggota')
    )
    db.session.add(new_user)
    db.session.commit()
    return {"message":f"Pengguna {new_user.nama} ditambahkan"}
    # else:
    #     return {
    #         'error': 'Unauthorized',
    #         'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
    #     }

@app.put('/pengguna/<int:id>')
def updatePengguna(id):
    user = Pengguna.query.get(id)

    # if login() == 'pustakawan':
    data = request.get_json()
    user.email = data.get('email')
    user.password = data.get('password')
    user.nama = data.get('nama')
    user.kontak = data.get('kontak')
    user.tipe = data.get('tipe')

    db.session.add(user)
    db.session.commit()
    return {'message': f'Pengguna {user.nama} berhasil diupdate'}
    # else:
    #     return {
    #         'error': 'Unauthorized',
    #         'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
    #     }

@app.delete('/pengguna/<int:id>')
def deletePengguna(id):
    user = Pengguna.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return {'message': f'Pengguna {user.nama} berhasil dihapus'}


@app.get('/penulis')
def getPenulis():
    data = Penulis.query.all()
    response = [
        {
            'id':p.id,
            'nama':p.nama,
            'kewarganegaraan':p.kewarganegaraan
        } for p in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/penulis/<int:id>')
def getPenulisSpesifik(id):
    author = Penulis.query.get(id)
    response = {
        'id':author.id,
        'nama':author.nama,
        'tipe':author.kewarganegaraan
    }
    return {'message':'success', 'response':response}


@app.get('/genre')
def getGenre():
    data = Genre.query.all()
    response = [
        {
            'id':g.id,
            'nama':g.nama
        } for g in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/genre/<int:id>')
def getGenreSpesifik(id):
    genre = Genre.query.get(id)
    response = {
        'id':genre.id,
        'nama':genre.nama
    }
    return {'message':'success', 'response':response}


@app.get('/buku')
def getBuku():
    data = Buku.query.all()
    response = [
        {
            'id':b.id,
            'judul':b.judul,
            'id_penulis':b.id_penulis,
            'tanggal_terbit':b.tanggal_terbit
        } for b in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/buku/<int:id>')
def getBukuSpesifik(id):
    buku = Buku.query.get(id)
    response = {
        'id':buku.id,
        'judul':buku.judul,
        'id_penulis':buku.id_penulis,
        'tanggal_terbit':buku.tanggal_terbit
    }
    return {'message':'success', 'response':response}


@app.get('/genrebuku')
def getGenreBuku():
    data = GenreBuku.query.all()
    response = [
        {
            'id_buku':gb.id_buku,
            'id_genre':gb.id_genre
        } for gb in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/genrebuku/<int:id>')
def getGenreBukuSpesifik(id):
    # genrebuku = db.session.get(GenreBuku, id)
    genrebuku = GenreBuku.query.filter_by(id_buku=id).first()
    response = {
        'id_buku':genrebuku.id_buku,
        'id_genre':genrebuku.id_genre               # hanya hasil teratas
    }
    return {'message':'success', 'response':response}


if __name__ == '__main__':
	app.run(debug=True)
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5433/perpustakaan'
db = SQLAlchemy(app)

class Pengguna(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    nama = db.Column(db.String)
    kontak = db.Column(db.String)
    tipe = db.Column(db.String)
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
    nama = db.Column(db.String)
    kewarganegaraan = db.Column(db.String)

    def __init__(self, nama, kewarganegaraan):
        self.nama = nama
        self.kewarganegaraan = kewarganegaraan

    def __repr__(self):
        return f'<Penulis {self.nama}>'


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String)

    def __init__(self, nama):
        self.nama = nama

    def __repr__(self):
        return f'<Genre {self.nama}>'


class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    judul = db.Column(db.String)
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
    id_genre = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True, nullable=False)

    def __init__(self, id_buku, id_genre):
        self.id_buku = id_buku
        self.id_genre = id_genre


class Transaksi(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_buku = db.Column(db.Integer, db.ForeignKey('buku.id'), nullable=False)
    id_pengguna = db.Column(db.Integer, db.ForeignKey('pengguna.id'), nullable=False)
    status = db.Column(db.String, nullable=False)
    tanggal_permintaan = db.Column(db.DateTime, nullable=True)
    penerima_permintaan = db.Column(db.String, nullable=True)
    tanggal_diterima = db.Column(db.DateTime, nullable=True)
    penerima_pengembalian = db.Column(db.String, nullable=True)
    tanggal_dikembalikan = db.Column(db.DateTime, nullable=True)

    def __init__(self, id_buku, id_pengguna, status, tanggal_permintaan, penerima_permintaan, tanggal_diterima, penerima_pengembalian, tanggal_dikembalikan):
        self.id_buku = id_buku
        self.id_pengguna = id_pengguna
        self.status = status
        self.tanggal_permintaan = tanggal_permintaan
        self.penerima_permintaan = penerima_permintaan
        self.tanggal_diterima = tanggal_diterima
        self.penerima_pengembalian = penerima_pengembalian
        self.tanggal_dikembalikan = tanggal_dikembalikan
    
    def __repr__(self):
        return f'<Transaksi {self.id}'


# _________________________________________________________________________
@app.get('/')
def login():
    username = request.authorization.get('username')
    password = request.authorization.get('password')

    try:
        user = Pengguna.query.filter_by(email=username).first_or_404()
    except:
        return {
            'error': '404 Not Found',
            'message': 'User tidak dikenali'
        }

    if user.password == password:
        if user.tipe == 'pustakawan':             # AUTH:
            return 'pustakawan'                   # N/A
        elif user.tipe == 'anggota':              # N/A 
            return 'anggota'                      # N/A
    else:
        return 'Password salah!'

# _________________________________________________________________________
@app.get('/pengguna')
def getPengguna():
    data = Pengguna.query.all()
    response = [
        {
            'id':p.id,
            'nama':p.nama,
            'tipe':p.tipe
        } for p in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/pengguna/<int:id>')
def getDetailPengguna(id):
    if login() == 'pustakawan':
        user = Pengguna.query.get(id)
        response = {
            'id':user.id,
            'email':user.email,
            'nama':user.nama,
            'kontak':user.kontak,
            'tipe':user.tipe
        }
        return {'message':'success', 'response':response}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.post('/pengguna')
def addPengguna():
    if login() == 'pustakawan':
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
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.put('/pengguna/<int:id>')
def updatePengguna(id):
    if login() == 'pustakawan':
        user = Pengguna.query.get(id)
        data = request.get_json()

        user.email = data.get('email')
        user.password = data.get('password')
        user.nama = data.get('nama')
        user.kontak = data.get('kontak')
        user.tipe = data.get('tipe')

        db.session.add(user)
        db.session.commit()
        return {'message': f'Pengguna {user.nama} berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.delete('/pengguna/<int:id>')
def deletePengguna(id):
    if login() == 'pustakawan':
        user = Pengguna.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return {'message': f'Pengguna {user.nama} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

# _______________________________________________________________________
@app.get('/penulis')
def getPenulis():
    data = Penulis.query.all()
    response = [
        {
            'id':p.id,
            'nama':p.nama
        } for p in data
    ]
    return {'count': len(response), 'data':response}

@app.get('/penulis/<int:id>')           # tambahkan si penulis sudah nulis buku apa saja
def getDetailPenulis(id):
    author = Penulis.query.get(id)
    response = {
        'id':author.id,
        'nama':author.nama,
        'kewarganegaraan':author.kewarganegaraan
    }
    return {'message':'success', 'response':response}

@app.post('/penulis')
def addPenulis():
    if login() == 'pustakawan':
        data = request.get_json()
        new_author = Penulis(
            data.get('nama'),
            data.get('kewarganegaraan')
        )
        db.session.add(new_author)
        db.session.commit()
        return {"message":f"Penulis {new_author.nama} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.put('/penulis/<int:id>')
def updatePenulis(id):
    if login() == 'pustakawan':
        author = Penulis.query.get(id)

        data = request.get_json()
        author.nama = data.get('nama')
        author.kewarganegaraan = data.get('kewarganegaraan')

        db.session.add(author)
        db.session.commit()
        return {'message': f'Penulis {author.nama} berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.delete('/penulis/<int:id>')
def deletePenulis(id):
    if login() == 'pustakawan':
        author = Penulis.query.get(id)
        db.session.delete(author)
        db.session.commit()
        return {'message': f'Penulis {author.nama} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

# _______________________________________________________________________
@app.get('/genre')
def getGenre():
    data = Genre.query.all()
    response = [g.nama for g in data]
    return {'count': len(response), 'data':response}

@app.get('/genre/<int:id>')
def getDetailGenre(id):
    genre = Genre.query.get(id)
    response = {
        'id':genre.id,
        'nama':genre.nama
    }
    return {'message':'success', 'response':response}

@app.post('/genre')
def addGenre():
    if login() == 'pustakawan':
        data = request.get_json()
        new_genre = Genre(
            data.get('nama')
        )
        db.session.add(new_genre)
        db.session.commit()
        return {"message":f"Genre {new_genre.nama} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.put('/genre/<int:id>')
def updateGenre(id):
    if login() == 'pustakawan':
        genre = Genre.query.get(id)

        data = request.get_json()
        genre.nama = data.get('nama')

        db.session.add(genre)
        db.session.commit()
        return {'message': f'Genre {genre.nama} berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.delete('/genre/<int:id>')
def deleteGenre(id):
    if login() == 'pustakawan':
        genre = Genre.query.get(id)
        db.session.delete(genre)
        db.session.commit()
        return {'message': f'Genre {genre.nama} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

# _____________________________________________________________________
@app.get('/buku')                       # buat jadi tampilkan judul, nama penulis, genre
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

@app.get('/buku/<int:id>')              # tambahkan nama penulis, genre
def getDetailBuku(id):
    buku = Buku.query.get(id)
    response = {
        'id':buku.id,
        'judul':buku.judul,
        'id_penulis':buku.id_penulis,
        'tanggal_terbit':buku.tanggal_terbit
    }
    return {'message':'success', 'response':response}

@app.post('/buku')
def addBuku():
    if login() == 'pustakawan':
        data = request.get_json()
        new_buku = Buku(
            data.get('judul'),
            data.get('id_penulis'),
            data.get('tanggal_terbit')
        )
        db.session.add(new_buku)
        db.session.commit()
        return {"message":f"Buku {new_buku.judul} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.put('/buku/<int:id>')
def updateBuku(id):
    if login() == 'pustakawan':
        buku = Buku.query.get(id)

        data = request.get_json()
        buku.judul = data.get('judul')
        buku.id_penulis = data.get('id_penulis')
        buku.tanggal_terbit = data.get('tanggal_terbit')

        db.session.add(buku)
        db.session.commit()
        return {'message': f'buku {buku.judul} berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.delete('/buku/<int:id>')
def deleteBuku(id):
    if login() == 'pustakawan':
        buku = Buku.query.get(id)
        db.session.delete(buku)
        db.session.commit()
        return {'message': f'Buku {buku.judul} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

#_____________________________________________________________________
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

@app.get('/genrebuku/<int:id>')         # hanya hasil teratas, harusnya semua genre dari buku tersebut
def getDetailGenreBuku(id):
    genrebuku = GenreBuku.query.filter_by(id_buku=id).first()
    response = {
        'id_buku':genrebuku.id_buku,
        'id_genre':genrebuku.id_genre               
    }
    return {'message':'success', 'response':response}

@app.post('/genrebuku')                 # return Genre Buku {judul} ditambahkan
def addGenreBuku():
    if login() == 'pustakawan':
        data = request.get_json()
        new_genre_buku = GenreBuku(
            data.get('id_buku'),
            data.get('id_genre')
        )
        db.session.add(new_genre_buku)
        db.session.commit()
        return {"message":f"Genre Buku {new_genre_buku.id_buku} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.put('/genrebuku/<int:id>')         # ??
def updateGenreBuku(id):
    if login() == 'pustakawan':
        genrebuku = GenreBuku.query.get(id)

        data = request.get_json()
        genrebuku.id_buku = data.get('id_buku')
        genrebuku.id_genre = data.get('id_genre')

        db.session.add(genrebuku)
        db.session.commit()
        return {'message': f'Genre Buku {genrebuku.judul} berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.delete('/genrebuku/<int:id>')
def deleteGenreBuku(id):
    if login() == 'pustakawan':
        genrebuku = GenreBuku.query.get(id)
        db.session.delete(genrebuku)
        db.session.commit()
        return {'message': f'Genre Buku {genrebuku.judul} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

# ___________________________________________________________________________
@app.get('/transaksi')
def getTransaksi():
    if login() == 'pustakawan':
        data = Transaksi.query.all()            # Ganti jadi judul buku
        response = [
            {
                'id':t.id,
                'id_buku':t.id_buku,
                'status':t.status
            } for t in data
        ]
        return {'count': len(response), 'data':response}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.get('/transaksi/<int:id>')         # buat hanya pustakawan dan pemilik transaksi yang bisa lihat
def getDetailTransaksi(id):
    if login() == 'pustakawan':
        transaksi = Transaksi.query.filter_by(id=id).first()
        response = {
            'id':transaksi.id,
            'id_buku':transaksi.id_buku,
            'id_pengguna':transaksi.id_pengguna,
            'status':transaksi.status,
            'pustakawan':{
                'permintaan':transaksi.penerima_permintaan,
                'pengembalian':transaksi.penerima_pengembalian
            },
            'tanggal_transaksi':{
                'permintaan':transaksi.tanggal_permintaan,
                'diterima':transaksi.tanggal_diterima,
                'dikembalikan':transaksi.tanggal_dikembalikan
            }
        }
        return {'message':'success', 'response':response}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.post('/transaksi')                 # Perbaiki returnnya
def addTransaksi():
    if login() == 'anggota':
        username = request.authorization.get('username')
        pengguna = Pengguna.query.filter_by(email=username).first_or_404()

        data = request.get_json()
        new_trans = Transaksi(
            data.get('id_buku'),
            pengguna.id,
            'diminta',
            date.today(),
            None,
            None,
            None,
            None
        )
        db.session.add(new_trans)
        db.session.commit()
        return {"message":f"Transaksi {new_trans.id_pengguna} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya anggota yang boleh melakukan operasi ini'
        }

@app.put('/transaksi/<int:id>/peminjaman')
def approveBuku(id):
    if login() == 'pustakawan':
        username = request.authorization.get('username')
        pengguna = Pengguna.query.filter_by(email=username).first_or_404()
        transaksi = Transaksi.query.get(id)

        data = request.get_json()
        transaksi.status = data.get('status')
        transaksi.penerima_permintaan = pengguna.id
        transaksi.tanggal_diterima = date.today()

        db.session.add(transaksi)
        db.session.commit()
        return {'message': f'Transaksi berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.put('/transaksi/<int:id>/pengembalian')
def returnBuku(id):
    if login() == 'pustakawan':
        username = request.authorization.get('username')
        pengguna = Pengguna.query.filter_by(email=username).first_or_404()
        transaksi = Transaksi.query.get(id)

        data = request.get_json()
        transaksi.status = data.get('status')
        transaksi.penerima_pengembalian = pengguna.id
        transaksi.tanggal_dikembalikan = date.today()

        db.session.add(transaksi)
        db.session.commit()
        return {'message': f'Transaksi berhasil diupdate'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }

@app.delete('/transaksi/<int:id>')
def deleteTransaksi(id):
    if login() == 'pustakawan':
        transaksi = Transaksi.query.get(id)
        db.session.delete(transaksi)
        db.session.commit()
        return {'message': f'Transaksi {transaksi.id_pengguna} untuk {transaksi.id_buku} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya pustakawan yang boleh melakukan operasi ini'
        }


if __name__ == '__main__':
	app.run(debug=True)
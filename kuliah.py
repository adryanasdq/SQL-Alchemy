from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5433/exercise'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Mahasiswa(db.Model):
    __tablename__ = 'mahasiswa'

    nim = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String())
    gender = db.Column(db.String())
    kontak = db.Column(db.String())
    email = db.Column(db.String())
    relation_kelas_ampu = db.relationship('KelasAmpu', backref='mahasiswa', lazy='dynamic')

    def __init__(self, nama, gender, kontak, email):
        self.nama = nama
        self.gender = gender
        self.kontak = kontak
        self.email = email

    def __repr__(self):
        return f'<Mahasiswa {self.nama}>'


class Matkul(db.Model):
    __tablename__ = 'mata_kuliah'

    kode_mk = db.Column(db.String(), primary_key=True)
    nama_mk = db.Column(db.String())
    sks = db.Column(db.Integer)
    relation_kelas = db.relationship('RuangKelas', backref='mk', lazy='dynamic')

    def __init__(self, kode_mk, nama_mk, sks):
        self.kode_mk = kode_mk
        self.nama_mk = nama_mk
        self.sks = sks
    
    def __repr__(self):
        return f'<Mata Kuliah {self.nama_mk}>'


class Dosen(db.Model):
    __tablename__ = 'dosen'

    nip_dosen = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String())
    gender = db.Column(db.String())
    kontak = db.Column(db.String)
    email = db.Column(db.String)
    relation_kelas = db.relationship('RuangKelas', backref='dosen', lazy='dynamic')

    def __init__(self, nip_dosen, nama, gender, kontak, email):
        self.nip_dosen = nip_dosen
        self.nama = nama
        self.gender = gender
        self.kontak = kontak
        self.email = email

    def __repr__(self):
        return f'<Dosen {self.nip_dosen}>'


class RuangKelas(db.Model):
    __tablename__ = 'ruang_kelas'

    kode_ruang_kelas = db.Column(db.String(5), primary_key=True)
    nama_ruang_kelas = db.Column(db.String(30))
    nip_dosen = db.Column(db.Integer, db.ForeignKey('dosen.nip_dosen'), nullable=False)
    kode_mk = db.Column(db.String(), db.ForeignKey('mata_kuliah.kode_mk'), nullable=False)
    jam = db.Column(db.Time)
    hari = db.Column(db.String(10))

    def __init__(self, kode_ruang_kelas, nama_ruang_kelas, nip_dosen, kode_mk, jam, hari):
        self.kode_ruang_kelas = kode_ruang_kelas
        self.nama_ruang_kelas = nama_ruang_kelas
        self.nip_dosen = nip_dosen
        self.kode_mk = kode_mk
        self.jam = jam
        self.hari = hari

    def __repr__(self):
        return f'<RuangKelas {self.nama_ruang_kelas}>'


class KelasAmpu(db.Model):
    __tablename__ = 'kelas_ampu'

    nim = db.Column(db.Integer, db.ForeignKey('mahasiswa.nim'), primary_key=True)
    kode_ruang_kelas = db.Column(db.String(), db.ForeignKey('ruang_kelas.kode_ruang_kelas'), primary_key=True)

    def __init__(self, nim, kode_ruang_kelas):
        self.nim = nim
        self.kode_ruang_kelas = kode_ruang_kelas


@app.get('/')
def login():
    auth = request.headers.get('Authorization')
    auth_type, code = auth.split(' ')
    decoded_string = (base64.b64decode(code).decode())
    username, password = decoded_string.split(':')

    try:
        mhs = Mahasiswa.query.get(username)
        dsn = Dosen.query.get(username)

        if mhs:                 # AUTH:
            return 'mahasiswa'  # Siapapun bisa get info 
        elif dsn:               # Mahasiswa hanya bisa enroll/update/unroll kelas ampu, dosen tidak bisa
            return 'dosen'      # Dosen bisa mendaftarkan mahasiswa baru, update, atau DO; edit matkul; edit dosen; dan edit ruang kelas
    except:
        return {
            'error': 'Unknown User',
            'message': 'User tidak dikenali'
        }

@app.get('/mahasiswa')
def getMahasiswa():
    datamahasiswa = Mahasiswa.query.all()
    response = [
        {
            'nim':m.nim,
            'nama':m.nama,
            'gender':m.gender,
            'kontak':m.kontak,
            'email':m.email
        } for m in datamahasiswa
    ]
    return {'count': len(response), 'mahasiswa':response}

@app.post('/mahasiswa')
def addMahasiswa():
    if login() == 'dosen':
        data = request.get_json()
        new_mhs = Mahasiswa(
            data.get('nama'),
            data.get('gender'),
            data.get('kontak'),
            data.get('email')
        )
        db.session.add(new_mhs)
        db.session.commit()
        return {"message":f"Mahasiswa {new_mhs.nama} ditambahkan"}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.route('/mahasiswa/<nim>', methods=['GET', 'PUT', 'DELETE'])
def handleMahasiswa(nim):
    if login() == 'dosen':
        mhs = Mahasiswa.query.get_or_404(nim)

        if request.method == 'GET':
            response = {
                'nim':mhs.nim,
                'nama':mhs.nama,
                'gender':mhs.gender,
                'kontak':mhs.kontak,
                'email':mhs.email
            }
            return {'message':'success', 'data':response}
        
        elif request.method == 'PUT':
            data = request.get_json()
            mhs.nim = data.get('nim')
            mhs.nama = data.get('nama')
            mhs.gender = data.get('gender')
            mhs.kontak = data.get('kontak')
            mhs.email = data.get('email')
            db.session.add(mhs)
            db.session.commit()
            return {'message': f'Mahasiswa {mhs.nama} berhasil diupdate'}
        
        elif request.method == 'DELETE':
            db.session.delete(mhs)
            db.session.commit()
            return {'message': f'Mahasiswa {mhs.nama} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.get('/matakuliah')
def getMatkul():
    datamatkul = Matkul.query.all()
    response = [
        {
            'kode_mk': dm.kode_mk,
            'nama_mk': dm.nama_mk,
            'sks': dm.sks
        } for dm in datamatkul
    ]
    return {'count': len(response), 'matakuliah':response}

@app.post('/matakuliah')
def addMatkul():
    if login() == 'dosen':
        data = request.get_json()
        new_matkul = Matkul(
            data.get('kode_mk'),
            data.get('nama_mk'),
            data.get('sks')
        )
        db.session.add(new_matkul)
        db.session.commit()
        return {'message':f'Matkul {new_matkul.nama_mk} ditambahkan'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.route('/matakuliah/<kode_mk>', methods=['GET', 'PUT', 'DELETE'])
def handleMatkul(kode_mk):
    if login() == 'dosen':
        mk = Matkul.query.get_or_404(kode_mk)

        if request.method == 'GET':
            response = {
                'kode_mk': mk.kode_mk,
                'nama_mk': mk.nama_mk,
                'sks': mk.sks
            }
            return {'message': 'success', 'data': response}
        
        elif request.method == 'PUT':
            data = request.get_json()
            mk.kode_mk = data.get('kode_mk')
            mk.nama_mk = data.get('nama_mk')
            mk.sks = int(data.get('sks'))
            db.session.add(mk)
            db.session.commit()
            return {'message': f'Matkul {mk.nama_mk} berhasil diupdate'}
        
        elif request.method == 'DELETE':
            db.session.delete(mk)
            db.session.commit()
            return {'message': f'Matkul {mk.nama_mk} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.get('/dosen')
def getDosen():
    if login() == 'dosen':
        dataDosen = Dosen.query.all()
        response = [
            {
                'nip_dosen':dd.nip_dosen,
                'nama':dd.nama,
                'gender':dd.gender,
                'kontak':dd.kontak,
                'email':dd.email
            } for dd in dataDosen]
        
        return {'count': len(response), 'mahasiswa':response}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.post('/dosen')
def addDosen():
    if login() == 'dosen':
        data = request.get_json()
        new_dosen = Dosen(
            data.get('nip_dosen'),
            data.get('nama'),
            data.get('gender'),
            data.get('kontak'),
            data.get('email')
        )
        db.session.add(new_dosen)
        db.session.commit()
        return {'message':f'Dosen {new_dosen.nama} ditambahkan'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.route('/dosen/<nip_dosen>', methods=['GET', 'PUT', 'DELETE'])
def handleDosen(nip_dosen):
    if login() == 'dosen':
        dsn = Dosen.query.get_or_404(nip_dosen)

        if request.method == 'GET':
            response = {
                'nip_dosen': dsn.nip_dosen,
                'nama': dsn.nama,
                'gender': dsn.gender,
                'kontak': dsn.kontak,
                'email': dsn.email
            }
            return {'message': 'success', 'data': response}
        
        elif request.method == 'PUT':
            data = request.get_json()
            dsn.nip_dosen = int(data.get('nip_dosen'))
            dsn.nama = data.get('nama')
            dsn.gender = data.get('gender')
            dsn.kontak = data.get('kontak')
            dsn.email = data.get('email')
            db.session.add(dsn)
            db.session.commit()
            return {'message': f'Dosen {dsn.nama} berhasil diupdate'}
        
        elif request.method == 'DELETE':
            db.session.delete(dsn)
            db.session.commit()
            return {'message': f'Dosen {dsn.nama} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.get('/ruangkelas')
def getKelas():
    datakelas = RuangKelas.query.all()
    response = [
        {
            'kode_ruang_kelas': dk.kode_ruang_kelas,
            'nama_ruang_kelas': dk.nama_ruang_kelas,
            'nip_dosen': dk.nip_dosen,
            'kode_mk': dk.kode_mk,
            'jam': str(dk.jam),
            'hari': dk.hari
        } for dk in datakelas]
    
    return {'count': len(response), 'ruangkelas': response}

@app.post('/ruangkelas')
def addRuangKelas():
    if login() == 'dosen':
        data = request.get_json()
        new_ruang_kelas = RuangKelas(
            data.get('kode_ruang_kelas'),
            data.get('nama_ruang_kelas'),
            int(data.get('nip_dosen')),
            data.get('kode_mk'),
            data.get('jam'),
            data.get('hari')
        )
        db.session.add(new_ruang_kelas)
        db.session.commit()
        return {'message':f'Ruang {new_ruang_kelas.nama_ruang_kelas} ditambahkan'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.route('/ruangkelas/<kode_ruang_kelas>', methods=['GET', 'PUT', 'DELETE'])
def handleRuangKelas(kode_ruang_kelas):
    if login() == 'dosen':
        rk = RuangKelas.query.get_or_404(kode_ruang_kelas)

        if request.method == 'GET':
            response = {
                'kode_ruang_kelas': rk.kode_ruang_kelas,
                'nama_ruang_kelas': rk.nama_ruang_kelas,
                'nip_dosen': rk.nip_dosen,
                'kode_mk': rk.kode_mk,
                'jam': str(rk.jam),
                'hari': rk.hari
            }
            return {'message': 'success', 'data': response}
        
        elif request.method == 'PUT':
            data = request.get_json()
            rk.kode_ruang_kelas = data.get('kode_ruang_kelas')
            rk.nama_ruang_kelas = data.get('nama_ruang_kelas')
            rk.nip_dosen = data.get('nip_dosen')
            rk.kode_mk = data.get('kode_mk')
            rk.jam = data.get('jam')
            rk.hari = data.get('hari')
            db.session.add(rk)
            db.session.commit()
            return {'message': f'Ruang kelas {rk.nama_ruang_kelas} berhasil diupdate'}
        
        elif request.method == 'DELETE':
            db.session.delete(rk)
            db.session.commit()
            return {'message': f'Ruang kelas {rk.nama_ruang_kelas} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya dosen yang boleh melakukan operasi ini'
        }

@app.get('/kelasampu')
def getAmpu():
    dataAmpu = KelasAmpu.query.all()
    response = [
        {
            'nim': da.nim,
            'kode_ruang_kelas': da.kode_ruang_kelas
        } for da in dataAmpu]
    
    return {'count': len(response), 'kelasampu': response}

@app.post('/kelasampu')
def addAmpu():
    if login() == 'mahasiswa':
        data = request.get_json()
        new_ampu = KelasAmpu(
            data.get('nim'),
            data.get('kode_ruang_kelas')
        )
        db.session.add(new_ampu)
        db.session.commit()
        return {'message':f'Kelas ampu {new_ampu.nim} ditambahkan'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya mahasiswa yang boleh melakukan operasi ini'
        }
    
@app.route('/kelasampu/<nim>', methods=['GET', 'PUT', 'DELETE'])
def handleAmpu(nim):
    if login() == 'mahasiswa':
        ampu = KelasAmpu.query.filter_by(nim=nim).first()

        if request.method == 'GET':
            response = {
                'nim': ampu.nim,
                'kode_ruang_kelas': ampu.kode_ruang_kelas,
                'nama': ampu.mahasiswa.nama
            }
            return {'message': 'success', 'data': response}
        
        elif request.method == 'PUT':
            data = request.get_json()
            ampu.nim = data.get('nim')
            ampu.kode_ruang_kelas = data.get('kode_ruang_kelas')
            db.session.add(ampu)
            db.session.commit()
            return {'message': f'Kelas ampu {ampu.nim} berhasil diupdate'}
        
        elif request.method == 'DELETE':
            db.session.delete(ampu)
            db.session.commit()
            return {'message': f'Kelas ampu {ampu.nim} berhasil dihapus'}
    else:
        return {
            'error': 'Unauthorized',
            'message': 'Hanya mahasiswa yang boleh melakukan operasi ini'
        }
    
if __name__ == '__main__':
	app.run(debug=True)
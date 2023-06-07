from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

    def __init__(self, kode_ruang_kelas, nama_ruang_kelas, jam, hari):
        self.kode_ruang_kelas = kode_ruang_kelas
        self.nama_ruang_kelas = nama_ruang_kelas
        self.jam = jam
        self.hari = hari

    def __repr__(self):
        return f'<RuangKelas {self.nama_ruang_kelas}>'

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
        } for m in datamahasiswa]
    
    return {'count': len(response), 'mahasiswa':response}

@app.post('/mahasiswa')
def addMahasiswa():
    data = request.get_json()
    new_mhs = Mahasiswa(
        nama = data['nama'],
        gender = data['gender'],
        kontak = data['kontak'],
        email = data['email'])
    db.session.add(new_mhs)
    db.session.commit()
    return {"message":f"Mahasiswa baru ditambahkan"}

@app.route('/mahasiswa/<nim>', methods=['GET', 'PUT', 'DELETE'])
def handleMahasiswa(nim):
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
        mhs.nim = data['nim']
        mhs.nama = data['nama']
        mhs.gender = data['gender']
        mhs.kontak = data['kontak']
        mhs.email = data['email']
        db.session.add(mhs)
        db.session.commit()
        return {'message': f'Mahasiswa {mhs.nama} berhasil diupdate'}
    
    elif request.method == 'DELETE':
        db.session.delete(mhs)
        db.session.commit()
        return {'message': f'Mahasiswa {mhs.nama} berhasil dihapus'}

@app.get('/matakuliah')
def getMatkul():
    datamatkul = Matkul.query.all()
    response = [
        {
            'kode_mk': dm.kode_mk,
            'nama_mk': dm.nama_mk,
            'sks': dm.sks
        } for dm in datamatkul]
    
    return {'count': len(response), 'matakuliah':response}

@app.get('/ruangkelas')
def getKelas():
    datakelas = RuangKelas.query.all()
    response = [
        {
            'kode_kelas': dk.kode_ruang_kelas,
            'nama_kelas': dk.nama_ruang_kelas,
            'nip_dosen': dk.nip_dosen,
            'kode_mk': dk.kode_mk,
            'jam': str(dk.jam),
            'hari': dk.hari
        } for dk in datakelas]
    
    return {'count': len(response), 'ruangkelas': response}

if __name__ == '__main__':
	app.run(debug=True)
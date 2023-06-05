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

@app.get('/mahasiswa')
def getMahasiswa():
    datamahasiswa = Mahasiswa.query.all()
    results = [
        {
            'nim':m.nim,
            'nama':m.nama,
            'gender':m.gender,
            'kontak':m.kontak,
            'email':m.email
        } for m in datamahasiswa]
    
    return {'count': len(results), 'mahasiswa':results}

@app.post('/mahasiswa')
def addMahasiswa():
    data = request.get_json()
    new_mhs = Mahasiswa(
        nama=data['nama'],
        gender=data['gender'],
        kontak=data['kontak'],
        email=data['email'])
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

if __name__ == '__main__':
	app.run(debug=True)
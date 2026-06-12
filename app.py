from flask import Flask,render_template, send_file,session,redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from xhtml2pdf import pisa
from flask import make_response
from sqlalchemy import extract
from xhtml2pdf import pisa
import os
from io import BytesIO
from flask import make_response
from xhtml2pdf import pisa
from openpyxl import Workbook
from flask import send_file
import io

app = Flask(__name__)
app.secret_key = 'pulih'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pulih.db'
db = SQLAlchemy(app)

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nama = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(100)
    )

    role = db.Column(
        db.String(20),
        default='user'
    )

    usia = db.Column(
        db.Integer
    )

    gender = db.Column(
        db.String(20)
    )

    prodi = db.Column(
        db.String(100)
    )

    semester = db.Column(
        db.String(20)
    )

    tanggal_daftar = db.Column(
        db.DateTime,
        default=datetime.now
    )

class RiwayatTes(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    tanggal = db.Column(
        db.DateTime
    )

    skor_depresi = db.Column(
        db.Integer
    )

    skor_anxiety = db.Column(
        db.Integer
    )

    skor_stress = db.Column(
        db.Integer
    )

    kategori_depresi = db.Column(
        db.String(50)
    )

    kategori_anxiety = db.Column(
        db.String(50)
    )

    kategori_stress = db.Column(
        db.String(50)
    )


@app.route('/')
def home():
    return render_template('home.html',
                           active_page='home')

@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(
        email=email,
        password=password
    ).first()

    if user:

        session['user'] = user.nama
        session['user_id'] = user.id
        session['role'] = user.role

        if user.role == 'admin':
            return redirect('/admin')

        return redirect('/')

    flash('Email atau password salah!')

    return redirect('/?login_error=1')



@app.route('/admin')
def admin():

    if session.get('role') != 'admin':
        return redirect('/')

    # total user (tanpa admin)
    total_user = User.query.filter(
        User.role == 'user'
    ).count()

    # total tes
    total_tes = RiwayatTes.query.count()

    # data user
    users = User.query.order_by(
        User.id.desc()
    ).all()

    # statistik user per bulan
    user_per_bulan = []

    for bulan in range(1, 13):

        jumlah = User.query.filter(
            extract('month', User.tanggal_daftar) == bulan,
            User.role == 'user'
        ).count()

        user_per_bulan.append(jumlah)

    return render_template(
        'admin.html',

        total_user=total_user,
        total_tes=total_tes,

        users=users,

        user_per_bulan=user_per_bulan
    )

@app.route('/admin/user/<int:id>')
def detail_user_admin(id):

    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get_or_404(id)

    riwayat = RiwayatTes.query.filter_by(
        user_id=user.id
    ).order_by(
        RiwayatTes.tanggal.desc()
    ).all()

    total_tes = len(riwayat)

    return render_template(
        'detail_user_admin.html',

        user=user,

        riwayat=riwayat,

        total_tes=total_tes
    )

@app.route('/hapus_user/<int:id>')
def hapus_user(id):

    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get_or_404(id)

    RiwayatTes.query.filter_by(
        user_id=user.id
    ).delete()

    db.session.delete(user)

    db.session.commit()

    return redirect('/admin')

@app.route('/register', methods=['POST'])
def register():

    nama = request.form['nama']
    email = request.form['email']
    password = request.form['password']
    usia = request.form['usia']
    gender = request.form['gender']
    prodi = request.form['prodi']
    semester = request.form['semester']

    if len(password) < 8:
        flash('Password minimal 8 karakter!')
        return redirect('/')

    user = User(
        nama=nama,
        email=email,
        password=password,
        role='user',
        usia=usia,
        gender=gender,
        prodi=prodi,
        semester=semester
    )

    db.session.add(user)
    db.session.commit()

    # LOGIN OTOMATIS SETELAH DAFTAR
    session['user'] = user.nama
    session['user_id'] = user.id
    session['role'] = user.role

    return redirect('/')

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

@app.route('/psikotes')
def psikotes():
    if 'user' not in session:
        return redirect('/')

    # reset status penyimpanan hasil
    session.pop('hasil_sudah_disimpan', None)

    return render_template(
        'psikotes.html',
        active_page='psikotes'
    )
# fakta
def kategori_depresi(skor):

    if skor <= 9:
        return "Normal"

    elif skor <= 13:
        return "Ringan"

    elif skor <= 20:
        return "Sedang"

    elif skor <= 27:
        return "Berat"

    else:
        return "Sangat Berat"


def kategori_anxiety(skor):

    if skor <= 7:
        return "Normal"

    elif skor <= 9:
        return "Ringan"

    elif skor <= 14:
        return "Sedang"

    elif skor <= 19:
        return "Berat"

    else:
        return "Sangat Berat"


def kategori_stress(skor):

    if skor <= 14:
        return "Normal"

    elif skor <= 18:
        return "Ringan"

    elif skor <= 25:
        return "Sedang"

    elif skor <= 33:
        return "Berat"

    else:
        return "Sangat Berat"
    
def forward_chaining(depresi, anxiety, stress):

        rekomendasi = []

        # RULE 1
        if depresi == "Normal":
            rekomendasi.append(
                "Pertahankan pola hidup sehat, tidur cukup, dan aktivitas yang menyenangkan."
            )

        # RULE 2
        if depresi == "Ringan":
            rekomendasi.append(
                "Lakukan aktivitas positif seperti olahraga ringan dan berbicara dengan orang terdekat."
            )

        # RULE 3
        if depresi == "Sedang":
            rekomendasi.append(
                "Buat jadwal aktivitas harian, lakukan journaling, dan cari dukungan sosial."
            )

        # RULE 4
        if depresi == "Berat":
            rekomendasi.append(
                "Kurangi aktivitas yang terlalu membebani dan pertimbangkan konsultasi dengan psikolog."
            )

        # RULE 5
        if depresi == "Sangat Berat":
            rekomendasi.append(
                "Segera cari bantuan profesional dari psikolog atau psikiater."
            )

        # RULE 6
        if anxiety == "Ringan":
            rekomendasi.append(
                "Latih teknik pernapasan dan kurangi konsumsi kafein."
            )

        # RULE 7
        if anxiety == "Sedang":
            rekomendasi.append(
                "Lakukan relaksasi atau meditasi secara rutin."
            )

        # RULE 8
        if anxiety == "Berat":
            rekomendasi.append(
                "Mulai konsultasi dengan tenaga profesional dan cari dukungan sosial."
            )

        # RULE 9
        if anxiety == "Sangat Berat":
            rekomendasi.append(
                "Segera konsultasikan kondisi kepada psikolog atau psikiater."
            )

        # RULE 10
        if stress == "Ringan":
            rekomendasi.append(
                "Atur waktu dengan baik dan lakukan aktivitas relaksasi."
            )

        # RULE 11
        if stress == "Sedang":
            rekomendasi.append(
                "Kurangi beban aktivitas dan perbaiki pola tidur."
            )

        # RULE 12
        if stress == "Berat":
            rekomendasi.append(
                "Istirahat yang cukup dan kurangi tekanan pekerjaan maupun akademik."
            )

        # RULE 13
        if stress == "Sangat Berat":
            rekomendasi.append(
                "Fokus pada pemulihan kondisi fisik dan mental serta konsultasi profesional."
            )

        # RULE KOMBINASI

        # RULE 14
        if anxiety == "Sangat Berat" or depresi == "Sangat Berat":
            rekomendasi.append(
                "Disarankan segera berkonsultasi dengan psikolog atau psikiater."
            )

        # RULE 15
        if (
            depresi in ["Berat", "Sangat Berat"] and
            anxiety in ["Berat", "Sangat Berat"]
        ):
            rekomendasi.append(
                "Libatkan keluarga atau orang terpercaya untuk mendapatkan dukungan emosional."
            )

        # RULE 16
        if (
            depresi in ["Berat", "Sangat Berat"] and
            anxiety in ["Berat", "Sangat Berat"] and
            stress in ["Berat", "Sangat Berat"]
        ):
            rekomendasi.append(
                "Kondisi memerlukan perhatian serius. Segera lakukan konsultasi profesional."
            )

        return rekomendasi
    
@app.route('/depresi', methods=['GET','POST'])
def depresi():

    if request.method == 'POST':

        jawaban = {}

        for i in range(1,8):
            jawaban[f'q{i}'] = request.form.get(f'q{i}')

        session['depresi_jawaban'] = jawaban

        total_depresi = (
            sum(
                int(request.form.get(f'q{i}',0))
                for i in range(1,8)
            )
        ) * 2

        session['skor_depresi'] = total_depresi

        return redirect('/anxiety')

    jawaban = {}

    return render_template(
        'depresi.html',
        jawaban=jawaban
    )


@app.route('/anxiety', methods=['GET','POST'])
def anxiety():

    if request.method == 'POST':

        jawaban = {}

        for i in range(1,8):
            jawaban[f'q{i}'] = request.form.get(f'q{i}')

        session['anxiety_jawaban'] = jawaban

        total_anxiety = (
            sum(
                int(request.form.get(f'q{i}',0))
                for i in range(1,8)
            )
        ) * 2

        session['skor_anxiety'] = total_anxiety

        return redirect('/stress')

    jawaban = {}

    return render_template(
        'anxiety.html',
        jawaban=jawaban
    )

@app.route('/stress', methods=['GET','POST'])
def stress():

    if request.method == 'POST':

        q1 = int(request.form['q1'])
        q2 = int(request.form['q2'])
        q3 = int(request.form['q3'])
        q4 = int(request.form['q4'])
        q5 = int(request.form['q5'])
        q6 = int(request.form['q6'])
        q7 = int(request.form['q7'])

        total_stress = (
            q1 + q2 + q3 +
            q4 + q5 + q6 + q7
        ) * 2

        session['skor_stress'] = total_stress

        return redirect('/hasil')

    return render_template(
        'stress.html'
    )
def warna_kategori(kategori):

    if kategori == "Normal":
        return "bg-normal"

    elif kategori == "Ringan":
        return "bg-ringan"

    elif kategori == "Sedang":
        return "bg-sedang"

    elif kategori == "Berat":
        return "bg-berat"

    elif kategori == "Sangat Berat":
        return "bg-sangat-berat"

    return "bg-secondary"   # Merah Maroon


@app.route('/hasil')
def hasil():

    if 'user_id' not in session:
        return redirect('/')

    user = db.session.get(
        User,
        session['user_id']
    )

    if not user:
        session.clear()
        return redirect('/')

    skor_depresi = session.get('skor_depresi', 0)
    skor_anxiety = session.get('skor_anxiety', 0)
    skor_stress = session.get('skor_stress', 0)

    # KATEGORI DASS
    depresi = kategori_depresi(skor_depresi)
    anxiety = kategori_anxiety(skor_anxiety)
    stress = kategori_stress(skor_stress)

    # FORWARD CHAINING
    rekomendasi = forward_chaining(
        depresi,
        anxiety,
        stress
    )

    print("Depresi :", depresi)
    print("Anxiety :", anxiety)
    print("Stress :", stress)
    print("Rekomendasi :", rekomendasi)

    # SIMPAN RIWAYAT SEKALI SAJA
    if not session.get('hasil_sudah_disimpan'):

        riwayat = RiwayatTes(
            user_id=user.id,
            tanggal=datetime.now(),
            skor_depresi=skor_depresi,
            skor_anxiety=skor_anxiety,
            skor_stress=skor_stress,
            kategori_depresi=depresi,
            kategori_anxiety=anxiety,
            kategori_stress=stress
        )

        db.session.add(riwayat)
        db.session.commit()

        session['riwayat_id'] = riwayat.id
        session['hasil_sudah_disimpan'] = True

    # PERSENTASE PROGRESS BAR
    persen_depresi = int((skor_depresi / 42) * 100)
    persen_anxiety = int((skor_anxiety / 42) * 100)
    persen_stress = int((skor_stress / 42) * 100)

    # WARNA BERDASARKAN KATEGORI
    warna_depresi = warna_kategori(depresi)
    warna_anxiety = warna_kategori(anxiety)
    warna_stress = warna_kategori(stress)
    
    return render_template(
        'hasil.html',

        user=user,

        skor_depresi=skor_depresi,
        skor_anxiety=skor_anxiety,
        skor_stress=skor_stress,

        depresi=depresi,
        anxiety=anxiety,
        stress=stress,

        persen_depresi=persen_depresi,
        persen_anxiety=persen_anxiety,
        persen_stress=persen_stress,

        warna_depresi=warna_depresi,
        warna_anxiety=warna_anxiety,
        warna_stress=warna_stress,

        rekomendasi=rekomendasi,

        riwayat_id=session.get('riwayat_id')
    )

@app.route('/selfcare')
def selfcare():
    return render_template('selfcare.html', active_page='selfcare')

def warna_badge(kategori):

    if kategori == "Normal":
        return "badge-normal"

    elif kategori == "Ringan":
        return "badge-ringan"

    elif kategori == "Sedang":
        return "badge-sedang"

    elif kategori == "Berat":
        return "badge-berat"

    elif kategori == "Sangat Berat":
        return "badge-sangat-berat"

def warna_angka(kategori):

    if kategori == "Normal":
        return "text-success"

    elif kategori == "Ringan":
        return "text-ringan"

    elif kategori == "Sedang":
        return "text-danger"

    elif kategori == "Berat":
        return "text-berat"

    elif kategori == "Sangat Berat":
        return "text-sangat-berat"

    return "text-dark"
@app.route('/riwayat')
def riwayat():

    if 'user_id' not in session:
        return redirect('/')

    data = RiwayatTes.query.filter_by(
        user_id=session['user_id']
    ).order_by(
        RiwayatTes.tanggal.desc()
    ).all()

    for item in data:

        # warna badge
        item.warna_depresi = warna_badge(
            item.kategori_depresi
        )

        item.warna_anxiety = warna_badge(
            item.kategori_anxiety
        )

        item.warna_stress = warna_badge(
            item.kategori_stress
        )

        # warna angka
        item.text_depresi = warna_angka(
            item.kategori_depresi
        )

        item.text_anxiety = warna_angka(
            item.kategori_anxiety
        )

        item.text_stress = warna_angka(
            item.kategori_stress
        )

    return render_template(
        'riwayat.html',
        data=data,
        active_page='riwayat'
    )

def warna_kategori(kategori):

    if kategori == "Normal":
        return "bg-normal"

    elif kategori == "Ringan":
        return "bg-ringan"

    elif kategori == "Sedang":
        return "bg-sedang"

    elif kategori == "Berat":
        return "bg-berat"

    elif kategori == "Sangat Berat":
        return "bg-sangat-berat"

    return "bg-secondary"
@app.route('/detail_hasil/<int:id>')
def detail_hasil(id):

    riwayat = RiwayatTes.query.get_or_404(id)

    user = User.query.get(riwayat.user_id)

    # FORWARD CHAINING
    rekomendasi = forward_chaining(
        riwayat.kategori_depresi,
        riwayat.kategori_anxiety,
        riwayat.kategori_stress
    )

    # PERSENTASE PROGRESS BAR
    persen_depresi = int((riwayat.skor_depresi / 42) * 100)
    persen_anxiety = int((riwayat.skor_anxiety / 42) * 100)
    persen_stress = int((riwayat.skor_stress / 42) * 100)

    # WARNA KATEGORI
    warna_depresi = warna_kategori(
        riwayat.kategori_depresi
    )

    warna_anxiety = warna_kategori(
        riwayat.kategori_anxiety
    )

    warna_stress = warna_kategori(
        riwayat.kategori_stress
    )

    return render_template(
        'hasil.html',

        user=user,

        skor_depresi=riwayat.skor_depresi,
        skor_anxiety=riwayat.skor_anxiety,
        skor_stress=riwayat.skor_stress,

        depresi=riwayat.kategori_depresi,
        anxiety=riwayat.kategori_anxiety,
        stress=riwayat.kategori_stress,

        persen_depresi=persen_depresi,
        persen_anxiety=persen_anxiety,
        persen_stress=persen_stress,

        warna_depresi=warna_depresi,
        warna_anxiety=warna_anxiety,
        warna_stress=warna_stress,

        rekomendasi=rekomendasi,

        riwayat_id=riwayat.id
    )
    
@app.route('/profil')
def profil():

    user = User.query.filter_by(
        nama=session['user']
    ).first()

    total_tes = RiwayatTes.query.filter_by(
        user_id=user.id
    ).count()

    return render_template(
        'profil.html',
        user=user,
        total_tes=total_tes
    )

@app.route('/edit_profil')
def edit_profil():

    user = User.query.filter_by(
        nama=session['user']
    ).first()

    return render_template(
        'edit_profil.html',
        user=user,
        active_page='profil'
    )
@app.route('/update_profil', methods=['POST'])
def update_profil():

    user = User.query.filter_by(
        nama=session['user']
    ).first()

    user.nama = request.form['nama']
    user.email = request.form['email']
    user.usia = request.form['usia']
    user.gender = request.form['gender']
    user.prodi = request.form['prodi']
    user.semester = request.form['semester']

    db.session.commit()

    session['user'] = user.nama

    return redirect('/profil')

with app.app_context():

    db.create_all()

    print("Database berhasil dibuat!")



logo_path = os.path.join(
    app.root_path,
    'static',
    'img',
    'logo',
    'logo.png'
)


@app.route('/download_pdf/<int:id>')
def download_pdf(id):

    riwayat = RiwayatTes.query.get_or_404(id)

    user = User.query.get(
        riwayat.user_id
    )

    html = render_template(
        'pdf_hasil.html',
        user=user,
        skor_depresi=riwayat.skor_depresi,
        skor_anxiety=riwayat.skor_anxiety,
        skor_stress=riwayat.skor_stress,
        depresi=riwayat.kategori_depresi,
        anxiety=riwayat.kategori_anxiety,
        stress=riwayat.kategori_stress,
        tanggal=riwayat.tanggal
    )

    pdf = BytesIO()

    pisa.CreatePDF(
        html,
        dest=pdf
    )

    pdf.seek(0)

    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hasil_tes_{id}.pdf'
    )

@app.route('/set_admin')
def set_admin():

    user = User.query.filter_by(
        email='pulih@gmail.com'
    ).first()

    user.role = 'admin'

    db.session.commit()

    return "Berhasil jadi admin"

@app.route('/selesai_tes')
def selesai_tes():

    session.pop('depresi_jawaban', None)
    session.pop('anxiety_jawaban', None)
    session.pop('stress_jawaban', None)

    session.pop('skor_depresi', None)
    session.pop('skor_anxiety', None)
    session.pop('skor_stress', None)

    session.pop('hasil_sudah_disimpan', None)

    return redirect('/riwayat')

@app.route('/tes_baru')
def tes_baru():

    # hapus jawaban
    session.pop('depresi_jawaban', None)
    session.pop('anxiety_jawaban', None)
    session.pop('stress_jawaban', None)

    # hapus skor
    session.pop('skor_depresi', None)
    session.pop('skor_anxiety', None)
    session.pop('skor_stress', None)

    # hapus flag
    session.pop('hasil_sudah_disimpan', None)

    return redirect('/depresi')

@app.route('/tentang')
def tentang():
    return render_template(
        'tentang.html',
        active_page='tentang'
    )


@app.route('/faq')
def faq():
    return render_template(
        'faq.html',
        active_page='faq'
    )


@app.route('/privasi')
def privasi():
    return render_template(
        'privasi.html',
        active_page='privasi'
    )


@app.route('/syarat')
def syarat():
    return render_template(
        'syarat.html',
        active_page='syarat'
    )



@app.route('/export_excel')
def export_excel():

    if session.get('role') != 'admin':
        return redirect('/')

    wb = Workbook()

    ws = wb.active
    ws.title = "Data User"

    ws.append([
        "Nama",
        "Email",
        "Usia",
        "Gender",
        "Prodi",
        "Semester",
        "Tanggal Daftar"
    ])

    users = User.query.filter(
        User.role == 'user'
    ).all()

    for user in users:

        ws.append([
            user.nama,
            user.email,
            user.usia,
            user.gender,
            user.prodi,
            user.semester,
            user.tanggal_daftar.strftime('%d-%m-%Y')
        ])

    file = io.BytesIO()

    wb.save(file)

    file.seek(0)

    return send_file(
        file,
        as_attachment=True,
        download_name='data_user.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=True)


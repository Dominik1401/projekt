from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, session, request, current_app
from functools import wraps
from werkzeug.utils import secure_filename
from backend.models import db, Bild, Artikel, Appointment
import os
from datetime import datetime


# Erlaubte Dateitypen definieren
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

backend_bp = Blueprint('backend', __name__,
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='/admin/static')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('backend.login'))
        return f(*args, **kwargs)
    return decorated_function
    
@backend_bp.route('/artikel', methods=['GET'])
@login_required
def artikel():
    artikel_liste = Artikel.query.all()
    return render_template('artikel.html', articles=artikel_liste)

@backend_bp.route('/artikel/neu', methods=['GET', 'POST'])
@login_required
def artikel_neu():
    if request.method == 'POST':
        titel = request.form['titel']
        inhalt = request.form['inhalt']
        is_published = 'is_published' in request.form
        artikel = Artikel(titel=titel, inhalt=inhalt, is_published=is_published)
        db.session.add(artikel)
        db.session.commit()
        flash('Artikel erfolgreich erstellt!', 'success')
        return redirect(url_for('backend.artikel'))
    return render_template('artikel_form.html')

@backend_bp.route('/artikel/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def artikel_edit(id):
    artikel = Artikel.query.get_or_404(id)
    if request.method == 'POST':
        artikel.titel = request.form['titel']
        artikel.inhalt = request.form['inhalt']
        artikel.is_published = 'is_published' in request.form
        db.session.commit()
        flash('Artikel erfolgreich aktualisiert!', 'success')
        return redirect(url_for('backend.artikel'))
    return render_template('artikel_form.html', article=artikel)

@backend_bp.route('/artikel/<int:id>/delete', methods=['POST'])
@login_required
def artikel_delete(id):
    artikel = Artikel.query.get_or_404(id)
    db.session.delete(artikel)
    db.session.commit()
    flash('Artikel erfolgreich gelöscht!', 'success')
    return redirect(url_for('backend.artikel'))

@backend_bp.route('/artikel/save', methods=['POST'])
@login_required
def save_article():
    artikel_id = request.form.get('artikel_id')
    if artikel_id:
        artikel = Artikel.query.get_or_404(artikel_id)
        artikel.titel = request.form['titel']
        artikel.inhalt = request.form['inhalt']
        artikel.is_published = 'is_published' in request.form
    else:
        artikel = Artikel(
            titel=request.form['titel'],
            inhalt=request.form['inhalt'],
            is_published='is_published' in request.form
        )
        db.session.add(artikel)
    db.session.commit()
    flash('Artikel erfolgreich gespeichert!', 'success')
    return redirect(url_for('backend.artikel'))


@backend_bp.route('/')
@login_required
def admin():
    return redirect(url_for('backend.dashboard'))

@backend_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
            session['logged_in'] = True
            return redirect(url_for('backend.dashboard'))
        return render_template('login.html', error="Login fehlgeschlagen")
    return render_template('login.html')

@backend_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@backend_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('backend.login'))
    
@backend_bp.route('/uploads/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'backend/static/uploads'), 
                             filename)

# Bilderverwaltung
@backend_bp.route('/bilder')
@login_required
def bilder():
    bilder = Bild.query.all()
    return render_template('bilder.html', bilder=bilder)

@backend_bp.route('/bilder/upload', methods=['POST'])
@login_required
def upload_bild():
    if 'bild' not in request.files:
        return redirect(url_for('backend.bilder'))
    
    file = request.files['bild']
    if file and allowed_file(file.filename):
        # Bild mit PIL öffnen
        img = Image.open(file)
        
        # Maximale Dimensionen
        max_size = (800, 800)
        
        # Originalgröße
        width, height = img.size
        
        # Skalierungsfaktor berechnen
        scale = min(max_size[0]/width, max_size[1]/height)
        
        # Nur skalieren wenn das Bild größer als erlaubt ist
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Skaliertes Bild speichern
        img.save(upload_path, quality=95, optimize=True)
        
        new_bild = Bild(
            filename=filename,
            path=upload_path,
            description=request.form.get('description', '')
        )
        db.session.add(new_bild)
        db.session.commit()
    
    return redirect(url_for('backend.bilder'))

@backend_bp.route('/bilder/delete/<int:bild_id>', methods=['POST'])
@login_required
def delete_bild(bild_id):
    bild = Bild.query.get_or_404(bild_id)
    if os.path.exists(bild.path):
        os.remove(bild.path)
    db.session.delete(bild)
    db.session.commit()
    return redirect(url_for('backend.bilder'))

# Artikelverwaltung
@backend_bp.route('/artikel')
@login_required
def artikel():
    artikel = Artikel.query.all()
    return render_template('artikel.html', artikel=artikel)

@backend_bp.route('/artikel/neu', methods=['GET', 'POST'])
@login_required
def artikel_neu():
    if request.method == 'POST':
        artikel = Artikel(
            titel=request.form['titel'],
            inhalt=request.form['inhalt'],
            is_published=False
        )
        db.session.add(artikel)
        db.session.commit()
        return redirect(url_for('backend.artikel'))
    bilder = Bild.query.filter_by(is_active=True).all()  # Alle aktiven Bilder laden
    return render_template('artikel_form.html', bilder=bilder)

@backend_bp.route('/artikel/edit/<int:artikel_id>', methods=['GET', 'POST'])
@login_required
def artikel_edit(artikel_id):
    artikel = Artikel.query.get_or_404(artikel_id)
    if request.method == 'POST':
        artikel.titel = request.form['titel']
        artikel.inhalt = request.form['inhalt']
        artikel.is_published = 'is_published' in request.form
        db.session.commit()
        return redirect(url_for('backend.artikel'))
    bilder = Bild.query.filter_by(is_active=True).all()  # Alle aktiven Bilder laden
    return render_template('artikel_form.html', artikel=artikel, bilder=bilder)

@backend_bp.route('/artikel/delete/<int:artikel_id>', methods=['POST'])
@login_required
def artikel_delete(artikel_id):
    artikel = Artikel.query.get_or_404(artikel_id)
    db.session.delete(artikel)
    db.session.commit()
    return redirect(url_for('backend.artikel'))
    
@backend_bp.route('/artikel/publish/<int:artikel_id>', methods=['POST'])
@login_required
def artikel_publish(artikel_id):
    artikel = Artikel.query.get_or_404(artikel_id)
    artikel.is_published = True
    db.session.commit()
    return redirect(url_for('backend.artikel'))
    

@backend_bp.route('/appointments/create', methods=['GET'])
@login_required
def create_appointment():
    return render_template('create_appointment.html')

@backend_bp.route('/appointments/add', methods=['POST'])
@login_required
def add_appointment():
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date')
    
    if not title or not date_str:
        return redirect(url_for('backend.create_appointment'))
        
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    appointment = Appointment(title=title, description=description, date=date)
    
    db.session.add(appointment)
    db.session.commit()
    
    return redirect(url_for('frontend.appointments'))
    
    
    


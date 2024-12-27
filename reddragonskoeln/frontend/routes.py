from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import os
from backend.models import Artikel, Appointment

frontend_bp = Blueprint('frontend', __name__,
                       template_folder='templates',
                       static_folder='static',
                       static_url_path='/static')

@frontend_bp.route('/')
def index():
    return render_template('index.html')
    return redirect(url_for('frontend.login'))
    
@frontend_bp.route('/impressum')
def impressum():
    return render_template('impressum.html')

@frontend_bp.route('/kontakt')
def kontakt():
    return render_template('kontakt.html')

@frontend_bp.route('/bilderarchiv')
def bilderarchiv():
    # Bilder aus dem Backend-Verzeichnis auflesen
    image_dir = os.path.join(current_app.root_path, 'backend/static/uploads')
    images = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.gif'))]
    return render_template('bilderarchiv.html', images=images)

@frontend_bp.route('/kalender')
def kalender():
    return render_template('kalender.html')

@frontend_bp.route('/blog')
def blog():
    artikel = Artikel.query.filter_by(is_published=True).order_by(Artikel.erstelldatum.desc()).all()
    return render_template('blog.html', artikel=artikel)
    
@frontend_bp.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv('MEMBER_PASSWORD'):
            session['authenticated'] = True
            return redirect(url_for('frontend.appointments'))
        else:
            return render_template('appointments.html', error="Falsches Passwort! Du Kommst hier nicht rein ;)")

    if not session.get('authenticated'):
        return render_template('appointments.html')

# Termine aus der Datenbank abrufen
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)
    

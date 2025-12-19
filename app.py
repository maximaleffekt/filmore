import os

from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from forms import RollForm, CameraForm, LensForm, ImageForm, LoginForm, RegisterForm
from models import db, User, Roll, Image, Camera, Lens, Filter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ''  # in prod: set via env var
# Cookie hardening options (für Entwicklung: SESSION_COOKIE_SECURE=False wenn kein HTTPS)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# ----- Auth Routes -----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Benutzername bereits vergeben.", "warning")
            return render_template('register.html', form=form)
        user = User(username=form.username.data,
                    password_hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash("Registrierung erfolgreich. Bitte einloggen.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Erfolgreich eingeloggt.", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash("Ungültiger Benutzername oder Passwort.", "danger")
    return render_template('login.html', form=form)

@app.route('/roles')
@login_required
def list_roles():
    roles = Roll.query.filter_by(user_id=current_user.id).all()
    return render_template('list_roles.html', roles=roles)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Ausgeloggt.", "info")
    return redirect(url_for('login'))

# ----- App Routes (geschützt) -----
FILM_OPTIONS = {
    "Kodak": ["Portra 160", "Portra 400", "Tri-X 400", "Ektar 100", "Gold 200", "T-Max 400", "T-Max 100",
              "Ektachrome E100", "Ultramax 400", "Colorplus 200", "Kodacolor 200", "Kodacolor 100", "Portra 800", "Portra 400"],
    "Fujifilm": ["Velvia 50", "Pro 400H", "Neopan 100 Acros"],
    "Ilford": ["HP5 Plus", "Delta 3200", "Pan F Plus"]
}

@app.route('/get_films/<manufacturer>')
@login_required
def get_films(manufacturer):
    manufacturer = manufacturer.title()
    films = FILM_OPTIONS.get(manufacturer, [])
    return jsonify(films)

@app.route('/add_role', methods=['GET', 'POST'])
@login_required
def add_role():
    form = RollForm()

    # Dynamische Filmtyp-Choices für POST
    if request.method == 'POST':
        manufacturer = request.form.get('film_manufacturer', '')
        films = FILM_OPTIONS.get(manufacturer.title(), [])
        form.film_type.choices = [(f, f) for f in films]

    if form.validate_on_submit():
        role = Roll(
            name=form.name.data,
            user_id=current_user.id,
            film_manufacturer=form.film_manufacturer.data,
            film_type=form.film_type.data,
            iso=form.iso.data
        )
        db.session.add(role)
        db.session.commit()
        flash("Rolle hinzugefügt.", "success")
        return redirect(url_for('index'))

    else:
        print("Form errors:", form.errors)

    return render_template('add_role.html', form=form)


@app.route('/')
@login_required
def index():
    # nur Rollen des aktuellen Benutzers zeigen
    roles = Roll.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', roles=roles)

@app.route('/role/<int:role_id>')
@login_required
def role_view(role_id):
    role = Roll.query.filter_by(id=role_id, user_id=current_user.id).first_or_404()
    return render_template('role.html', role=role)

@app.route('/role/<int:role_id>/add_image', methods=['GET', 'POST'])
@login_required
def add_image(role_id):
    role = Roll.query.filter_by(id=role_id, user_id=current_user.id).first_or_404()
    form = ImageForm()

    # Optionen inkl. None-Auswahl
    form.camera.choices = [(0, '– Keine –')] + [(c.id, c.name) for c in Camera.query.filter_by(user_id=current_user.id)]
    form.lens.choices = [(0, '– Keine –')] + [(l.id, l.name) for l in Lens.query.filter_by(user_id=current_user.id)]
    form.filter.choices = [(0, '– Keine –')] + [(f.id, f.name) for f in Filter.query.filter_by(user_id=current_user.id)]

    if form.validate_on_submit():
        last_frame = Image.query.filter_by(role_id=role.id).order_by(Image.frame_number.desc()).first()
        next_frame = (last_frame.frame_number + 1) if (last_frame and last_frame.frame_number) else 1

        # Datei speichern (optional)
        image_filename = None
        if form.image_file.data:
            file = form.image_file.data
            safe_name = secure_filename(file.filename)
            image_filename = f"{role.id}_{next_frame}_{safe_name}"
            file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        new_image = Image(
            filename=form.filename.data,
            shutter_speed=form.shutter_speed.data,
            aperture=form.aperture.data,
            camera_id=form.camera.data if form.camera.data != 0 else None,
            lens_id=form.lens.data if form.lens.data != 0 else None,
            filter_id=form.filter.data if form.filter.data != 0 else None,
            role_id=role.id,
            image_file=image_filename,
            frame_number=next_frame
        )
        db.session.add(new_image)
        db.session.commit()
        flash(f"Bild Frame {next_frame} hinzugefügt.", "success")
        return redirect(url_for('role_view', role_id=role.id))

    return render_template('add_image.html', form=form, role=role)

# weitere Routen (add_camera, add_lens, export_json ...) sollten ebenfalls @login_required haben
@app.route('/add_camera', methods=['GET', 'POST'])
@login_required
def add_camera():
    form = CameraForm()
    if form.validate_on_submit():
        c = Camera(name=form.name.data, min_shutter_speed=form.min_shutter_speed.data, max_shutter_speed=form.max_shutter_speed.data, serial_number=form.serial_number.data, user_id=current_user.id)
        db.session.add(c)
        db.session.commit()
        flash("Kamera hinzugefügt.", "success")
        return redirect(url_for('index'))
    return render_template('add_camera.html', form=form)

@app.route('/add_lens', methods=['GET', 'POST'])
@login_required
def add_lens():
    form = LensForm()
    if form.validate_on_submit():
        l = Lens(name=form.name.data, focal_length=form.focal_length.data, min_aperture=form.min_aperture.data, max_aperture=form.max_aperture.data, serial_number=form.serial_number.data, user_id=current_user.id)
        db.session.add(l)
        db.session.commit()
        flash("Objektiv hinzugefügt.", "success")
        return redirect(url_for('index'))
    return render_template('add_lens.html', form=form)

@app.route("/edit_image/<int:image_id>", methods=["GET", "POST"])
@login_required
def edit_image(image_id):
    image = Image.query.get_or_404(image_id)
    form = ImageForm(obj=image)

    # Dropdown-Optionen neu laden
    form.camera.choices = [(0, "–")] + [(c.id, c.name) for c in Camera.query.filter_by(user_id=current_user.id)]
    form.lens.choices = [(0, "–")] + [(l.id, l.name) for l in Lens.query.filter_by(user_id=current_user.id)]
    form.filter.choices = [(0, "–")] + [(f.id, f.name) for f in Filter.query.filter_by(user_id=current_user.id)]

    if form.validate_on_submit():
        image.shutter_speed = form.shutter_speed.data
        image.aperture = form.aperture.data
        image.camera_id = form.camera.data or None
        image.lens_id = form.lens.data or None
        image.filter_id = form.filter.data or None

        db.session.commit()
        flash("Aufnahme aktualisiert!", "success")
        return redirect(url_for("role_view", role_id=image.role_id))

    return render_template("add_image.html", form=form, role=image.role, edit_mode=True)

@app.route("/delete_image/<int:image_id>")
@login_required
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    role_id = image.role_id
    db.session.delete(image)
    db.session.commit()
    flash("Aufnahme gelöscht.", "info")
    return redirect(url_for("role_view", role_id=role_id))

@app.route('/materials')
@login_required
def materials():
    cameras = Camera.query.filter_by(user_id=current_user.id).all()
    lenses = Lens.query.filter_by(user_id=current_user.id).all()
    filters = Filter.query.filter_by(user_id=current_user.id).all()
    return render_template('materials.html', cameras=cameras, lenses=lenses, filters=filters)


@app.route('/role/<int:role_id>/export_json')
@login_required
def export_role_json(role_id):
    role = Roll.query.filter_by(id=role_id, user_id=current_user.id).first_or_404()

    images_data = []
    for img in role.images:
        images_data.append({
            "frame_number": img.frame_number,
            "filename": img.filename,
            "shutter_speed": img.shutter_speed,
            "aperture": img.aperture,
            "camera": img.camera.name if img.camera else None,
            "lens": img.lens.name if img.lens else None,
            "filter": img.filter.name if img.filter else None,
            "image_file": img.image_file
        })

    data = {
        "role_name": role.name,
        "film_manufacturer": role.film_manufacturer,
        "film_type": role.film_type,
        "iso": role.iso,
        "images": images_data
    }

    # JSON Response als Download
    resp = jsonify(data)
    resp.headers['Content-Disposition'] = f'attachment; filename=role_{role.id}_export.json'
    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

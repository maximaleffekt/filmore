from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed

class RoleForm(FlaskForm):
    name = StringField('Name der Rolle', validators=[DataRequired()])
    film_manufacturer = SelectField(
        'Hersteller',
        choices=[('', '– Auswählen –')] + [(m, m) for m in ["Kodak", "Fujifilm", "Ilford"]],
        validators=[DataRequired()]
    )
    film_type = SelectField(
        'Filmtyp',
        choices=[('', '– Wähle zuerst Hersteller –')],
        validators=[DataRequired()],
        validate_choice=False  # damit JS-Werte akzeptiert werden
    )
    iso = StringField('ISO', validators=[DataRequired()])
    submit = SubmitField('Speichern')



class CameraForm(FlaskForm):
    name = StringField('Kamera', validators=[DataRequired()])
    seriennummer = StringField('Seriennummer')
    min_shutter_speed = StringField('Min. Verschlusszeit')
    max_shutter_speed = StringField('Max. Verschlusszeit')
    submit = SubmitField('Speichern')

class LensForm(FlaskForm):
    name = StringField('Objektiv', validators=[DataRequired()])
    focal_length = StringField('Brennweite')
    min_aperture = StringField('Min. Blende', validators=[DataRequired()])
    max_aperture = StringField('Max. Blende', validators=[DataRequired()])
    serial_number = StringField('Seriennummer')
    submit = SubmitField('Speichern')

class FilterForm(FlaskForm):
    name = StringField('Filter', validators=[DataRequired()])
    submit = SubmitField('Speichern')

class ImageForm(FlaskForm):
    filename = StringField("Dateiname")
    shutter_speed = StringField("Verschlusszeit")
    aperture = StringField("Blende")
    camera = SelectField("Kamera", coerce=int, choices=[])
    lens = SelectField("Objektiv", coerce=int, choices=[])
    filter = SelectField("Filter", coerce=int, choices=[])
    image_file = FileField("Bilddatei (optional)", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Speichern")

class LoginForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired()])
    password = PasswordField("Passwort", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Passwort", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Passwort wiederholen", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrieren")


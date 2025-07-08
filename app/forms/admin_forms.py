from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField, FileField, SelectField, FieldList, FormField, HiddenField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email
from app.forms.validators import HexColour

# Manage user classes


class AddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add User')
    editor = BooleanField("Editor")
    admin = BooleanField("Admin")
    superuser = BooleanField("SuperUser")


class ManageUserForm(FlaskForm):
    user_id = HiddenField("User ID", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    admin = BooleanField("Admin")
    update = SubmitField("Update")
    delete = SubmitField("Delete")
    editor = BooleanField("Editor")
    admin = BooleanField("Admin")
    superuser = BooleanField("SuperUser")


# add articles


class ArticleBlockForm(FlaskForm):
    block_type = SelectField('Type', choices=[
        ('heading', 'Heading'),
        ('paragraph', 'Paragraph'),
        ('image', 'Image'),
        ('figure', 'Figure'),
        ('link', 'Link')
    ])
    content = TextAreaField('Content')  # For heading/paragraph/figure caption
    image = FileField('Upload image', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], 'Ensure you are uploading an image, supported formats: jpg, jpeg, png')])
    alt_text = StringField('Alt text',  validators=[])  # for images
    url_text = StringField('Link text')  # for images


class UploadArticleForm(FlaskForm):
    user_id = HiddenField("User ID", validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    blocks = FieldList(FormField(ArticleBlockForm), min_entries=1)
    post = SubmitField('Post Article')
    preview = SubmitField('Preview Article')


# Newsletters

class NewsBlockForm(FlaskForm):
    block_type = SelectField('Type', choices=[
        ('heading', 'Heading'),
        ('subheading', 'Subheading'),
        ('paragraph', 'Paragraph'),
        ('image', 'Image'),
        ('button', 'Button')

    ])
    content = TextAreaField('Content')  # For heading/paragraph/figure caption
    image = FileField('Upload image', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], 'Ensure you are uploading an image, supported formats: jpg, jpeg, png')])
    alt_text = StringField('Alt text',  validators=[])  # for images
    url_text = StringField('Link text')  # for images
    colour = StringField('Colour', validators=[HexColour()])

 
class UploadNewsForm(FlaskForm):
    user_id = HiddenField("User ID", validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    blocks = FieldList(FormField(NewsBlockForm), min_entries=1)
    post = SubmitField('Post newsletter')
    preview = SubmitField('Download Newsletter')
    book_recs = BooleanField(
        'Include Reading recommendations?', default="checked")

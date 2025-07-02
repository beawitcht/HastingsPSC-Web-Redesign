from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField, FileField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Email

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
        ('figure', 'Figure')
    ])
    content = StringField('Content')  # For heading/paragraph/figure caption
    image = FileField('Upload image', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], 'Ensure you are uploading an image')])
    alt_text = StringField('Alt text',  validators=[])  # for images


class UploadArticleForm(FlaskForm):
    user_id = HiddenField("User ID", validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    blocks = FieldList(FormField(ArticleBlockForm), min_entries=1)
    post = SubmitField('Post Article')
    preview = SubmitField('Preview Article')

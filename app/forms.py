from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, validators


class CommandForm(Form):
    command = TextField('command', [validators.required()])


class RegisterModuleForm(Form):
    name = TextField('Nom', [validators.required(), validators.length(max=120)])
    description = TextAreaField('Description', [validators.optional(), validators.length(max=1024)])

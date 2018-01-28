from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Regexp, ValidationError, Email, DataRequired
from app.models import Users, Role, Source, Menu


# 博客
class PostForm(FlaskForm):
	title = TextAreaField(validators=[DataRequired(message=u'内容不能为空')])
	summary = TextAreaField(validators=[DataRequired(message=u'内容不能为空')])
	body = TextAreaField(validators=[DataRequired(message=u'内容不能为空')])
	source = SelectField('Source', coerce=int)
	menu = SelectField('Menu', coerce=int)
	submit = SubmitField("Submit")


# 管理员修改资料表单

class EditProfileAdminForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	username = StringField('Username', validators=[
		Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
										  'numbers,dots or underscores')])
	confirmed = BooleanField('Confirmed')
	role = SelectField('Role', coerce=int)  # 注意，这里的Field是Select，也就是下拉选择列表
	name = StringField('Real Name', validators=[Length(0, 64)])
	location = StringField('Location', validators=[Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

	def __init__(self, user, *args, **kwargs):  # 这里一定要注意到，在生成表单的时候，是需要带着参数user的！！！
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name)
							 for role in Role.query.order_by(Role.name).all()]
		self.user = user

	# 上面的role.choices属性，是针对的表单role的选项，后面单独写
	def validate_email(self, field):
		if field.data != self.user.email and \
				Users.query.filter_by(email=field.data).first():  # 检验email是否发生更改且是否重复
			raise ValidationError('Email already registered.')

	def validate_username(self, field):  # 检验username是否发生更改且是否重复
		if field.data != self.user.username and \
				Users.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use')

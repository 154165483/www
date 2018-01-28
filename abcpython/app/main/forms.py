from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, DataRequired, Email


# 用户修改自己资料表单
class EditProfileForm(FlaskForm):
	name = StringField('Real name', validators=[Length(0, 64)])  # 这里Length设置(0,64)的意思是可选项，不一定必填
	location = StringField('Location', validators=[Length(0, 64)])
	about_me = TextAreaField('About me')  # TextAreaField，一个文本框功能
	submit = SubmitField('Submit')


# #管理员修改资料表单
#
# class EditProfileAdminForm(FlaskForm):
#     email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
#     username = StringField('Username', validators=[
#         Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
#                                           'numbers,dots or underscores')])
#     confirmed = BooleanField('Confirmed')
#     role = SelectField('Role', coerce=int)  # 注意，这里的Field是Select，也就是下拉选择列表
#     name = StringField('Real Name', validators=[Length(0, 64)])
#     location = StringField('Location', validators=[Length(0, 64)])
#     about_me = TextAreaField('About me')
#     submit = SubmitField('Submit')
#
#     def __init__(self, user, *args, **kwargs):  # 这里一定要注意到，在生成表单的时候，是需要带着参数user的！！！
#         super(EditProfileAdminForm, self).__init__(*args, **kwargs)
#         self.role.choices = [(role.id, role.name)
#                              for role in Role.query.order_by(Role.name).all()]
#         self.user = user
#
#     # 上面的role.choices属性，是针对的表单role的选项，后面单独写
#     def validate_email(self, field):
#         if field.data != self.user.email and \
#                 Users.query.filter_by(email=field.data).first():  # 检验email是否发生更改且是否重复
#             raise ValidationError('Email already registered.')
#
#     def validate_username(self, field):  # 检验username是否发生更改且是否重复
#         if field.data != self.user.username and \
#                 Users.query.filter_by(username=field.data).first():
#             raise ValidationError('Username already in use')


# 评论表单
class CommentForm(FlaskForm):
	body = TextAreaField(u'内容', validators=[DataRequired(), Length(1, 1024)])
	submit = SubmitField('Submit')

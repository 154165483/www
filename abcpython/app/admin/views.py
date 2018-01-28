from flask_login import login_required, current_user
from flask import url_for, flash, redirect, render_template, abort
from app import db
from app.admin.forms import PostForm, EditProfileAdminForm
from app.decorators import admin_required
from app.models import Permission, Post, Users, Role, Source, Menu
from datetime import datetime
from . import admin


# 管理员欢迎界面
@admin.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	return render_template('admin/admin_index1.html')


# 管理员编辑资料
@admin.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):  # 注意：这里的函数带参数id的
	user = Users.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('The profile has been updated.')
		return redirect(url_for('main.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id  # 注意：这里设置初始值的时候，用的是role_id，而role_id是外键，对应roles.id，就是roles表的id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('admin/edit_profile_admin.html', form=form, user=user)


# 管理员编辑博客
@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author_id and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	sources = [(s.id, s.name) for s in Source.query.all()]
	form.source.choices = sources
	menu = [(m.id, m.name) for m in Menu.query.all()]
	form.menu.choices = menu
	if form.validate_on_submit():
		post.title = form.title.data
		post.source_id = form.source.data
		post.body = form.body.data
		post.menu_id = form.menu.data
		post.summary = form.summary.data
		post.author = current_user._get_current_object()
		post.update_time = datetime.utcnow()
		source = Source.query.get(post.source_id)
		menu = Menu.query.get(post.menu_id)
		if source and menu:
			db.session.add(post)
			db.session.commit()
		flash('The post has been updated.')
		return redirect(url_for('main.post', id=post.id))
	form.title.data = post.title
	form.source.data = post.source_id
	form.body.data = post.body
	form.menu.data = post.menu_id
	form.summary.data = post.summary
	return render_template('admin/edit_post_admin.html', form=form, post=post)


# 管理员删除博客
@admin.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete(id):
	post = Post.query.get_or_404(id)
	count = 0
	if current_user != post.author_id and not current_user.can(Permission.WRITE_ARTICLES):
		abort(403)
	for comment in post.comments:
		db.session.delete(comment)
		count = count + 1
	db.session.delete(post)
	try:
		db.session.commit()
	except:
		db.session.rollback()
		flash(u'删除失败！', 'danger')
	else:
		flash(u'成功删除博文和%s条评论！' % count, 'success')
	return redirect(url_for('auth.index'))

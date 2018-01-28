from datetime import datetime
import random
import os
from flask import render_template, abort, flash, redirect, url_for, request, current_app, make_response
from flask_login import login_required, current_user
from app import csrf
from app.admin.forms import PostForm
from app.decorators import permission_required, admin_required
from app.models import Users, Permission, Post, Comment, Source, Menu, BlogCount
from app import db
from .forms import EditProfileForm, CommentForm
from . import main



def gen_rnd_filename():
	filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
	return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@main.route('/main/<username>', methods=['GET', 'POST'])
@login_required
def index(username):
	user = Users.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	# posts = user.posts.order_by(Post.create_time.desc()).all()
	page = request.args.get('page', 1,
							type=int)  # 渲染的页数从请求的查询字符串（request.args）中获取，如果没有明确指定，则默认渲 染第一页。参数 type=int 保证参数无法转换成整数时，返回默认值
	pagination = user.posts.order_by(Post.create_time.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
		error_out=True)
	posts = pagination.items
	return render_template('main/main.html', user=user, posts=posts, pagination=pagination)


# 资料页面路由
@main.route('/user/<username>')
@login_required
def user(username):
	user = Users.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	posts = user.posts.order_by(Post.create_time.desc()).all()
	page = request.args.get('page', 1,
							type=int)  # 渲染的页数从请求的查询字符串（request.args）中获取，如果没有明确指定，则默认渲 染第一页。参数 type=int 保证参数无法转换成整数时，返回默认值
	pagination = user.posts.order_by(Post.create_time.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
		error_out=True)
	posts = pagination.items
	return render_template('main/user.html', user=user, posts=posts, pagination=pagination)


# 修改用户自己资料路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash('Your profile has been updated')
		return redirect(url_for('main.user', username=current_user.username))
	form.name.data = current_user.name  # 注意以下三行的缩进，这三行的功能是让表单在没有提交或者提交失败的情况下
	form.location.data = current_user.location  # 显示的内容是预设值，而预设值就是在提交之前，current_user的各项属性值
	form.about_me.data = current_user.about_me
	return render_template('main/edit_profile.html', form=form)


# 关注路由
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = Users.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('You are already following this user.')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are now following %s.' % username)
	return redirect(url_for('.user', username=username))


# 关注者视图路由
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = Users.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('You are not following this user.')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following %s anymore.' % username)
	return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
@login_required
def followers(username):
	user = Users.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(
		page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
		error_out=False)
	follows = [{'user': item.follower, 'timestamp': item.timestamp}
			   for item in pagination.items]
	return render_template('followers.html', user=user, title="Followers of",
						   endpoint='.followers', pagination=pagination,
						   follows=follows)


@main.route('/followed-by/<username>')
@login_required
def followed_by(username):
	user = Users.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(
		page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
		error_out=False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp}
			   for item in pagination.items]
	return render_template('followers.html', user=user, title="Followed by",
						   endpoint='.followed_by', pagination=pagination,
						   follows=follows)


# 查询所有文章
@main.route('/all')
def show_all():
	resp = make_response(redirect(url_for('auth.index')))
	resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
	return resp


# 查询关注者的文章
@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('auth.index')))
	resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
	return resp


# 博客文章固定链接以及评论
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
	BlogCount.add_blogview(db)
	form = CommentForm(request.form)
	post = Post.query.get_or_404(id)
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
						  post=post,
						  author=current_user._get_current_object())

		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.')
		return redirect(url_for('main.post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (post.comments.count() - 1) // current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	post.add_view(post, db)
	# return render_template('post.html', post=post, User=User,form=form, comments=comments, pagination=pagination, page=page)
	return render_template('post.html',  post=post, Users=Users,
                           comments=comments, pagination=pagination, page=page,
                           form=form, endpoint='.post', id=post.id)

# 管理评论的路由
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
	comments = pagination.items
	return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


# 屏蔽评论
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()
	flash("屏蔽成功")
	return redirect(url_for('.post',id=comment.post_id,
							page=request.args.get('page', 1, type=int)))


# 解除屏蔽评论
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()
	flash("解除屏蔽成功")
	return redirect(url_for('.post',id=comment.post_id,
							page=request.args.get('page', 1, type=int)))

#删除评论
@main.route('/moderate/delete/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_delete(id):
	comment = Comment.query.get_or_404(id)
	db.session.delete(comment)
	db.session.commit()
	flash("删除成功")
	return redirect(url_for('.post',id=comment.post_id,
							page=request.args.get('page', 1, type=int)))




# 写博客
@main.route('/writeblog', methods=['GET', 'POST'])
@login_required
def writeblog():
	if not current_user.can(Permission.WRITE_ARTICLES):
		abort(403)
	form = PostForm()
	sources = [(s.id, s.name) for s in Source.query.all()]
	form.source.choices = sources
	menu = [(m.id, m.name) for m in Menu.query.all()]
	form.menu.choices = menu
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():  # 检查用户是否有写文章的权限
		title = form.title.data
		source_id = form.source.data
		body = form.body.data
		menu_id = form.menu.data
		summary = form.summary.data
		author = current_user._get_current_object()
		source = Source.query.get(source_id)
		menu = Menu.query.get(menu_id)
		if source and menu:
			#将文章内容生成post实例
			post = Post(title=title, source=source, summary=summary, author=author, menu=menu, body=body)
			db.session.add(post)
			db.session.commit()
			flash('Write A Blog Success!', 'success')
			return redirect(url_for('main.post',id=post.id))
	if form.errors:
		flash('Write A Blog Er!', 'danger')
	return render_template('main/writeblog.html', form=form)


# 博客编辑
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author_id and not current_user.can(Permission.WRITE_ARTICLES):
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
	return render_template('main/edit_post.html', form=form, post=post)


# 博客删除
@main.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
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




# 上传图片
@csrf.exempt
@main.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
	error = ''
	url = ''
	callback = request.args.get("CKEditorFuncNum")

	if request.method == 'POST' and 'upload' in request.files:
		fileobj = request.files['upload']
		fname, fext = os.path.splitext(fileobj.filename)
		rnd_name = '%s%s' % (gen_rnd_filename(), fext)

		filepath = os.path.join(main.static_folder, 'upload', rnd_name)

		# 检查路径是否存在，不存在则创建
		dirname = os.path.dirname(filepath)
		if not os.path.exists(dirname):
			try:
				os.makedirs(dirname)
			except:
				error = 'ERROR_CREATE_DIR'
		elif not os.access(dirname, os.W_OK):
			error = 'ERROR_DIR_NOT_WRITEABLE'

		if not error:
			fileobj.save(filepath)
			url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
	else:
		error = 'post error'

	res = """<script type="text/javascript">
      window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>""" % (callback, url, error)

	response = make_response(res)
	response.headers["Content-Type"] = "text/html"
	return response


# 上传图片
@csrf.exempt
@main.route('/edit/upload/', methods=['GET', 'POST'])
@login_required
def editupload():
	error = ''
	url = ''
	callback = request.args.get("CKEditorFuncNum")

	if request.method == 'POST' and 'upload' in request.files:
		fileobj = request.files['upload']
		fname, fext = os.path.splitext(fileobj.filename)
		rnd_name = '%s%s' % (gen_rnd_filename(), fext)

		filepath = os.path.join(main.static_folder, 'upload', rnd_name)

		# 检查路径是否存在，不存在则创建
		dirname = os.path.dirname(filepath)
		if not os.path.exists(dirname):
			try:
				os.makedirs(dirname)
			except:
				error = 'ERROR_CREATE_DIR'
		elif not os.access(dirname, os.W_OK):
			error = 'ERROR_DIR_NOT_WRITEABLE'

		if not error:
			fileobj.save(filepath)
			url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
	else:
		error = 'post error'

	res = """<script type="text/javascript">
      window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>""" % (callback, url, error)

	response = make_response(res)
	response.headers["Content-Type"] = "text/html"
	return response

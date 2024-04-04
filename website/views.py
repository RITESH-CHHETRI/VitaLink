from flask import Blueprint, render_template, request, flash, jsonify,redirect, url_for,send_file
from flask_login import login_required, current_user
from .models import User, Post, Notification, Message
from . import db
import json
from werkzeug.utils import secure_filename
import os
import hashlib

PASSWORD = 'edb9b2757f69b16503d2fc2b3a68479ddab27c0eea2f0c338e353239fcf2d5b9'

views = Blueprint('views', __name__)

@views.route('/VitaLink', methods=['GET'])
def landing():
    return render_template("landingPage.html")

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    notifs=Notification.query.filter_by(user_id=current_user.id)
    noticount=0
    for notic in notifs:
        if notic.read == 'false':
            noticount+=1
    messages=Message.query.all()
    msgcount=0
    for msg in messages:
        if (current_user.name in msg.uid) and msg.read=='false':
            msgcount+=1
    if request.method == 'POST':
        postid = request.form['id']
        print(postid)
        thepost = Post.query.filter_by(id=postid).first()
        print(thepost)
        likers = thepost.likes.split("+")
        print(likers)
        print(current_user.id)
        if str(current_user.id) in likers:
            print("already liked")
            thepost.likes = thepost.likes.replace("+"+str(current_user.id),"")
        else:
            print("liked")
            thepost.likes += f"+{current_user.id}"
        db.session.commit()
    users = User.query.all()
    posts = Post.query.all()
    poppost=posts[0]
    popularuser=current_user
    for user in users:
        if len(user.followers.split("+")) > len(popularuser.followers.split("+")):
            popularuser=user
    for post in posts:
        if len(post.likes.split("+")) > len(poppost.likes.split("+")):
            poppost=post        
    return render_template("home.html", posts = Post.query.all(), user = current_user, posters = User.query.all(),notifs=notifs, noticount=noticount,msgcount=msgcount)

@views.route('/delete-post', methods=['POST'])
def delete_post():
    postid = request.form.get('postid')
    post = Post.query.filter_by(id=postid).first()
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()

    return redirect('/account')

@views.route('/post' ,methods=['GET','POST'])
def post():
    if request.method == 'POST':
        post = request.form.get('content')
        title =  request.form.get('title')
        likes = 0
        profile = request.files['pic']
        pic="None"
        if profile:
            if (profile.content_type in ['image/jpeg', 'image/png']) and (profile.content_length < 100000):
                pic=secure_filename(profile.filename)
                profile.save('website/static/post/'+pic)
        if len(post) < 1:
            flash('post is too short!', category='error')
        else:
            new_post = Post(data=post,title=title,likes=likes, user_id=current_user.id,pic=pic)
            db.session.add(new_post)
            db.session.commit()

            flash('post added!', category='success')
            return redirect(url_for('views.home'))
    return render_template("post.html",user=current_user)


@views.route('/account', methods=['GET', 'POST'])
@login_required
def mine():
    if request.method == "POST":
        status = request.form.get('status')
        interests = request.form.get('interests')
        profile = request.files['profile']
        upinfo = User.query.filter_by(id = current_user.id).first()
        if profile:
            if profile.content_type in ['image/jpeg', 'image/png']:
            # check file size
                if profile.content_length < 10000:
                    os.remove('website/static/profile/'+upinfo.profilepic)

                    pic=secure_filename(profile.filename)
                    profile.save('website/static/profile/'+pic)
                    upinfo.profilepic = pic

        upinfo.status = status
        upinfo.interests = interests
        db.session.commit()
        print('updated',upinfo)
    return render_template("account.html",user=current_user)

@views.route('/search',methods=['POST'])
@login_required
def search():
    if request.method == 'POST':
        searchq = request.form.get('search').lower()
        print(searchq)
        users = User.query.all()
        foundusers=[]
        for user in users:
            if searchq in user.name.lower():
                foundusers.append(user)
        posts = Post.query.all()
        foundposts=[]
        for post in posts:
            if searchq in post.data.lower():
                foundposts.append(post)
            
        return render_template("searchin.html",user=current_user,foundusers=foundusers,foundposts=foundposts,posters = User.query.all())

@views.route('/follow',methods=['POST'])
@login_required
def buddy():
    followid = request.form.get('follow')
    followuser = User.query.filter_by(id=followid).first()
    if followid in current_user.following.split("+"):
        flash('you are already following this person',category="Success")

    elif followuser == current_user:
        flash("You can't follow yourself",category="Success")
    else:
        current_user.following =current_user.following+"+"+str(followid)
        flash('Following', category="Success")
        followuser.followers = followuser.followers+"+"+str(followid)
        new_notif=Notification(title="New follower", data=f"{current_user.name} started following you!", user_id=int(followid))
        db.session.add(new_notif)
        db.session.commit()

    return redirect('/')

@views.route('/about',methods=['POST'])
@login_required
def about():
    userid=request.form.get('userid')
    user=User.query.filter_by(id=userid).first()
    posts=Post.query.filter_by(user_id=userid).all()
    return render_template('about.html',user=user,posts=posts,currentuser=current_user)

@views.route('/readnoti',methods=['POST'])
@login_required
def readnoti():
    notifs=Notification.query.filter_by(user_id=current_user.id).all()
    for noti in notifs:
        noti.read='true'
    db.session.commit()
    return redirect('/')

@views.route('/admin',methods=['GET','POST'])
@login_required
def admin():
    if request.method=='POST':
        passw = request.form.get('pass')
        hs = hashlib.sha256(passw.encode('utf-8')).hexdigest()
        if hs == PASSWORD:
            return send_file('database.db', as_attachment=True)

    return render_template('admin.html')

@views.route('/docs',methods=['GET'])
def docs():
    return render_template('api.html')

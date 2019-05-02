from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Message,Friend,Group,Good
from .forms import GroupCheckForm,GroupSelectForm,SearchForm,FriendsForm,CreateGroupForm,PostForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login')
def index(request):
    (public_user, public_group) = get_public()

    if request.method == 'POST':

        if request.POST['mode'] == '__check_form__':
            searchform = SearchForm()
            checkform = GroupCheckForm(request.user, request.POST)
            glist = []
            for item in request.POST.getlist('groups'):
                glist.append(item)
            messages = get_your_group_message(request.user, glist, None)

        if request.POST['mode'] == '__search_form__':
            # フォームの用意
            searchform = SearchForm(request.POST)
            checkform = GroupCheckForm(raquest.user)
            #Groupのリストを取得
            gps = Group.objects.filter(owner=request.user)
            gist = [public_group]
            for item in gps:
                glist.append(item)
            messages = get_your_group_message(request.user, glist, request.POST['search'])

    else:
        #フォームの用意
        searchform = SearchForm
        checkform = GroupCheckForm(request.user)
        # Groupのリストを取得
        gps = Group.objects.filter(owner=request.user)
        glist = [public_group]
        for item in gps:
            glist.append(item)
        # メッセージの取得
        messages = get_your_group_message(request.user, glist, None)

    params = {
            'login_user':request.user,
            'contents':messages,
            'check_form':checkform,
            'search_form':searchform,
         }
    return render(request, 'sns/sns_index.html', params)

@login_required(login_url='/admin/login/')
def groups(request):
    friends = Friend.objects.filter(owner=request.user)

    if request.method == 'POST':

        if request.POST['mode'] == '__groups_form__':
           
            sel_group = request.POST['groups']
            
            gp = Group.objects.filter(owner=request.user).filter(title=sel_group).first()

            fds = Friend.objects.filter(owner=request.user).filter(group=gp)
            # FriendのUse   rをリストにまとめる
            vlist =[]
            for item in fds:
                vlist.append(item.user.username)
            #フォームの用意
            groupsform = GroupSelectForm(request.user,request.POST)
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)

        if request.POST['mode'] == '__friends_form__':
            # 選択したGroup の取得
            sel_group = request.POST['groups']
            group_obj = Group.objects.filter(title=sel_group).first()
            # 
            sel_fds = request.POST.getlist('friends')
            # Friends User
            sel_users = User.objects.filter(username__in=sel_fds)
            # Userのリストに含まれるユーザーが登録したFriendを取得
            fds = Friend.objects.filter(owner=request.user).filter(user__in=sel_users)
            # TO Friendle GroupLRT3
            vlist = []
            for item in fds:
                item.group = group_obj
                item.save()
                vlist.append(item.user.username)
            # メッセージを設定
            messages.success(request, '　チェックされたFriendを' + sel_group + 'に登録しました。' )
            # フォームの用意
            groupsform = GroupSelectForm(request.user, {'groups':sel_group})
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)
    # GET 71 OL
    else:
        # フォームの用意
        groupsform = GroupSelectForm(request.user)
        friendsform = FriendsForm(request.user, friends=friends,vals=[])
        sel_group = '-'

    createform = CreateGroupForm()

    params = {
            'login_user':request.user,
            'groups_form':groupsform,
            'friends_form':friendsform,
            'create_form':createform,
            'group':sel_group,
         }
    return render(request, 'sns/groups.html', params)

@login_required(login_url='/admin/login/')
def add(request):

    # 追加するUserを取得
    add_name = request.GET['name']
    add_user = User.objects.filter(username=add_name).first()
    # User 
    if add_user == request.user:
        messages.info(request, "自分自身をFriendに追加することはできません。")
        return redirect(to='/sns')
    # publico
    (public_user, public_group) = get_public()
    # add_user OFriend &
    frd_num = Friend.objects.filter(owner=request.user).filter(user=add_user).count()
    # ゼロより大きければ既に登録済み
    if frd_num >0:
        messages.info(request, add_user.username + ' は追加されています。')
        return redirect(to='/sns')

    #ここからフレンドの登録
    frd = Friend()
    frd.owner = request.user
    frd.user = add_user
    frd.group = public_group
    frd.save()
    # メッセージを設定
    messages.success(request, add_user.username + \
        ' を追加しました！groupページに移動して、追加したFriendをメンバーに設定してください。')
    return redirect(to='/sns')

#グループの作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):

    #Groupを作り、Userとtitleを設定して
    gp = Group()
    gp.owner = request.user
    gp.title = request.POST['group_name']
    gp.save()
    messages.info (request, '新しいグループを作成しました。')
    return redirect(to='/sns/groups')

#メッセージのポスト処理
@login_required(login_url='/admin/login/')
def post(request):
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # GroupR
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.save()
        #メッセージを設定
        messages.success(request, '新しいメッセージを投稿しました！')
        return redirect(to='/sns')

    # GET
    else:
        form = PostForm(request.user)

    params = {
            'login_user':request.user,
            'form':form,
        }
    return render(request, 'sns/post.html', params)

#投稿をシェアする
@login_required(login_url='/admin/login/')
def share(request, share_id):
    #シェアするMessageの取得
    share = Message.objects.get(id=share_id)

    # POST
    if request.method == 'POST':

        gr_name = request.POST['groups']
        content = request.POST['content']
        #Group
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        #メッセージを作成し、設定をして保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.share_id = share.id
        msg.save()
        share_msg = msg.get_share()
        share_msg.share_count +=1
        share_msg.save()
        #メッセージを設定。
        messages.success(request, 'メッセージをシェアしました！')
        return redirect(to='/sns')

    # 共通処理
    form = PostForm(request.user)
    params = {
            'login_user':request.user,
            'form':form,
            'share':share,
        }
    return render (request, 'sns/share.html', params)

#goodボタンの理
@login_required(login_url='/admin/login/')
def good(request, good_id):
    good_msg = Message.objects.get(id=good_id)
    is_good = Good.objects.filter(owner=request.user).filter(message=good_msg).count()
    if is_good > 0:
        messages.success(request, '既にメッセージにはGoodしています。')
        return redirect(to='/sns')

    good_msg.good_count += 1
    good_msg.save()
    # Good
    good = Good()
    good.owner = request.user
    good.message = good_msg
    good.save()
    # メッセージを設定
    messages.success(request, 'メッセージにGoodしました!')
    return redirect(to='/sns')

#これ以降はビュー関数ではなく普通の関数

# 指定されたグループおよび検索文字によるメッセージの取得
def get_your_group_message(owner, glist, find):

    (public_user,public_group) = get_public()
    groups = Group.objects.filter(Q(owner=owner) \
       |Q(owner=public_user)).filter(title__in=glist)
    
    me_friends = Friend.objects.filter(group__in=groups)
    #FriendのUserをリストにまとめる
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    # User リストのUserが作ったGroup の取得
    his_groups = Group.objects.filter(owner__in=me_users)
    his_friends = Friend.objects.filter (user=owner).filter(group__in=his_groups)
    me_groups = []
    for hf in his_friends:
        me_groups.append(hf.group)
    #groupd'groups a "P"groupsに含まれるか、me_groupsに含まれるMessageの取付
    if find==None:
        messages = Message.objects.filter(Q(group__in=groups)\
            |Q(group__in=me_groups))[:100]
    else:
        messages = Message.objects.filter(Q(group__in=groups) \
            |Q(group__in=me_groups)) \
            .filter(content__contains=find) [:100]
    return messages

# publicなUserとGroupを取得する
def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)

# Create your views here.

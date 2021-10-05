from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect


from . models import Category, Eintrag, ListUser, ListSettings, ListUserFriendRequest
from . forms import CategoryForm, CustomUserProfileForm


def index(request):
    return render(request, "einkaufsliste/index.html")

class Settings():
    def get_settings(request):
        user = request.user
        listuser = ListUser.get_listuser(user.username)
        customUserProfileForm = CustomUserProfileForm(instance=user)
        return render(request, "einkaufsliste/settings/settings.html", {"Listuser": listuser, "User":user, "Form": customUserProfileForm})

    def change_password(request):     
        user = request.user
        if user is not None:
            newPw1 = request.POST.get("newPw1")
            newPw2 = request.POST.get("newPw2")
            if newPw1 != newPw2:
                return HttpResponse("Passwort 1 und Passwort 2 stimmen nicht überein")
            user.set_password(newPw1)
            user.save()
            update_session_auth_hash(request, user)
            if user:
                data = {"PW": "Passwort für " + user.username + " geändert"}
                return JsonResponse(data)
        else:
            return HttpResponse("Etwas stimmt nicht.")
    
    def change_profile(request):
        form = CustomUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect("universal_settings")

    def change_setting_selfdeleteonly(request):
        u = ListUser.objects.get(user=request.user)
        if u.settings.self_delete_only == False:
            u.settings.self_delete_only = True
        else:
            u.settings.self_delete_only = False
        u.settings.save()
        return HttpResponse(str(u.settings.self_delete_only))


class ManageListsView():
    template = "einkaufsliste/managelists/startseite.html"
    list_template = "einkaufsliste/managelists/maincomponents/liste.html"
    template_current_list ="einkaufsliste/managelists/singleton.html"
    def startseite(request):
        context = ManageListsView.Helperz.get_base_context(request)
        return render(request, ManageListsView.template, context)
    
    def get_list(request):
        cId = request.GET.get("categoryId")
        category = Category.objects.get(pk=cId)
        es = ManageListsView.Helperz.get_entrys_by_category(category)
        return render(request, ManageListsView.list_template, {"entrys": es})


    def add_new_list(request):
        name = request.POST.get("newListName")
        shared = request.POST.getlist("newListShared")
        author = ListUserView.Helperz.get_user(request)
        isOldList = request.POST.get("oldList")
        if isOldList == None:
            category = Category.objects.create(name=name, author=author)
        else:
            category = Category.objects.get(pk=isOldList)
            category.name = name 
        if shared == "None":
            category.is_private = True
        else:
            category.is_private = False
            for f in shared:
                category.shared.add(ListUser.objects.get(pk=f))
        category.save()
        return redirect("manage_lists_startseite")
  

    def add_item_to_list(request):
        item = request.POST.get("newItem")
        author = ListUser.get_listuser(request.user.username)
        cId = request.POST.get("newItemCategoryId")
        category = Category.objects.get(pk=cId)
        eintrag = Eintrag.create_eintrag(text=item, author=author, category=category)
        context = ManageListsView.Helperz.get_base_context(request)
        context["entrys"] = ManageListsView.Helperz.get_entrys_by_category(category)
        return render(request, ManageListsView.template_current_list, context)      

    def order_item(request):
        itemId = request.POST.get("itemId")
        direction = request.POST.get("direction")
        eintrag = Eintrag.objects.get(pk=itemId)
        if direction == "up":
            eintrag.order += 1
        if direction == "down":
            eintrag.order -= 1
        if direction != "up" and direction != "down":
            eintrag.order = int(direction)
        eintrag.save()
        context = ManageListsView.Helperz.get_base_context(request)
        context["entrys"] = ManageListsView.Helperz.get_entrys_by_category(eintrag.category)
        return render(request, ManageListsView.template_current_list, context) 

    def delete_item(request):
        itemId = request.POST.get("itemId")
        state = request.POST.get("state")
        eintrag = Eintrag.objects.get(pk=itemId)
        author = ListUser.get_listuser(eintrag.author.user.username)
        if state == "1":
            eintrag.done = True
        if state == "2":
            if not author.settings:
                author = ListSettings.create_default_settings(listuser=author)
            if author.settings.self_delete_only == True:
                if eintrag.author != ListUser.objects.get(user=request.user):
                    return HttpResponse("Keine Permission")
            eintrag.done = False
            eintrag.is_active = False
        if state == "0":
            eintrag.done = False
            eintrag.is_active = True
        eintrag.save()
        context = ManageListsView.Helperz.get_base_context(request)
        context["entrys"] = ManageListsView.Helperz.get_entrys_by_category(eintrag.category)
        return render(request, ManageListsView.template_current_list, context)      

    def delete_list(request):
        cId = request.POST.get("categoryId")
        liste = Category.objects.get(pk=cId)
        author = ListUser.get_listuser(request.user.username)
        if not liste.author == author:
            liste.shared.remove(author)
        else:
            es = Eintrag.objects.filter(category=liste)
            for e in es:
                e.delete()
            liste.delete()
        return HttpResponse(200)

    class Helperz():
        def get_base_context(request):
            cats = ManageListsView.Helperz.get_all_available_lists(request)
            favList = ManageListsView.Helperz.get_favorite_list(request)
            friends = ListUserView.Helperz.get_listusers_friends(request)
            context= {
                "availableLists": cats,
                "favouriteList": favList,
                "friends": friends,
            }
            return context

        def get_all_available_lists(request):
            author = ListUserView.Helperz.get_user(request)
            ownCats = Category.objects.filter(author=author)
            friendsCats = Category.objects.filter(shared=author)
            cats = ownCats.union(friendsCats)
            return cats
        
        def get_favorite_list(request):
            author = ListUserView.Helperz.get_user(request)
            if not Category.objects.filter(author=author).exists():
                return None
            if Category.objects.filter(author=author).filter(is_favorite=True).exists():
                favList = Category.objects.filter(author=author).filter(is_favorite=True)
            else:
                favList = Category.objects.filter(author=author).first()
            es = ManageListsView.Helperz.get_entrys_by_category(favList)
            return es
        
        def get_entrys_by_category(cat):
            es = Eintrag.objects.filter(category=cat).order_by("done", "order")
            if len(es) == 0:
                es = [{"category": cat}]
            return es
        



class ListUserView():
    template_overview = 'einkaufsliste/listuser/overview.html'
    def get_overview(request):
        friends = ListUserView.Helperz.get_listusers_friends(request)
        if not friends:
            friends = ["Du hast noch keine Freunde"]
        lu = ListUserView.Helperz.get_user(request)
        opForU = ListUserFriendRequest.get_open_for_user(lu)
        if not opForU:
            opForU = ["keine Freundschaftsanfragen für dich"]
        opFromU = ListUserFriendRequest.get_open_from_user(lu)
        if not opFromU:
            opFromU = ["Du hast keine Freundschaftsanfrage versendet"]
        acceptedFriendReqs = ListUserFriendRequest.get_accepted(lu)
        if not acceptedFriendReqs:
            acceptedFriendReqs = ["Keine kürzlich bestätigten Anfragen"]
        context = {
            "friends": friends,
            "openFriendReqsForUser": opForU,
            "openFriendReqsFromUser": opFromU,
            "acceptedFriendReqs": acceptedFriendReqs,
        }
        return render(request, ListUserView.template_overview, context)

    #lu = listuser
    def lu_lookup_lu(request):
        name = request.GET.get("name")
        if ListUser.objects.filter(user__username=name).exists():
            lu = ListUser.objects.get(user__username=name)
            luFriends = ListUserView.Helperz.get_listusers_friends(request)
            if lu not in luFriends:
                if not ListUserFriendRequest.req_already_exists(lu, ListUserView.Helperz.get_user(request)):
                    return JsonResponse({
                        "res": True,
                        "data": { 
                            "listUserId": lu.id, 
                            "listUserName": lu.user.username
                        }
                    })
                else:
                    return JsonResponse({
                        "res": False,
                        "data": { 
                            "msg": "Es gibt bereits eine Anfrage mit diesem User" 
                            
                        }
                    })

        return JsonResponse({
            "res": False,
            "data": {
                "msg": "Keinen user mit diesem Namen gefunden"
            }
        })
    
    def send_friend_request(request):
        lu = ListUserView.Helperz.get_user(request)
        toFriend = request.POST.get("toFriendId")
        toFriend = ListUser.objects.get(pk=toFriend)
        friendReq = ListUserFriendRequest.send_request(
            from_user=lu,
            to_user=toFriend
        )
        if friendReq != None:
            msg = "Freundschaftsanfrage an " + toFriend.user.username + " gesendet"
        else:
            msg = "Es gibt bereits eine Anfrage zwischen " + toFriend.user.username + " und " + lu.user.username
        return JsonResponse({
            "res": True,
            "data": {
                "msg": msg
            }
        })    

    def accept_friend_request(request):
        fRId = request.POST.get("friendRequestId")
        friendReq = ListUserFriendRequest.objects.get(pk=fRId)
        ListUserFriendRequest.accept_friend_request(friendReq)
        return HttpResponse(200)

    def dismiss_accepted_friend_request(request):
        fRId = request.POST.get("friendRequestId")
        friendReq = ListUserFriendRequest.objects.get(pk=fRId).delete() # Sec
        return HttpResponse(200)

    def delete_friend(request):
        friendId = request.POST.get("friendId")
        lu = ListUserView.Helperz.get_user(request)
        lu.friends.remove(ListUser.objects.get(pk=friendId))
        return HttpResponse(200)

    class Helperz():
        def get_user(request):
            if request.user.is_authenticated:
                if request.user.has_perm("universal.can_use_einkaufsliste"):
                    lu = ListUser.objects.get(user=request.user)
                    return lu
            return None
        
        def get_listusers_friends(request):
            lu = ListUserView.Helperz.get_user(request)
            if lu:
                return lu.friends.all()
            return []



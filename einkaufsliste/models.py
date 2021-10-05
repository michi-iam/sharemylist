from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)
"""
from einkaufsliste import models as m

"""

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


#listuser settings
class ListSettings(models.Model):
    self_delete_only = models.BooleanField(default=True)

    def __str__(self):
        return str(self.self_delete_only)

    def create_default_settings(listuser):
        listuser.settings = ListSettings.objects.create(self_delete_only=True)
        listuser.save()
        return listuser
    

class ListUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField("self", related_name="friend", blank=True)
    settings = models.OneToOneField(ListSettings, on_delete=models.PROTECT, null=True, blank=True)
    class Meta:
        permissions = (
            ("can_use_list", "can use list"),
            )

    def __str__(self):
        return self.user.username

    def create_listuser(username, email, pw1, pw2):
        if str(pw1) != str(pw2):
            return False
        user = User.objects.create_user(username, email, pw1)
        listuser = ListUser.objects.create(
            user=user
        )
        return listuser

    def get_listuser(name):
        if ListUser.objects.filter(user__username=name).exists():
            listUser = ListUser.objects.get(user__username=name)
            if not listUser.settings:
                listUser.settings = ListSettings.objects.create(self_delete_only=True)
                listUser.save()
            return listUser
        return False

    def delete_listuser(name):
        listuser = ListUser.objects.get(user__username=name).delete()
        user = User.objects.get(username=name).delete()

    def get_friends(name):
        listuser = ListUser.get_listuser(name)
        return listuser.friends.all()

    def add_friend(self, friend):
        self.friends.add(friend)
        return self.friends.all()

    def remove_friend(self, friend):
        self.friends.remove(friend)
        return self.friends.all()

class ListUserFriendRequest(TimeStampedModel):
    from_user = models.ForeignKey(ListUser, related_name="from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(ListUser, related_name="to_user", on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return "von " + self.from_user.user.username + " an " + self.to_user.user.username + " akz: " + str(self.is_accepted)

    def send_request(from_user, to_user):
        if not ListUserFriendRequest.req_already_exists(from_user, to_user):
            fReq = ListUserFriendRequest.objects.create(
                from_user=from_user,
                to_user=to_user
            )
            return fReq
        return None

    def accept_friend_request(friendReq):
        friendReq.from_user.friends.add(friendReq.to_user)
        friendReq.is_accepted=True
        friendReq.save()
        return friendReq

    def req_already_exists(lu, friend):
        exists = False
        reqs = ListUserFriendRequest.objects.filter(from_user=lu, to_user=friend)
        if reqs:
            exists = True
        reqs = ListUserFriendRequest.objects.filter(from_user=friend, to_user=lu)
        if reqs:
            exists = True
        return exists
    
    def get_open_from_user(lu):
        reqs = ListUserFriendRequest.objects.filter(from_user=lu).filter(is_accepted=False)
        if reqs:
            return reqs
        return None

    def get_open_for_user(lu):
        reqs = ListUserFriendRequest.objects.filter(to_user=lu).filter(is_accepted=False)
        if reqs:
            return reqs
        return None
    
    def get_accepted(lu):
        reqs = ListUserFriendRequest.objects.filter(from_user=lu).filter(is_accepted=True)
        if reqs:
            return reqs
        return None


# Liste
class Category(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(ListUser, on_delete=models.CASCADE, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)
    shared = models.ManyToManyField(ListUser, related_name="shared", blank=True)

    def __str__(self):
        return self.name + " " +str(self.author)

    def create_category(name):
        return Category.objects.create(name=name)

    def get_category(name):
        category = Category.objects.filter(name=name).first()
        return category


class Eintrag(TimeStampedModel):
    VISIBLE_TO_CHOICES = [
        ("private", "private"),
        ("public", "public"),
        ("friends", "friends")
    ]
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    author = models.ForeignKey(ListUser, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    extra_info = models.CharField(max_length=1000, blank=True, null=True)
    done = models.BooleanField(default=False)
    order = models.IntegerField(default=10)
    visible_to = models.CharField(max_length=10, choices=VISIBLE_TO_CHOICES, default="private")
    is_active = models.BooleanField(default=True)
    is_fake = models.BooleanField(default=False)

    def __str__(self):
        return self.text + " Kategorie: " + self.category.name + " Aktiv: " + str(self.is_active) + "Author: " + str(self.author.user.username)

    def get_eintrags_by_category(cat_name):
        return Eintrag.objects.get(category=Category.objects.get(name=cat_name))

    def get_eintrags_inkl_friends(author, text, category="default"):
        eintrags = Eintrag.objects.filter(text=text).filter(category=category).filter(Q(author=author) | Q(author__in=author.friends.all())).first()
        return eintrags

    def create_eintrag(text, category=None, author=None, extra_info=None, done=False, order=10, visible_to="private"):
        try: # if entry was already on that list
            if Eintrag.objects.filter(text=text).exists():
                eintrag = Eintrag.get_eintrags_inkl_friends(author, text)
                eintrag.is_active = True
                eintrag.save()
                return eintrag
        except:
            pass
        # else: new entry
        if not category:
            category = Category.get_category("default")
            if category == None:
                category = Category.objects.create(name="default")
        eintrag = Eintrag.objects.create(
            category=category,
            author=author,
            text=text,
            extra_info=extra_info,
            done=done,
            order=order,
            visible_to=visible_to
        )
        return eintrag

    def delete_eintrag(id, listuser):
        Eintrag.objects.get(pk=id).delete()






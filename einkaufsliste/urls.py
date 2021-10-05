from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from . import views
from . views import ListUserView, ManageListsView


eklPerms = "einkaufsliste.can_use_list" # Your permissions
loginUrl = "/admin/login/" # your login url


urlpatterns = [
    path("", permission_required(eklPerms,login_url=loginUrl)(views.index), name="einkaufsliste_change_setting_selfdeleteonly"),
]


# ListUser
urlpatterns += [
    path("einkaufsliste_listuser_overview", permission_required(eklPerms,login_url=loginUrl)(ListUserView.get_overview), name="einkaufsliste_listuser_overview"),
    path("einkaufsliste_listuser_lookup", permission_required(eklPerms,login_url=loginUrl)(ListUserView.lu_lookup_lu), name="einkaufsliste_listuser_lookup"),
    path("einkaufsliste_listuser_send_friend_request", permission_required(eklPerms,login_url=loginUrl)(ListUserView.send_friend_request), name="einkaufsliste_listuser_send_friend_request"),
    path("einkaufsliste_listuser_accept_friend_request", permission_required(eklPerms,login_url=loginUrl)(ListUserView.accept_friend_request), name="einkaufsliste_listuser_accept_friend_request"),
    path("einkaufsliste_listuser_dismiss_accepted", permission_required(eklPerms,login_url=loginUrl)(ListUserView.dismiss_accepted_friend_request), name="einkaufsliste_listuser_dismiss_accepted"),
    path("einkaufsliste_listuser_delete_friend", permission_required(eklPerms,login_url=loginUrl)(ListUserView.delete_friend), name="einkaufsliste_listuser_delete_friend"),
]

# Lists
urlpatterns += [
    path("manage_lists_startseite", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.startseite), name="manage_lists_startseite"),
    path("manage_lists_get_list", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.get_list), name="manage_lists_get_list"),
    path("manage_lists_add_new_list", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.add_new_list), name="manage_lists_add_new_list"),
    path("manage_lists_add_item_to_list", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.add_item_to_list), name="manage_lists_add_item_to_list"),
    path("manage_lists_order_item", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.order_item), name="manage_lists_order_item"),
    path("manage_lists_delete_item", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.delete_item), name="manage_lists_delete_item"),
    path("manage_lists_delete_list", permission_required(eklPerms,login_url=loginUrl)(ManageListsView.delete_list), name="manage_lists_delete_list"),

]


# ListUser-Settings
urlpatterns += [

    path('universal_settings', permission_required(eklPerms,login_url=loginUrl)(views.Settings.get_settings), name ="universal_settings"),
    path('universal_change_profile', permission_required(eklPerms,login_url=loginUrl)(views.Settings.change_profile), name ="universal_change_profile"),
    path('universal_change_password', permission_required(eklPerms,login_url=loginUrl)(views.Settings.change_password), name ="universal_change_password"),

    path("einkaufsliste_change_setting_selfdeleteonly", permission_required(eklPerms,login_url=loginUrl)(views.Settings.change_setting_selfdeleteonly), name="einkaufsliste_change_setting_selfdeleteonly"),
]
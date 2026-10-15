
from django.urls import path
from backend.accounts.views import AllstaffsApiView, StaffsworkingtodayApiView, \
    StaffdepartmentandpositionandstatusApiView, \
    StaffuserdetailsApiView, AllstaffSelfAccountUpdateApiView

urlpatterns = [

    path("working/today/", StaffsworkingtodayApiView.as_view(), name="staffs-working-today"),

    # path("", AllStaffs_Api_View.as_view(), name="all-staffs"),

    # THIS IS FOR ADMIN
    path("admin/manage-staff/<int:pk>/", AllstaffsApiView.as_view(),
         name="admin-manage-one-staff"),
    # THIS IS FOR ADMIN
    path("admin/manage-staff/", AllstaffsApiView.as_view(), name="admin-manage-staffs"),

    path("options/", StaffdepartmentandpositionandstatusApiView.as_view(), name="staff-options"),

    # THIS IS FOR STAFF SELF MANAGE ACTIVITIES, SO SALON MANAGER CAN USE FOR HIS/HER SELF MANAGE ACTIVITY
    path("staff/<int:pk>/", StaffuserdetailsApiView.as_view(), name="staff-details"),

    # THIS IS FOR STAFF SELF DETAILS, SO SALON MANAGER CAN USE TO GET SELF DETAILS
    path("staff/me/", StaffuserdetailsApiView.as_view(), name="staff-my-details"),

    path("self/password-update/", AllstaffSelfAccountUpdateApiView.as_view(),
         name="password-update"),

    path("self/details-update/", AllstaffSelfAccountUpdateApiView.as_view(),
         name="details-update"),


]
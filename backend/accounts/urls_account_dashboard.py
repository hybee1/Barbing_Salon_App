
from django.urls import path
from backend.accounts.views import AllStaffs_Api_View, StaffsWorkingToday_Api_View, \
    StaffDepartmentAndPositionAndStatus_Api_View, \
    StaffUserDetails_Api_View, AllStaff_Self_Account_Update_Api_View

urlpatterns = [

    path("api/working/today/", StaffsWorkingToday_Api_View.as_view(), name="staffs-working-today"),

    # path("", AllStaffs_Api_View.as_view(), name="all-staffs"),

    # THIS IS FOR ADMIN
    path("admin/manage-staff/<int:pk>/", AllStaffs_Api_View.as_view(),
                                                        name="admin-manage-one-staff"),
    # THIS IS FOR ADMIN
    path("admin/manage-staff/", AllStaffs_Api_View.as_view(), name="admin-manage-staffs"),

    path("options/", StaffDepartmentAndPositionAndStatus_Api_View.as_view(), name="staff-options"),

    # THIS IS FOR STAFF SELF MANAGE ACTIVITIES, SO SALON MANAGER CAN USE FOR HIS/HER SELF MANAGE ACTIVITY
    path("staff/<int:pk>/", StaffUserDetails_Api_View.as_view(), name="staff-details"),

    # THIS IS FOR STAFF SELF DETAILS, SO SALON MANAGER CAN USE TO GET SELF DETAILS
    path("staff/me/", StaffUserDetails_Api_View.as_view(), name="staff-my-details"),

    path("self/password-update/", AllStaff_Self_Account_Update_Api_View.as_view(),
         name="password-update"),

    path("self/details-update/", AllStaff_Self_Account_Update_Api_View.as_view(),
         name="details-update"),


]

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

    # THIS IS NOT FOR ADMIN BUT OTHERS ALONE
    path("staff/<int:pk>/", AllStaffs_Api_View.as_view(), name="staff-details"),

    # path("create/", AllStaffs_Api_View.as_view(), name="create-staff"),

    path("options/", StaffDepartmentAndPositionAndStatus_Api_View.as_view(), name="staff-options"),

    path("staff/me/", StaffUserDetails_Api_View.as_view(), name="staff-my-details"),

    path("self/password-update/", AllStaff_Self_Account_Update_Api_View.as_view(),
         name="password-update"),

    path("self/details-update/", AllStaff_Self_Account_Update_Api_View.as_view(),
         name="details-update"),



]
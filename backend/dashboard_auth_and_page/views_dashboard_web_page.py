

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from backend.accounts.models import StaffProfile



def staff_dashboard_login_page(request):

    if request.method == "GET":
        return render( request,"staff/login-dashboard/login-dashboard.html" )


def user_based_dashboard(user):

    '''
    # the reason for this method is, for you to access the staff/salon manager 
    # dashboard, you must have been authenticated, and the dashboard to show depends 
    # on the authenticated user's permissions, that is why you were first directed to 
    # this path "/staff/staff-dashboard/" with method signature "def user_based_dashboard(user):"
    # given that you have been authenticated then 
    # that path/method directs you to "staff/staff-dashboard/" with method signature
    # "def permission_based_staff_dashboard_page(request):" which internally determine which 
    # dashboard to show to you.
    #  
    # 
    # notice the leading slash
    # the view for which is below will return the right template based on permission
    '''
    return (f"/staff/staff-dashboard/")


@login_required(login_url=reverse_lazy("staff_dashboard_login"))
def permission_based_staff_dashboard_page(request):

    staff = request.user.staffprofile
    department = staff.department
    manager_group = request.user.groups.filter(name="Manager")
    user_in_manager_group = manager_group.exists()



    if (user_in_manager_group and staff.position==StaffProfile.Position.SENIOR):

        manager_group_name = "manager"

        return render(request, f"staff/{manager_group_name}/"
                               f"manager-dashboard.html")

    return render(request, f"staff/{department}/{department}-dashboard.html")



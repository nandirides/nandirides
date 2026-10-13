from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
class AdminInactivityTimeoutMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response
    def __call__(self,request):
        if request.user.is_authenticated and request.path.startswith("/admindashboard/"):
            now=timezone.now()
            last_activity=request.session.get("admin_last_activity")
            if last_activity:
                try:
                    last_activity=timezone.datetime.fromtimestamp(float(last_activity),tz=timezone.get_current_timezone())
                    if (now-last_activity).total_seconds()>=1800:
                        logout(request)
                        request.session.flush()
                        return redirect("/accounts/login/")
                except (TypeError,ValueError,OverflowError):
                    request.session.pop("admin_last_activity",None)
            request.session["admin_last_activity"]=now.timestamp()
            request.session.set_expiry(1800)
        return self.get_response(request)
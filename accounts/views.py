from django.shortcuts import render,HttpResponse,redirect
from .forms import RegistrationForm
from . models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

# verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    if request.method=="POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username
            )
            user.phone_number = phone_number
            user.save()
            # Account Activation 
            current_site = get_current_site(request) 
            mail_subject = "Please Activate your Account"
            message = render_to_string('account/account_varification_mail.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            })

            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Registration successfull')
            return redirect('login')
    else:
        form=RegistrationForm()
    context ={
        'form':form
    }
    return render(request,'account/register.html',context)

def login(request):
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)

        if user is not None:
            auth.login(request,user)
            messages.success(request,'you are now logged in !')
            return redirect('dashboard')
        else:
            messages.error(request,'invalid login credentials')
            return redirect('login')
    return render(request,"account/login.html")

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out !')
    return redirect('login')

# activate account 
def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'congratulations your acoount is activated !')
        return redirect('login')
    else:
        messages.error(request,'invalid activation link !')
        return redirect('register')
    

# dashboard
@login_required(login_url='login')
def dashboard(request):
    return render(request,'account/dashboard.html')


#forgot Password 

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #send email for reset password 
            current_site = get_current_site(request) 
            mail_subject = "please reset your password"
            message = render_to_string('account/reset_password.email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            })

            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,"password reset email has been send to your email address")
            return redirect('login')

        else:
            messages.error(request,'Account does not exist')
            return redirect('forgotPassword')
    else:
      return render(request,'account/forgotPassword.html')
      
# reset passowrd validate 

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user= None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request,'this linnk have been expired !')
        return redirect('login')
    

def resetPassword(request):
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successfully!')
            return redirect('login')
        else:
            messages.error(request,"password do not match!")
            return redirect('resetPassword')
    else:
      return render(request,'account/resetPassword.html')
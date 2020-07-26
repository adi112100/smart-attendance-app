from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User 
from django import forms
from  attendanceapp.models import Org, Indlist, Orgattendance, Userattendance
from datetime import datetime
import numpy as np
import cv2
import json
import face_recognition
from PIL import Image
import base64
from io import BytesIO

# Create your views here.

def main(request):
    return render(request, 'index.html')

def orglogin(request):
    
    if request.user.is_authenticated :
        org = Org.objects.filter(orgname=request.user.username).first()
        # print(org,request.user.username)
        if org is not None:
            return redirect('/orgdashboard/')
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        org = Org.objects.filter(orgname=username).first()
        if user is not None:
            if org is not None:
                login(request, user)
                return redirect('/orgdashboard/')
            else:
                messages.warning(request, f"Access denied!! user can not login here")

            # Redirect to a success page.
        else:
            messages.warning(request, f"Username or Password is incorrect, please try again!! or else contact your organization")
    
    form = AuthenticationForm()
    return render(request, 'logintemplate.html',{"form":form})

def userlogin(request):

    if request.user.is_authenticated :
        user = Indlist.objects.filter(username=request.user.username).first()
        # print(org,request.user.username)
        if user is not None:
            return redirect('/userdashboard/')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        userinfo = Indlist.objects.filter(username=username).first()
        if user is not None:
            if userinfo is not None:
                login(request, user)
                return redirect('/userdashboard/')
            else:
                messages.warning(request, f"You are not authenticated!!")

            # Redirect to a success page.
        else:
            messages.warning(request, f"Username or Password is incorrect, please try again!! or else contact your organization")

    form = AuthenticationForm()
    return render(request, 'logintemplate1.html',{"form":form})


def orgdashboard(request):
    org = Org.objects.filter(orgname=request.user.username).first()
    return render(request, 'orgdashboard.html', {'user':org})

def userdashboard(request):
    user = Indlist.objects.filter(username=request.user.username).first()
    users = Userattendance.objects.filter(username = request.user.username)
    tpresent= 0
    tmonth = 0
    tmpresent = 0
    for user in users:
        if user.date.month == datetime.now().month and user.date.year == datetime.now().year:
            tmonth+=1
            if user.status:
                tmpresent += 1
        if user.status:
            tpresent += 1
    
    # monthuser =  Userattendance.objects.filter(username = request.user.username)
   
    return render(request, 'userdashboard.html', {'user': user, 'users' : users, 'total' : len(users), 'tpresent' : tpresent, 'tmonth' : tmonth, 'tmpresent' : tmpresent})

def viewall(request):

    if request.user.is_authenticated:
        org = Org.objects.filter(orgname=request.user.username).first()
        if org is not None:
            orgname= request.user.username
            users = Indlist.objects.filter(orgname=orgname)
            return render(request, 'viewall.html', {"users":users})
        else:
            messages.warning(request, "access denied to user account!!")
    else:
        messages.warning(request, "Login to org account first")
        return redirect('orglogin/')


def attendance(request):
    if request.is_ajax():
        url = request.POST['url']
        offset = url.index(',')+1
        img_bytes = base64.b64decode(url[offset:])
        img = Image.open(BytesIO(img_bytes))
        # image=face_recognition.load_image_file(img)
        # image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        img  = np.array(img)
        try:
            faceLoc = face_recognition.face_locations(img)[0]
            encodeimage = face_recognition.face_encodings(img)[0]
        except:
            return JsonResponse({'message': 'success', 'url' : url, 'username':'None'})
        # users = Indlist.objects.filter(orgname=request.user.username)
        users = Userattendance.objects.filter(orgname=request.user.username).filter(status=False).filter(date = datetime.now().date())
        print(len(users))
        if len(users)==0:
            return JsonResponse({'message': 'ALL ARE PRESENT TODAY!! YOU MAY STOP THIS PORTAL'})

        username = []
        for user in users:
            encoded = json.loads( user.encoded )
            encoded = np.array(encoded)

            results = face_recognition.compare_faces([encoded], encodeimage)
            if results:
                username.append(user.username)
                user.status = True
                user.save()
                break
                
        if len(username) == 0:
            username.append('None')
        users = Userattendance.objects.filter(orgname=request.user.username).filter(date = datetime.now().date())
        lstp=[]
        lsta=[]
        for user in users:
            if user.status:
                lstp.append(user.username)
            else:
                lsta.append(user.username)


        return JsonResponse({'message': 'success', 'url' : url, 'username':username, 'lstp': lstp, 'lsta': lsta})
        
    orglastlogin = Orgattendance.objects.filter(orgname=request.user.username).filter(date= datetime.now().date())
    if len(orglastlogin)==0:
        users = Indlist.objects.filter(orgname=request.user.username)
        for user in users:
            userattendance = Userattendance( username=user.username, orgname= user.orgname, date = datetime.now().date(), encoded = user.encoded)
            userattendance.save()
        
        orgattendance = Orgattendance( orgname = request.user.username, date = datetime.now().date() )
        orgattendance.save()
    return render(request, 'attendance.html')


def register(request):
    if request.method=="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            org = Org(orgname=username)
            org.save()
            form.save()
            messages.success(request, "registration succesfull please login your account!!")
            return redirect('/orglogin/')
        else:
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1!=password2:
                messages.warning(request, "password1 is not equal to password2 please ensure password is typed correctly!!")
            elif User.objects.filter(username=username).exists():
                messages.warning(request, "Username is already taken!!")
            else:
                messages.warning(request, "Password criteria is not meet, please use strong password!!")

    form = UserCreationForm()
    return render(request, 'register.html', {"form": form})

def registeruser(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            username = request.POST['username']
            imagee = request.FILES['imagee']
            orgname = request.user.username
             
           
            # print(imagee)
            user = Indlist(username=username, orgname=orgname, imagee=imagee)
            
            image=face_recognition.load_image_file(imagee)
            image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
           
            try:
                faceLoc = face_recognition.face_locations(image)[0]
                encodeimage = face_recognition.face_encodings(image)[0]
            except:
                messages.warning(request,"Please upload valid image  only support -> jpg, jpeg format !!")
                return redirect('/registeruser/')

            user = Indlist(username=username, orgname=orgname, imagee=imagee, encoded=json.dumps(encodeimage.tolist()))

            user.save()
            form.save()
            
            messages.success(request, f"registration of {username} is successfull!!")
            return redirect('/orgdashboard/')
        else:
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1!=password2:
                messages.warning(request, "password1 is not equal to password2 please ensure password is typed correctly!!")
            elif User.objects.filter(username=username).exists():
                messages.warning(request, "Username is already taken!!")
            else:
                messages.warning(request, "Password criteria is not meet, please use strong password!!")



    form = UserCreationForm()
    return render(request, 'registeruser.html', {"form": form})
    



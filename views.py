from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from django.db import connection
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from . import views
import random

def signup(request):
    if request.method == "POST":
        user_id = request.POST['name']

        name = request.POST['name']
        address = request.POST['address']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        lat=request.POST['lat']
        lon=request.POST['lon']
        status="pending"

        cursor = connection.cursor()
        cursor.execute("select * from turf where status !='pending' ")
        cdata = cursor.fetchall()
        cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
        rates=cursor.fetchall()
        cursor.execute("select user_id from user_register where user_id ='"+user_id+"' ")
        data = cursor.fetchone()
        if data==None:
            cursor.execute("select idturf from turf where idturf ='" + user_id + "' ")
            data = cursor.fetchone()
            if data==None:
                cursor.execute("select admin_id from login where admin_id ='" + user_id + "' ")
                data = cursor.fetchone()
                if data==None:
                    cursor.execute("insert into turf values('" + str(user_id) + "','" + str(name )+ "','" + str(address) + "','" + str(phone) + "','" + str(email) + "','" +str(password) + "','" +str(lat) + "','" +str(lon) + "','" +str(status) + "')")
                    return redirect("login")
                else:
                    return render(request, "login.html",{'data':cdata,'rates':rates})
            else:
                return render(request, "login.html",{'data':cdata,'rates':rates})
        else:
            return render(request, "login.html",{'data':cdata,'rates':rates})
    return render(request, "login.html",{'data':cdata,'rates':rates})

def login(request):
    if request.method == "POST":
        userid = request.POST['userid']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute("select * from login where admin_id= '" + userid + "' AND password = '" + password + "'")
        admin = cursor.fetchone()
        if admin == None:
            cursor.execute("select * from turf where idturf = '" + userid + "' AND password = '" + password + "' AND status ='approved' ")
            turf = cursor.fetchone()
            if turf == None:
                cursor.execute("select * from user_register where user_id ='"+userid+"' and password = '" + password + "' ")
                user=cursor.fetchone()
                if user == None:
                    return render(request, "invalidlogin.html")
                else:
                    request.session["uid"] = userid
                    return redirect("user_home")
            else:
                request.session["tid"] = userid
                return redirect("turf_home")
        else:
            return redirect("admin_home")
    cursor = connection.cursor()
    cursor.execute("select * from turf where status !='pending' and status !='rejected'")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "login.html",{'data':cdata,'rates':rates})

def admin_home(request):
    cursor = connection.cursor()
    cursor.execute("select * from turf where status ='approved' ")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()

    return render(request, "admin_home.html",{'data':cdata,'rates':rates})

def view_approved_turf(request):
    cursor= connection.cursor()
    cursor.execute("select * from turf where status ='approved'")
    cdata=cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "admin_approved_turf.html", {'data':cdata,'rates':rates})

def view_pending_turf(request):
    cursor = connection.cursor()
    cursor.execute("select * from turf where status ='pending'")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "admin_pending_turf.html", {'data': cdata,'rates':rates})

def edit_pending_turf_status(request):
    if request.method == "POST":
        id = request.POST['id']
    cursor = connection.cursor()
    cursor.execute("update turf set status ='approved' where  idturf ='" + str(id) + "' ")
    return redirect("admin_home")

def reject_pending_turf_status(request):
    if request.method == "POST":
        id = request.POST['id']
    cursor = connection.cursor()
    cursor.execute("update turf set status ='rejected' where  idturf ='" + str(id) + "' ")
    return redirect("admin_home")
def view_feedback(request):
    cursor=connection.cursor()
    cursor.execute("select * from feedback ")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "adminfeedbacks.html", {'data': cdata,'rates':rates})




def turf_home(request):
    cursor = connection.cursor()
    cursor.execute("select * from turf where status='approved'")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_home.html", {'data': cdata,'rates':rates})

def register_comp(request):
    tid = request.session["tid"]  #turf id
    cursor = connection.cursor()
    cursor.execute("select * from team where idturf = '"+str(tid)+"' ")
    cdata = cursor.fetchall()
    print(cdata)
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_register_comp.html", {'data': cdata,'rates':rates})

def add_comp(request):
    tid = request.session["tid"]  #turf id
    if request.method == "POST":
        cn=request.POST['cn']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        teamcount = request.POST['teamcount']
        cursor = connection.cursor()
        cursor.execute("insert into competition values(null,'" + str(cn) + "','" + str(sdate) + "','" + str(edate) + "', '" + str(tid) + "', '" + str(teamcount) + "') ")
        return redirect('view_comp')

def view_comp(request):
    tid = request.session["tid"]
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM competition  where idturf ='"+str(tid)+"' ")
    comp = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_view_comp.html", {'comp': comp,'rates':rates})

def edit_comp(request, id):
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("select * from competition  where idcompetition ='"+str(id)+"' and idturf ='"+str(tid)+"'")
    cdata = cursor.fetchone()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_edit_comp.html", {'row': cdata,'rates':rates})

def update_comp(request, id):
    tid = request.session["tid"]
    if request.method == "POST":
        cn = request.POST['cn']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        teamcount = request.POST['teamcount']
        count = request.POST['teamcountprevious']
        cursor=connection.cursor()
        if (teamcount != count):
            cursor.execute("delete from pool where competition_id ='"+str(id)+"' ")
        cursor.execute("update competition set name='"+str(cn)+"' where idcompetition ='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update competition set start_date='"+str(sdate)+"' where idcompetition ='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update competition set end_date='"+str(edate)+"'where idcompetition ='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update competition set total_team='"+str(teamcount)+"' where idcompetition ='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        return redirect('view_comp')

def delete_comp(request,id):
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("delete from competition where idcompetition='" + str(id) + "'  and idturf ='"+str(tid)+"'")
    cursor.execute("delete from pool where competition_id ='"+str(id)+"' ")
    cursor.execute("delete from team where idcompetition ='"+str(id)+"' ")
    return redirect('view_comp')

def register_team(request, id):
    cursor= connection.cursor()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_register_team.html",{'id':id,'rates':rates})

def add_team(request):
    if request.method == "POST":
        cid=request.POST['compid']
        id=request.session["tid"]
        name=request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']
        email = request.POST['email']
        trophy = request.POST['trophy']
        year = request.POST['year']
        location = request.POST['location']
        cursor = connection.cursor()

        cursor.execute("select * from team where name ='"+str(name)+"' and idturf = '" + str(id) + "' and idcompetition= '"+str(cid)+"' ")
        data=cursor.fetchone()
        if data ==None:
            cursor.execute("select idteam from team where idturf = '" + str(id) + "' and idcompetition= '" + str(cid) + "' ")
            teams=cursor.fetchall()
            teams=list(teams)
            length=len(teams)
            cursor.execute("select total_team from competition where idcompetition= '" + str(cid) + "' ")
            team_no= cursor.fetchone()
            team_no=list(team_no)
            team_no=int(team_no[0])
            if team_no>length:
                cursor.execute("insert into team values(null,'" + str(name) + "','" + str(address) + "','" + str(phone) + "','" + str(email) + "', '" + str(trophy) + "','" + str(year) + "', '" + str(location) + "','" + str(id) + "','" + str(cid) + "') ")
                messages.success(request, 'Team Registered Scccessfully')
                return redirect('register_team', id=cid)
            elif team_no == length:

                messages.error(request, 'Already Added Specified Number Of Teams..')
                return redirect('view_team', id=cid)
        else:
            messages.error(request, 'Team Name Already Exist')
            return redirect('register_team',id=cid)

def view_team(request,id):
    tid = request.session["tid"]
    request.session["compid"]=id
    cursor=connection.cursor()
    cursor.execute("select * from team where idturf ='"+tid+"' and idcompetition='"+str(id)+"' ")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render (request, "turf_view_team.html", {'data': cdata,'rates':rates})

def edit_team(request, id):
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("select * from team  where idteam ='"+str(id)+"' and idturf ='"+str(tid)+"' ")
    cdata = cursor.fetchone()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_edit_team.html", {'data': cdata,'rates':rates})

def update_team(request,id):
    compid=request.session["compid"]
    tid=request.session["tid"]
    if request.method == "POST" :
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']
        email = request.POST['email']
        trophy = request.POST['trophy']
        year = request.POST['year']
        location = request.POST['location']
        cursor = connection.cursor()
        cursor.execute("update team set name ='"+str(name)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update team set address ='"+str(address)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update team set phone ='"+str(phone)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update team set email ='"+str(email)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update team set number_of_trophy ='"+str(trophy)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update team set founded ='"+str(year)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update team set location ='"+str(location)+"' where idteam='"+str(id)+"' and idturf ='"+str(tid)+"'  ")
        return redirect('view_team',id=compid)

def delete_team(request,id):
    compid=request.session["compid"]
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("delete from team where idteam='" + str(id) + "' and idturf ='"+str(tid)+"'")
    return redirect('view_team',id=compid)

def upload_adv(request, id):
    tid = request.session["tid"]
    request.session["uadv"]= id
    cursor = connection.cursor()
    cursor.execute("select * from team where idturf = '" + str(tid) + "' ")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_upload_adv.html", {'row': cdata,'rates':rates})

def add_adv(request):
    if request.method == "POST" and request.FILES['upload']:
        id = request.session["uadv"]
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save( upload.name, upload)
        file_url = fss.url(file)
        description = request.POST['desc']
        cursor = connection.cursor()
        cursor.execute("insert into competition_advertisement values(null,'" + str(id) + "','" + str(description) + "','"+str(upload)+"') ")
        return redirect('view_adv',id=id)

def view_adv(request,id):
    request.session["cadv"]=id
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM competition_advertisement where idcompetition ='" + str(id) + "' ")
    adv = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_view_adv.html", {'adv': adv,'rates':rates})

def edit_adv(request,id):
    cursor=connection.cursor()
    cursor.execute("select * from competition_advertisement where idcompetition_advertisement ='"+str(id)+"'")
    adv = cursor.fetchone()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_edit_adv.html",{'adv':adv,'rates':rates})

def delete_adv(request, id):
    cadv=request.session["cadv"]
    cursor=connection.cursor()
    cursor.execute("delete from competition_advertisement where idcompetition_advertisement ='" + str(id) + "' ")
    return redirect('view_adv', id=cadv)


def make_pool(request, id):
    cursor = connection.cursor()
    cursor.execute("select * from pool where competition_id ='"+str(id)+"'")
    data=cursor.fetchone()
    if data==None:
        cursor.execute("select idteam from team where idcompetition= '" + str(id) + "' ")
        teams = cursor.fetchall()
        teams = list(teams)
        length = len(teams)
        cursor.execute("select total_team from competition where idcompetition= '" + str(id) + "' ")
        team_no = cursor.fetchone()
        team_no = list(team_no)
        team_no = int(team_no[0])
        if length<team_no:
            messages.error(request, 'Add "'+str(team_no)+'" teams to see pool')
            return redirect('view_comp')
        elif(length==team_no):
            cursor.execute("select idteam from team where  idcompetition='"+str(id)+"'")
            team = cursor.fetchall()
            team = list(team)
            l=[]
            for i in team:
                m = list(i)
                l.append(m[0])
            random.shuffle(l)
            if length ==32:
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[0]) + "','" + str(l[1]) + "','" + str(l[2]) + "', '" + str(l[3]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[4]) + "','" + str(l[5]) + "','" + str(l[6]) + "', '" + str(l[7]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[8]) + "','" + str(l[9]) + "','" + str(l[10]) + "', '" + str(l[11]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[12]) + "','" + str(l[13]) + "','" + str(l[14]) + "', '" + str(l[15]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[16]) + "','" + str(l[17]) + "','" + str(l[18]) + "', '" + str(l[19]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[20]) + "','" + str(l[21]) + "','" + str(l[22]) + "', '" + str(l[23]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[24]) + "','" + str(l[25]) + "','" + str(l[26]) + "', '" + str(l[27]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[28]) + "','" + str(l[29]) + "','" + str(l[30]) + "', '" + str(l[31]) + "') ")
                return redirect('view_pool', id=id)
            elif length ==16:
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[0]) + "','" + str(l[1]) + "','" + str(l[2]) + "', '" + str(l[3]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[4]) + "','" + str(l[5]) + "','" + str(l[6]) + "', '" + str(l[7]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[8]) + "','" + str(l[9]) + "','" + str(l[10]) + "', '" + str(l[11]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[12]) + "','" + str(l[13]) + "','" + str(l[14]) + "', '" + str(l[15]) + "') ")
                return redirect('view_pool',id=id)
            elif length == 8:
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[0]) + "','" + str(l[1]) + "','" + str(l[2]) + "', '" + str(l[3]) + "') ")
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[4]) + "','" + str(l[5]) + "','" + str(l[6]) + "', '" + str(l[7]) + "') ")
                return redirect('view_pool', id=id)
            elif length == 4:
                cursor.execute("insert into pool values (null,'" + str(id) + "','" + str(l[0]) + "','" + str(l[1]) + "','" + str(l[2]) + "', '" + str(l[3]) + "') ")
                return redirect('view_pool', id=id)
            else:
                messages.error(request, 'something is wrong!! cant access pools')
                return redirect('view_comp')
        else:
            messages.error(request, 'something is wrong!! cant access pools')
            return redirect('view_comp')
    else:
        return redirect('view_pool',id=id)

def view_pool(request,id):
    cursor=connection.cursor()
    cursor.execute("select * from pool where competition_id = '"+str(id)+"' ")

    data= cursor.fetchall()
    count = len(data)


    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_a=team.idteam  where team.idcompetition ='"+str(id)+"' ")
    teama=cursor.fetchall()

    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_b=team.idteam  where team.idcompetition ='" + str(id) + "' ")
    teamb = cursor.fetchall()
    teamb= list(teamb)
    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_c=team.idteam  where team.idcompetition ='" + str(id) + "' ")
    teamc = cursor.fetchall()
    teamc=list(teamc)
    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_d=team.idteam  where team.idcompetition ='" + str(id) + "' ")
    teamd = cursor.fetchall()
    teamd = list(teamd)

    teams=[]
    for i in range(count):
        teama = list(teama)
        teamname = teama[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)
        teamb = list(teamb)
        teamname = teamb[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)
        teamc = list(teamc)
        teamname = teamc[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)
        teamd = list(teamd)
        teamname = teamd[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)

    data = list(data)
    for i in data:
        teams.append(i[0])
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()

    if count == 1:
        return render(request, 'turf_view_pool1.html', {'data': data, 'team':teams,'rates':rates})
    if count == 2:
        return render(request, 'turf_view_pool2.html', {'data': data, 'team': teams,'rates':rates})
    if count == 4:
        return render(request, 'turf_view_pool4.html', {'data': data, 'team': teams,'rates':rates})
    if count == 8:
        return render(request, 'turf_view_pool8.html', {'data': data, 'team': teams,'rates':rates})




def register_match(request):
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("select * from team where idturf = '"+str(tid)+"' ")
    cdata = cursor.fetchall()
    print(cdata)
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "register_match.html", {'data': cdata,'rates':rates})

def add_match(request):
    tid = request.session["tid"]
    if request.method == "POST":
        teamid=request.POST['teamid']
        oteamid = request.POST['oteamid']
        date = request.POST['date']
        result = request.POST['result']
        mn=request.POST['mn']
        cursor = connection.cursor()
        cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
        rates=cursor.fetchall()
        if teamid == oteamid:
            cursor = connection.cursor()
            cursor.execute("select * from teams ")
            cdata = cursor.fetchall()
            print(cdata)
            return render(request,"errorregister_match.html", {'data': cdata,'rates':rates})
        else:
            cursor.execute("insert into matches values(null,'" + str(tid) + "','" + str(teamid) + "','" + str(oteamid) + "', '" + str(date) + "', '" + str(result) + "', '"+str(mn)+ "') ")
            return redirect('view_match')

def edit_match(request, id):
    cursor = connection.cursor()
    cursor.execute("SELECT m.idmatches, m.idteam ,m.match_date,m.result, m.match_name, p1.name ,p2.name as opponent,m.idmatches,m.poolid, m.score FROM matches m JOIN team p1 ON m.idteam = p1.idteam JOIN team p2 ON m.opponent = p2.idteam where m.idmatches ='"+str(id)+"' ")
    cdata = cursor.fetchone()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_edit_match.html", {'row': cdata,'rates':rates})

def update_match(request, id):
    tid = request.session["tid"]
    if request.method == "POST":
        date = request.POST['date']
        result = request.POST['result']
        mn = request.POST['mn']
        score =request.POST['score']
        poolid = request.POST['pid']
        cursor=connection.cursor()

        cursor.execute("update matches set match_name='"+str(mn)+"' where idmatches='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update matches set match_date='"+str(date)+"' where idmatches='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update matches set result='"+str(result)+"' where idmatches='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        cursor.execute("update matches set score='"+str(score)+"' where idmatches='"+str(id)+"' and idturf ='"+str(tid)+"' ")
        return redirect('view_match_of_pool',id=int(poolid))

def delete_match(request,id):
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("delete from matches where idmatches='" + str(id) + "'  and idturf ='"+str(tid)+"'")
    return redirect('view_match')

def view_match(request):
    tid = request.session["tid"]
    cursor=connection.cursor()
    cursor.execute("SELECT m.idmatches, m.idteam ,m.match_date,m.result, m.match_name, p1.name ,p2.name as opponent,m.idmatches, m.score FROM matches m JOIN team p1 ON m.idteam = p1.idteam JOIN team p2 ON m.opponent = p2.idteam where m.idturf ='"+str(tid)+"' ")
    matches = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_view_matches.html", {'matches': matches,'rates':rates})

def edit_profile(request):
    tid = request.session["tid"]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM turf  where idturf ='"+str(tid)+"' ")
    turf = cursor.fetchone()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_profile.html", {'data': turf,'rates':rates})

def update_profile(request):
    cursor=connection.cursor()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    tid = request.session["tid"]
    if request.method == "POST":
        name = request.POST['name']
        address = request.POST['address']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        lat = request.POST['lat']
        lon = request.POST['lon']
        cursor = connection.cursor()
        cursor.execute("select user_id from user_register where user_id ='" + str(name) + "' ")
        data = cursor.fetchone()
        if data == None:
            cursor.execute("select idturf from turf where idturf ='" + str(name) + "' ")
            data = cursor.fetchone()
            if data == None:
                cursor.execute("select admin_id from login where admin_id ='" + str(name) + "' ")
                data = cursor.fetchone()
                if data == None:
                    cursor= connection.cursor()
                    cursor.execute("select idcompetition from competition where idturf ='"+ str(tid)+ "'")
                    comp=cursor.fetchall()
                    comp=list(comp)
                    for i in comp:
                        cursor.execute("update competition set idturf ='"+ str(name)+"' where idcompetition='"+str(i[0])+"' ")
                    cursor.execute("select idteam from team where idturf = '" + str(tid) +"'")
                    teams= cursor.fetchall()
                    teams = list(teams)
                    for i in teams:
                        cursor.execute("update team set idturf ='" + str(name) + "' where idteam='" + str(i[0]) + "' ")
                    cursor.execute("select idmatches from matches where idturf = '"+str(tid)+"' ")
                    turfs=cursor.fetchall()
                    turfs= list(turfs)
                    for i in turfs:
                        cursor.execute("update matches set idturf ='"+str(name)+"' where idmatches = '"+str(i[0])+"' ")
                    cursor.execute("select idfeedback from feedback where user_id ='"+str(tid)+"'")
                    feeds=cursor.fetchall()
                    feeds=list(feeds)
                    for i in feeds:
                        cursor.execute("update feedbacks set idfeedback ='"+str(i[0])+"' ")
                    cursor.execute("delete from turf where idturf ='" + str(tid) + "' ")
                    cursor.execute("insert into turf values('" + str(name) + "','" + str(name) + "','" + str(address) + "','" + str(phone) + "','" + str(email) + "','" + str(password) + "','" + str(lat) + "','" + str(lon) + "','approved')")
                    return redirect("login")
                else:
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM turf  where idturf ='" + str(tid) + "' ")
                    turf = cursor.fetchone()
                    return render(request,'error_editprofile.html', {'data':turf,'rates':rates})
            else:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM turf  where idturf ='" + str(tid) + "' ")
                turf = cursor.fetchone()
                return render(request, 'error_editprofile.html', {'data': turf,'rates':rates})
        else:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM turf  where idturf ='" + str(tid) + "' ")
            turf = cursor.fetchone()
            return render(request, 'error_editprofile.html', {'data': turf,'rates':rates})

def feedback(request):
    cursor=connection.cursor()
    tid = request.session["tid"]
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_feedback.html", {"user": tid,'rates':rates})

def sendfb(request):
    cursor = connection.cursor()
    if request.method == "POST":
        fbdetails = request.POST['fbdetails']
        tid = request.session["tid"]
        cursor.execute("insert into feedback values( null,'" + str(tid) + "', '" + str(fbdetails) + "',curdate() )")
        messages.info(request, "done")
        return redirect("view_fb")

def view_fb(request):
    tid = request.session["tid"]
    cursor=connection.cursor()
    cursor.execute("select * from feedback where user_id='"+tid+"' ")
    table=cursor.fetchall()
    print(table)
    table0 = list(table)
    length = len(table0)
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    if length == 0:
        value="feedback"
        return render(request,"no_carts.html",{"val":value,'rates':rates})
    else:
        return render(request,"turf_view_fb.html",{"table":table,'rates':rates})

def user_view_turfs(request):
    cursor = connection.cursor()
    cursor.execute("select * from turf where status ='approved' ")
    turf = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request,'user_view_turf.html',{'turf':turf,'rates':rates})

def user_view_competition(request,id):
    cursor= connection.cursor()
    cursor.execute("select * from competition where idturf = '"+str(id)+"'")
    data = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, 'user_view_competition.html',{'comp':data,'rates':rates})

def user_view_team(request,id):
    cursor=connection.cursor()
    cursor.execute("select * from team where idcompetition='"+str(id)+"' ")
    cdata = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render (request, "user_view_team.html", {'data': cdata,'rates':rates})

def user_view_adv(request,id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM competition_advertisement where idcompetition ='" + str(id) + "' ")
    adv = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "user_view_adv.html", {'adv': adv,'rates':rates})

def user_view_pool(request,id):
    cursor=connection.cursor()
    cursor.execute("select * from pool where competition_id = '" + str(id) + "' ")
    sanda = cursor.fetchone()
    if sanda == None:
        return HttpResponse("<script> alert('No Pools Added Yet!!');window.location='../user_view_turfs';</script>")
    cursor.execute("select * from pool where competition_id = '"+str(id)+"' ")
    data= cursor.fetchall()
    count = len(data)
    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_a=team.idteam  where team.idcompetition ='"+str(id)+"' ")
    teama=cursor.fetchall()

    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_b=team.idteam  where team.idcompetition ='" + str(id) + "' ")
    teamb = cursor.fetchall()
    teamb= list(teamb)
    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_c=team.idteam  where team.idcompetition ='" + str(id) + "' ")
    teamc = cursor.fetchall()
    teamc=list(teamc)
    cursor.execute("SELECT team.name,team.idteam FROM  pool join team on pool.team_d=team.idteam  where team.idcompetition ='" + str(id) + "' ")
    teamd = cursor.fetchall()
    teamd = list(teamd)

    teams=[]
    for i in range(count):
        teama = list(teama)
        teamname = teama[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)
        teamb = list(teamb)
        teamname = teamb[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)
        teamc = list(teamc)
        teamname = teamc[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)
        teamd = list(teamd)
        teamname = teamd[i]
        teamnam = list(teamname)
        teamname = teamnam[0]
        teamid = teamnam[1]
        print(teamname)
        print(teamid)
        teams.append(teamname)
        teams.append(teamid)

    data = list(data)
    for i in data:
        teams.append(i[0])
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    if count == 1:
        return render(request, 'user_view_pool1.html', {'data': data, 'team':teams,'rates':rates})
    if count == 2:
        return render(request, 'user_view_pool2.html', {'data': data, 'team': teams,'rates':rates})
    if count == 4:
        return render(request, 'user_view_pool4.html', {'data': data, 'team': teams,'rates':rates})
    if count == 8:
        return render(request, 'user_view_pool8.html', {'data': data, 'team': teams,'rates':rates})

def user_view_match_of_pool(request,id):
    cursor = connection.cursor()
    cursor.execute("SELECT m.idmatches, m.idteam ,m.match_date,m.result, m.match_name, p1.name ,p2.name as opponent,m.idmatches, m.score FROM matches m JOIN team p1 ON m.idteam = p1.idteam JOIN team p2 ON m.opponent = p2.idteam where m.poolid ='"+str(id)+"' ")
    data = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request,'user_view_match_of_pool.html',{'data':data,'rates':rates})

def user_home(request):
    cursor = connection.cursor()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "user_home.html",{'rates':rates})

def feedback_user(request):
    cursor = connection.cursor()
    cursor.execute("select * from turf where status='approved'")
    cdata = cursor.fetchall()
    tid = request.session["uid"]
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "user_feedback_user.html", {"user": tid, "data":cdata,'rates':rates})

def sendfb_user(request):
    cursor = connection.cursor()
    if request.method == "POST":
        fbdetails = request.POST['fbdetails']
        tid = request.session["uid"]
        cursor.execute("insert into feedback values( null,'" + str(tid) + "', '" + str(fbdetails) + "',curdate() )")
        return redirect("view_fb_user")

def view_fb_user(request):
    tid = request.session["uid"]
    cursor=connection.cursor()
    cursor.execute("select * from feedback where user_id='"+tid+"' ")
    table=cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    print(table)
    table0 = list(table)
    length = len(table0)
    if length == 0:
        value="feedback"
        return render(request,"no_carts_user.html",{"val":value,'rates':rates})
    else:
        return render(request,"user_view_fb_user.html",{"table":table,'rates':rates})


def make_match_of_pool(request,id):
    cursor = connection.cursor()
    tid = request.session["tid"]
    cursor.execute("select * from matches where poolid ='"+str(id)+"' ")
    data = cursor.fetchone()
    if data == None:
        cursor.execute("select * from pool where pool_id ='"+str(id)+"' ")
        pool=cursor.fetchone()
        pool= list(pool)
        compid =pool[1]
        team_a =pool[2]
        team_b =pool[3]
        team_c =pool[4]
        team_d =pool[5]
        cursor.execute("insert into matches values(null,'"+str(tid)+"','"+str(team_a)+"','"+str(team_b)+"','not published', 'not published', 'pending', '"+str(id)+"', '"+str(compid)+"','pending')")
        cursor.execute("insert into matches values(null,'"+str(tid)+"','"+str(team_c)+"','"+str(team_d)+"','not published', 'not published', 'pending', '"+str(id)+"', '"+str(compid)+"','pending')")
        cursor.execute("insert into matches values(null,'"+str(tid)+"','"+str(team_a)+"','"+str(team_c)+"','not published', 'not published', 'pending', '"+str(id)+"', '"+str(compid)+"','pending')")
        cursor.execute("insert into matches values(null,'"+str(tid)+"','"+str(team_b)+"','"+str(team_d)+"','not published', 'not published', 'pending', '"+str(id)+"', '"+str(compid)+"','pending')")
        cursor.execute("insert into matches values(null,'"+str(tid)+"','"+str(team_a)+"','"+str(team_d)+"','not published', 'not published', 'pending', '"+str(id)+"', '"+str(compid)+"','pending')")
        cursor.execute("insert into matches values(null,'"+str(tid)+"','"+str(team_c)+"','"+str(team_b)+"','not published', 'not published', 'pending', '"+str(id)+"', '"+str(compid)+"','pending')")
        messages.info(request, "matches added for this pool")
        return redirect('view_match_of_pool',id=id)

    else:
        messages.info(request, "matches already exist in this pool")
        return redirect('view_match_of_pool', id=id)

def view_match_of_pool(request,id):
    cursor = connection.cursor()
    cursor.execute("SELECT m.idmatches, m.idteam ,m.match_date,m.result, m.match_name, p1.name ,p2.name as opponent,m.idmatches, m.score FROM matches m JOIN team p1 ON m.idteam = p1.idteam JOIN team p2 ON m.opponent = p2.idteam where m.poolid ='"+str(id)+"' ")
    data = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request,'turf_view_match_of_pool.html',{'data':data,'rates':rates})


def add_members(request,id):
    cursor = connection.cursor()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request, "turf_add_members.html",{'id':id,'rates':rates})

def members_add(request):
    if request.method == "POST" and request.FILES['upload']:
        teamid = request.POST['teamid']
        name = request.POST['name']
        yellow = request.POST['yellow']
        red = request.POST['red']
        icon = request.FILES['upload']
        upload = request.FILES['upload']
        position = request.POST['position']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
        cursor = connection.cursor()
        cursor.execute("insert into team_members values(null,'"+str(teamid)+"','" + str(name) + "','" + str(yellow) + "', '" + str(red) + "','" + str(icon) + "', '" + str(position) + "') ")
        return redirect('view_comp')


def view_members(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from team_members where idteam = '"+str(id)+"' ")
    data = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved' ")
    rates=cursor.fetchall()
    return render(request,'turf_view_members.html',{'data':data,'rates':rates})

def delete_member(request, id):
    cursor = connection.cursor()
    cursor.execute("select idteam from team_members where idteam_members = '"+str(id)+"' ")
    teamid = cursor.fetchone()
    teamid= list(teamid)
    teamid=teamid[0]
    cursor.execute("delete from team_members where idteam_members ='"+str(id)+"' ")
    return redirect('view_team', id=int(teamid))


def user_rate_turf(request,id):
    cursor =connection.cursor()
    cursor.execute("select * from turf  where idturf='"+str(id)+"'")
    ddata = cursor.fetchone()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    cursor.execute("select * from competition where idturf ='"+str(id)+"' ")
    comps=cursor.fetchall()
    return render(request,'user_rate_turf.html',{'ddata':ddata,'rates':rates,'comps':comps})

def rate(request,id):
    if request.method == "POST":
        cursor = connection.cursor()
        user = request.session["uid"]
        rate = request.POST['rate']
        cursor.execute("select * from rating where user_id= '" + str(user) + "' AND idturf = '" + str(id) + "'")
        exist = cursor.fetchone()
        if exist == None:
            cursor.execute(" insert into rating values( null,'" + str(user) + "','" + str(id) + "','" + str(rate) + "',curdate() ) ")
            cursor = connection.cursor()
            cursor.execute("select * from user_register")
            us = cursor.fetchall()
            n = 0
            for i in us:
                n = n + 1
            max_pers_user = 100 / n
            cursor.execute("select idturf from turf ")
            teams = cursor.fetchall()
            for i in teams:
                l = list(i)
                cursor = connection.cursor()
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='5' ")
                n5 = cursor.fetchall()
                r5 = 0
                for i in n5:
                    r5 = r5 + 1
                v5 = r5 * max_pers_user

                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='4' ")
                n4 = cursor.fetchall()
                r4 = 0
                for i in n4:
                    r4 = r4 + 1
                v4 = (r4 * max_pers_user * 4) / 5
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='3' ")
                n3 = cursor.fetchall()
                r3 = 0
                for i in n3:
                    r3 = r3 + 1
                v3 = (r3 * max_pers_user * 3) / 5
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='2' ")
                n2 = cursor.fetchall()
                r2 = 0
                for i in n2:
                    r2 = r2 + 1
                v2 = (r2 * max_pers_user * 2) / 5
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='1' ")
                n1 = cursor.fetchall()
                r1 = 0
                for i in n1:
                    r1 = r1 + 1
                v1 = (r1 * max_pers_user * 1) / 5
                val = v1 + v2 + v3 + v4 + v5
                cursor.execute("select * from turf_rate where idturf ='" + str(l[0]) + "'")
                yes = cursor.fetchone()
                if yes == None:
                    cursor.execute("insert into turf_rate values(null,'" + str(l[0]) + "','" + str(val) + "') ")
                else:
                    cursor.execute("update turf_rate set rate ='" + str(val) + "' where idturf ='" + str(l[0]) + "'")
            return redirect('user_home')
        else:
            cursor.execute("update rating set user_rating ='" + str(rate) + "' where idturf='" + str(id) + "' and user_id = '"+str(user)+"' ")
            cursor = connection.cursor()
            cursor.execute("select * from user_register")
            us = cursor.fetchall()
            n = 0
            for i in us:
                n = n + 1
            max_pers_user = 100 / n
            cursor.execute("select idturf from turf ")
            teams = cursor.fetchall()
            for i in teams:
                l = list(i)
                cursor = connection.cursor()
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='5' ")
                n5 = cursor.fetchall()
                r5 = 0
                for i in n5:
                    r5 = r5 + 1
                v5 = r5 * max_pers_user

                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='4' ")
                n4 = cursor.fetchall()
                r4 = 0
                for i in n4:
                    r4 = r4 + 1
                v4 = (r4 * max_pers_user * 4) / 5
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='3' ")
                n3 = cursor.fetchall()
                r3 = 0
                for i in n3:
                    r3 = r3 + 1
                v3 = (r3 * max_pers_user * 3) / 5
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='2' ")
                n2 = cursor.fetchall()
                r2 = 0
                for i in n2:
                    r2 = r2 + 1
                v2 = (r2 * max_pers_user * 2) / 5
                cursor.execute("select * from rating where idturf ='" + str(l[0]) + "' and user_rating ='1' ")
                n1 = cursor.fetchall()
                r1 = 0
                for i in n1:
                    r1 = r1 + 1
                v1 = (r1 * max_pers_user * 1) / 5
                val = v1 + v2 + v3 + v4 + v5
                cursor.execute("select * from turf_rate where idturf='" + str(l[0]) + "'")
                yes = cursor.fetchone()
                if yes == None:
                    cursor.execute("insert into turf_rate values(null,'" + str(l[0]) + "','" + str(val) + "') ")
                else:
                    cursor.execute("update turf_rate set rate ='" + str(val) + "' where idturf ='" + str(l[0]) + "'")
            return redirect('user_home')

def user_view_competitions(request,id):
    cursor = connection.cursor()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    cursor.execute("select competition_advertisement.*,competition.* from competition_advertisement join competition where competition.idcompetition = competition_advertisement.idcompetition and competition.idcompetition = '"+str(id)+"' ")
    compdetail=cursor.fetchall()
    print(compdetail)
    count=0
    for i in compdetail:
        count=count+1
    cursor.execute("select * from competition where idcompetition ='"+str(id)+"' ")
    comp=cursor.fetchone()
    return render(request,'user_view_competitions.html',{'rates':rates,'compdetails':compdetail,'count':count,'comp':comp})

def user_view_members(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from team_members where idteam_members = '"+str(id)+"' ")
    data = cursor.fetchall()
    cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
    rates=cursor.fetchall()
    return render(request,'user_view_members.html',{'data':data,'rates':rates})

def location(request,id,jd):
    return render(request,"Location.html",{'lat':id,'lon':jd})

def signupu(request):
    if request.method == "POST":
        user_id = request.POST['name']
        name = request.POST['name']
        address = request.POST['address']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute("select * from turf where status !='pending' ")
        cdata = cursor.fetchall()
        cursor.execute("SELECT turf_rate.idturf,turf_rate.rate, turf.name FROM turf_rate join turf where turf_rate.idturf = turf.idturf and turf.status ='approved'")
        rates=cursor.fetchall()
        cursor.execute("select user_id from user_register where user_id ='"+user_id+"' ")
        data = cursor.fetchone()
        if data==None:
            cursor.execute("select idturf from turf where idturf ='" + user_id + "' ")
            data = cursor.fetchone()
            if data==None:
                cursor.execute("select admin_id from login where admin_id ='" + user_id + "' ")
                data = cursor.fetchone()
                if data == None:
                    cursor.execute("insert into user_register values('" + str(user_id) + "','" + str(name )+ "','" + str(address) + "','" + str(email) + "','" + str(phone) + "','" +str(password) + "') ")
                    return redirect("login")
                else:
                    return render(request, "login.html",{'data':cdata,'rates':rates})
            else:
                return render(request, "login.html",{'data':cdata,'rates':rates})
        else:
            return render(request, "login.html",{'data':cdata,'rates':rates})
    return render(request, "login.html",{'data':cdata,'rates':rates})
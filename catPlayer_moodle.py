# lucnh this script and as mouse first clean orphan games and then
# join the game
import os,django
os.environ['DJANGO_SETTINGS_MODULE'] =  'RatonGato.settings'
django.setup()
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from server.models import Game, Move, Counter
import time
import re, math
import random, json

#python ./manage.py test rango.tests.UserAuthenticationTests --keepdb
#class UserAuthenticationTests(TestCase):

usernameCat = 'gatoUser'
passwdCat = 'gatoPasswd'
usernameMouse = 'ratonUser'
passwdMouse = 'ratonPasswd'
DEBUG = False

class CatPlayer():
    def __init__(self):
        self.clientCat = Client()
        self.cats = [0, 2, 4, 6]
        self.game=None
        currenTime = time.time()
        RandomSeed = int(currenTime) + os.getpid()
        random.seed(RandomSeed)

    def creatUser(self, userName, userPassword):
        try:
            user = User.objects.get(username=userName)
        except User.DoesNotExist:
            user = User(username=userName, password=userPassword)
            user.set_password(user.password)
            user.save()
        return user.id

    def login(self, userName, userPassword, client):
        response = client.get(reverse('login_user'))
        loginDict={}
        loginDict["username"]=userName
        loginDict["password"]=userPassword
        loginDict["type_player"]="cat"
        response = client.post(reverse('login_user'), loginDict, follow=True)
        return response


    def deleteUser(self, userName):
        try:
            userKK = User.objects.get(username=userName)
            userKK.delete()
        except User.DoesNotExist:
            pass

    def logout(self, client):
        try:
            response = client.get(reverse('logout_user'), follow=True)
            return response
        except:
            pass

    def wait_loop(self, seconds):
        key = "Es tu turno" #adaptado a nuestro juego
        print ("wait loop begin")
        while True:
            response = self.clientCat.post('/server/status_board/', {'value': '1',}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            if response.content.find(key) != -1:
                break
            time.sleep(seconds)
            print ".",
        print ("wait loop end")
        return 0

    def parse_mouse(self):
        """http://pythex.org/"""
        response = self.clientCat.post('/server/status_board/', {'value': '1',}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        searchString='<td id=id_(\d+) onclick="getID\(this\);" >\s+<img class="token" src="/static/images/mouse.png" alt="mouse" style="opacity: 0.7"/>'
        finds = re.findall(searchString,response.content)
        print finds
        return finds[0]

    def validRandomMove(self,mousePosition):
        counter=0
        validMoves=[+7,+9]
        target = -1
        catIndex = -1
        origin = -1
        moveDict={}

        while True:
            counter += 1
            if counter > 1000:
                print "I cannot move. You won."
                exit(0)
            i = random.randrange(0,2)
            catIndex = random.randrange(0,4)

            origin = self.cats[catIndex]
            target = origin + validMoves[i]
            print("origin target cats", origin, target, self.cats)
            #cannot be a cat
            if mousePosition == target:
                 print("continue mouseposition", mousePosition,target )
                 continue
            #canot be a cat in target
            continueit=False
            for cat in self.cats:
                if cat == target:
                    print("continue cats")
                    continueit = True
            if continueit:
                continue
            #can not move two rows o no row
            if not ( 1 + (origin//8)) ==(target//8) :
                 print("continue no two rows")
                 continue
            # if target in the right range break
            if target < 0 or target > 63:
                print("continue target self.cats, target ",self.cats, target)
                continue

            moveDict['origin']=origin
            moveDict['target']=target
            response = self.clientCat.post(reverse('move'), moveDict)
            print response.content
            
            if response.content.find("Error!") == -1:
                break
            else:
                continue
        return origin,target
        #try to move
    def set_catPosition(self,origin, position):
        for cat in range(0,4):
            if self.cats[cat] == origin:
                self.cats[cat] = target
                break
        print("self.cats",self.cats)

CatPlayer = CatPlayer()
#make sure mouse user exists
userMouseID = CatPlayer.creatUser(usernameCat, passwdCat)
#login
response = CatPlayer.login(usernameCat, passwdCat, CatPlayer.clientCat) #cuando logeas como gato se crea el juego
#create game
#response = CatPlayer.clientCat.get(reverse('create_game'))
#get last game id
game = Game.objects.latest("id")

#check if mouse has joined
print("waiting untill mouse joins")
while True:
     time.sleep(1)
     gameOK = Game.objects.filter(mouseUser__isnull=True).order_by("-id")
     if gameOK.exists():
         game2 = gameOK[0]
         if game.id == game2.id:
             print ".",
             continue
     else:
         break

#comienza el juego
print("game id=%d"%game.id)
moveDict={}
while True:
     # loop waiting for myTurn=True
     CatPlayer.wait_loop(2)# time in second between retrial

     #moveDict['origin']=0
     #moveDict['target']=9
     #response = CatPlayer.clientCat.post(reverse('move'), moveDict)

     # parse mouse position
     mousePosition = CatPlayer.parse_mouse()
     print('mousePosition', mousePosition)
     #create random cat move
     origin, target = CatPlayer.validRandomMove(mousePosition)
     #move
     CatPlayer.set_catPosition(origin, target)


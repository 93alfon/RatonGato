import os,django
os.environ["DJANGO_SETTINGS_MODULE"] = "RatonGato.settings"
django.setup()
from server.models import User, Game, Move

#busca usuario id10 y si no existe lo crea
u = User.objects.filter(id=10)
if u.exists():
	u10 = u[0]
	print "El usuario con id=10 ya existe, obtenida su instancia"
else :
	u10 = User ( id=10 , username = 'u10', password= 'p10')
	u10.save()
	print "Creado usuario con id=10"

#busca usuario id11 y si no existe lo crea
u2 = User.objects.filter(id=11)
if u2.exists():
	u11 = u2[0]
	print "El usuario con id=11 ya existe, obtenida su instancia"
else :
	u11 = User ( id=11 , username = 'u11', password= 'p11')
	u11.save()
	print "Creado usuario con id=11"

#Busca si hay algun juego con car id 10 y sin mouse, y sino lo crea
print "Buscamos juegos con el usuario10 como gato y sin raton"
g = Game.objects.filter(catUser=u10)
if g.exists():
	game = g[0]
	print "Obtenido la instancia del juego gato=usuario10 y sin raton"
else :
	game = Game (catUser=u10)
	game.save()
	print "El usuario 10 no tiene ningun juego com gato y sin raton. Lo hemos creado"

#Busca un juego sin mouse, y si hay pone como mouse id 10
print "Buscamos juegos sin raton"
g2 = Game.objects.filter(mouseUser__isnull=True)
if g2.exists():
	game = g2[0]
	game.mouseUser= u11
	game.save()
	print "Encontrado juego sin raton, unimos al usuario 11 como raton"

	#movimiento por user 10 de 2 a 11
	m1 = Move(origin=2, target=11, game=game)
	game.cat2 = 11;
	game.catTurn = False
	game.save()
	m1.save()
	print "Realizado movimineto de 2=>11 por el usuario10"

	#movimiento por user 11 de 59 a 52
	m2 = Move(origin=59, target=52, game=game)
	game.mouse = 52
	game.catTurn = True
	game.save()
	m2.save()
	print "Realizado movimineto de 59=>82 por el usuario11"
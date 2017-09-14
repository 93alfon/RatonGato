from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpResponseRedirect, HttpResponse
from server.models import User, Game, Move, Counter
from server.forms import UserForm, MoveForm

#Autor Alfonso Bonilla
def index(request):
	context_dict = {}

	if request.user.is_authenticated():

		username = request.user.username
		context_dict['username'] = username

		if 'gameID' in request.session:
			context_dict['OnGame'] = True

	context_dict['index'] = True

	return render(request, 'server/index.html', context_dict)

#Autor Alfonso Bonilla
def counterSession(request):

	#Intentamos acceder al contador
	try:
		counterG = Counter.objects.get()
		counter = counterG.counter
		counterG.counter += 1
		counterG.save()
	#Si hay una excepcion lo creamos
	except Counter.DoesNotExist:
		counterG = Counter(counter=2);
		counter = 1
		counterG.save()

	#Si existe el contador en sesison lo obtenemos
	if 'counterSes' in request.session:
		counterSes = request.session['counterSes']
	#Si no existe creamos una variable local a 0
	else:
		counterSes = 0

	#Sumamos uno al contador anterior obtenido
	counterSes = counterSes + 1

	#guardamos el valor actualizado en la variable de sesision
	request.session['counterSes'] = counterSes

	#Vamos a la pagina counter.html pasando las variables
	return render(request, 'server/counter.html', {'counterSes': counterSes, 'counterGlobal': counter})

#Autor Alfonso Bonilla
def register_user(request):
	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	if request.method == 'POST':
		#process input data
		user_form = UserForm(data=request.POST)
		# If the two forms are valid...
		if user_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Update our variable to tell the template registration was successful.
			registered = True
			return render(request, 'server/login.html', {'registered': registered, 'margin': 'margin-top:3em'})
		else:
			return render(request, 'server/register.html',{'user_form': user_form, 'registered': registered, 'error':"Nombre de Usuario en uso", 'margin': 'margin-top:3em'} )
	else:
		user_form = UserForm()
		# Render the template depending on the context.
		#return render(request,'server/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

		return render(request, 'server/register.html',{'user_form': user_form, 'registered': registered, 'margin': 'margin-top:3em'})

#Autor Alfonso Bonilla
def login_user(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		type_player = request.POST.get('type_player') # cat or mouse

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)

				#si el jugador eligio gato creamos un juego
				if type_player == 'cat':
					request.session["amIcat"] = True
					create_game(request)
					#join_game(request)
					return HttpResponseRedirect('/server/join_game')

				else:
					request.session["amIcat"] = False
					#join_game(request)
					return HttpResponseRedirect('/server/join_game')

			else:
				# An inactive account was used - no logging in!
				return render(request, 'server/login.html', {'error': 'Tu cuenta esta desactivada'})
		else:
			# Bad login details were provided. So we can't log the user in.
			return render(request, 'server/login.html', {'error': 'Datos de usuario incorrectos'})

		# The request is not a HTTP POST, so display the login form.
		# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'server/login.html', {'margin': 'margin-top:3em'})

#Autor Alfonso Bonilla
def logout_user(request):
	#Restringido el acceso a solo usuarios logeados
	if request.user.is_authenticated():
		# Since we know the user is logged in, we can now just log them out.
		username = request.user.username
		context_dict = {'username':username}

		#Eliminamos las variables de sesion antes de cerrar sesion
		if 'counterSes' in request.session:
			del request.session['counterSes']

		if 'amIcat' in request.session:
			del request.session['amIcat']

		if 'gameID' in request.session:
			del request.session['gameID']

		request.session.modified = True
		logout(request)
		return render(request, 'server/login.html', {'info': 'Hasta Pronto '+ username})
	else:
		#en caso de no estar logeado vaos a nologged.html
		return render(request, 'server/login.html', {'error': 'Tienes que logearte primero'})

#Autor Alfonso Bonilla
def create_game(request):
	game = Game (catUser=request.user)
	game.save()
	request.session["gameID"] = game.id


#Autor Alfonso Bonilla
def clean_orphan_games(request):
	#obtenemos una lista de juegos sin mouse
	games = Game.objects.filter(mouseUser__isnull=True)

	#numero de juegos obtenidos
	rows = len(games)

	#bucle para eliminarlos
	for g in games:
		g.delete()

	#render pasando el numero de juegos eliminados
	return render(request, 'server/clean.html', {'rows_count': rows})

#Autor Alfonso Bonilla
def join_game(request):
	#Restringido el acceso a solo usuarios logeados
	if request.user.is_authenticated():
		gato = request.session["amIcat"]
		username = request.user.username
		context_dict = {}
		context_dict['username'] = username
		if gato == True:
			if 'gameID' not in request.session:
				create_game(request)
			context_dict['mensaje'] = "Esperando a que se una un Raton"
		else:
			context_dict['mensaje'] = "Esperando a que un gato cree un juego"

		return render(request, 'server/join.html', context_dict)
	else:
		#en caso de no estar logeado vaos a login.html con mensaje de error
		return render(request, 'server/login.html', {'error': 'Tienes que logearte primero'})

def wait_player(request):
	bando = request.session["amIcat"]
	if bando == True:
		gameID = request.session['gameID']
		g = Game.objects.filter(id=gameID)
		game = g[0]
		if game.mouseUser == None:
			return HttpResponse("False")
		else:
			return HttpResponse("True")
	else:
		games = Game.objects.filter(mouseUser__isnull=True)
		if games.exists():
			g = games[len(games)-1]
			g.mouseUser = request.user
			g.save()
			request.session["gameID"] = g.id
			return HttpResponse("True")
		else:
			return HttpResponse("False")

#Autor Alfonso Bonilla
def cat_move(request):
	#Obtenemos y convertimos a entero para poder operar el origen y el destino
	origin = int(request.POST.get('origin'))
	target = int(request.POST.get('target'))

	#A partir del gameID guardado en sesion, obtenemos la instancia del juego
	gameID = request.session['gameID']
	g = Game.objects.filter(id=gameID)
	game = g[0]

	#Obtenemos las posiciones de los gatos y el raton del tablero, para las comprobaciones
	cat1 = game.cat1
	cat2 = game.cat2
	cat3 = game.cat3
	cat4 = game.cat4
	mouse = game.mouse

	#Gato1 solo se mueve hacia delante.por eso solo suma en las comprobaciones
	if cat1 == origin:
		if target < origin:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }
		if target != origin+7 and target != origin+9:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if (target == origin+7 and (origin+8)%8 != 0 ) or (target == origin+9 and (origin+9)%8 != 0):
			if target == cat2 or target == cat3 or target == cat4 or target == mouse:
				return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Gato o raton en destino", 'moveDone': False }
			game.cat1 = target
			game.catTurn = False
			game.save()
			move = Move (origin=origin, target=target , game= game)
			move.save()

			return {'move_form': MoveForm(request.POST) ,'game': game, 'move': move, 'moveDone': True }
		else:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

	#Gato2 solo se mueve hacia delante.por eso solo suma en las comprobaciones
	elif cat2 == origin:
		if target < origin:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if target != origin+7 and target != origin+9:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if (target == origin+7 and (origin+8)%8 != 0 ) or (target == origin+9 and (origin+9)%8 != 0):
			if target == cat1 or target == cat3 or target == cat4  or target == mouse:
				return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Gato o raton en destino", 'moveDone': False }
			game.cat2 = target
			game.catTurn = False
			game.save()
			move = Move (origin=origin, target=target , game= game)
			move.save()


			return {'move_form': MoveForm(request.POST) ,'game': game, 'move': move, 'moveDone': True }
		else:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

	#Gato3 solo se mueve hacia delante.por eso solo suma en las comprobaciones
	elif cat3 == origin:
		if target < origin:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if target != origin+7 and target != origin+9:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if (target == origin+7 and (origin+8)%8 != 0 ) or (target == origin+9 and (origin+9)%8 != 0):
			if target == cat1 or target == cat2 or target == cat4  or target == mouse:
				return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Gato o raton en destino", 'moveDone': False }
			game.cat3 = target
			game.catTurn = False
			game.save()
			move = Move (origin=origin, target=target , game= game)
			move.save()

			return {'move_form': MoveForm(request.POST) ,'game': game, 'move': move, 'moveDone': True }
		else:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

	#Gato4 solo se mueve hacia delante.por eso solo suma en las comprobaciones
	elif cat4 == origin:
		if target < origin:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if target != origin+7 and target != origin+9:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }

		if (target == origin+7 and (origin+8)%8 != 0 ) or (target == origin+9 and (origin+9)%8 != 0):
			if target == cat1 or target == cat2 or target == cat3  or target == mouse:
				return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Gato o raton en destino", 'moveDone': False }
			game.cat4 = target
			game.catTurn = False
			game.save()
			move = Move (origin=origin, target=target , game= game)
			move.save()

			return {'move_form': MoveForm(request.POST) ,'game': game, 'move': move, 'moveDone': True }
		else:
			return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal descendente", 'moveDone': False }
	else:
		return { 'move_form': MoveForm(request.POST), 'game': game, 'error':"No hay Gato en esa posicion de origen", 'moveDone': False}


#Autor Alfonso Bonilla
def mouse_move(request):
	#Obtenemos y convertimos a entero para poder operar el destino
	target = int(request.POST.get('target'))

	#A partir del gameID guardado en sesion, obtenemos la instancia del juego
	gameID = request.session['gameID']
	g = Game.objects.filter(id=gameID)
	game = g[0]

	if target < 0 or target >63:
		return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Cannot create a move", 'moveDone': False }

	#Obtenemos las posiciones de los gatos y el raton del tablero, para las comprobaciones
	cat1 = game.cat1
	cat2 = game.cat2
	cat3 = game.cat3
	cat4 = game.cat4
	mouseOrigin = game.mouse

	#COmprobacion de que la casilla destino no este ocupada
	if target == cat1 or target == cat2 or target == cat3 or target == cat4:
		return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Gato en destino", 'moveDone': False }

	if ((target == mouseOrigin+7 and (mouseOrigin+8)%8 != 0 ) or (target == mouseOrigin+9 and (mouseOrigin+9)%8 != 0)
			or (target == mouseOrigin-7 and (mouseOrigin-7)%8 != 0 ) or (target == mouseOrigin-9 and (mouseOrigin-8)%8 != 0)):
		game.mouse = target
		game.catTurn = True
		game.save()
		move = Move ( origin=mouseOrigin, target=target , game=game)
		move.save()

		#Movimiento correcto
		return {'move_form': MoveForm(request.POST) ,'game': game, 'move': move, 'moveDone': True }
	else:
		return {'move_form': MoveForm(request.POST) ,'game': game, 'error':"Solo puedes moverte diagonal", 'moveDone': False }

#Autor Alfonso Bonilla
def move(request):
	#Restringido el acceso a solo usuarios logeados
	if request.user.is_authenticated():

		if request.method == 'POST':
			form = MoveForm(request.POST)
			# Have we been provided with a valid form?
			if form.is_valid():

				if 'amIcat' in request.session and 'gameID' in request.session:
					amIcat = request.session['amIcat']
					gameID = request.session['gameID']
				else:
					return render(request, 'server/move.html', {'error': "No estas unido ni has creado un juego"})

				#Obtenemos la instancia del juego usando el id guardado en sesion
				gameID = request.session['gameID']
				g = Game.objects.filter(id=gameID)
				game = g[0]

				if game.mouseUser == None:
					return render(request, 'server/move.html', {'error': "Cannot create a move: I valid game requires a mouse user"})

				#Soy un gato y no es mi turno => ERROR
				if game.catTurn == False and amIcat == True:
					return render(request, 'server/move.html', {'error': "Cannot create a move"})

				#Soy un raton y no es mi turno => ERROR
				if game.catTurn == True and amIcat == False:
					return render(request, 'server/move.html', {'error': "Cannot create a move"})

				#Soy un gato y es mi turno => cat_move
				if game.catTurn == True and amIcat == True:
					dicc = cat_move(request)

				#Soy un raton y es mi turno => mouse_move
				if game.catTurn == False and amIcat == False:
					dicc = mouse_move(request)

			else:
				# The supplied form contained errors - just print them to the terminal.
				print form.errors
		else:
			# If the request was not a POST, display the form to enter details.
			form = MoveForm()
			dicc = {'move_form': form}
		return render(request, 'server/move.html', dicc)

	else:
		#en caso de no estar logeado vaos a login.html con mensaje de error
		return render(request, 'server/login.html', {'error': 'Tienes que logearte primero'})

#Autor Alfonso Bonilla
def status_turn(request):
	context_dict = {}

	if 'amIcat' in request.session and 'gameID' in request.session:
		amIcat = request.session['amIcat']
		gameID = request.session['gameID']
		#obtenemos la instnacia del juego usando el id guardado en sesion
		game = Game.objects.filter(id=gameID)
		catTurn = game[0].catTurn

		#Si el usuario es gato y es el turno de gato, entonces turno true
		if catTurn == True and amIcat == True:
			context_dict['turno'] = True
			context_dict['jugador'] = "Gato"
			context_dict['turno_mensaje'] = "Es tu turno, puedes mover"
		#si el usuario es raton y el turno es de raton, entonces turno true
		elif catTurn == False and amIcat == False:
			context_dict['turno'] = True
			context_dict['jugador'] = "Raton"
			context_dict['turno_mensaje'] = "Es tu turno, puedes mover"
		#si el usuario es gato y el turno es de raton, entonces turno false
		elif catTurn == False and amIcat == True:
			context_dict['turno'] = False
			context_dict['jugador'] = "Gato"
			context_dict['turno_mensaje'] = "No es tu turno, espera a que mueva el Raton"
		#cualquier otro caso, turno false
		else:
			context_dict['turno'] = False
			context_dict['jugador'] = "Raton"
			context_dict['turno_mensaje'] = "No es tu turno, espera a que mueva el Gato"
	else:
		#si no hay variables de sesion es que no hay juego, asique false
		context_dict['turno'] = False

	return context_dict

#Autor Alfonso Bonilla
def status_board(request):
	#Restringido el acceso a solo usuarios logeados
	if request.user.is_authenticated():
		username = request.user.username

		if 'gameID' in request.session:
			gameID = request.session['gameID']

			#Obtenemos la instancia del juego usando id guardado en sesion
			g = Game.objects.filter(id=gameID)
			game = g[0]

			if game.mouseUser == None:
				return HttpResponseRedirect('/server/join_game')
			#creamos la lista de 64 celdas
			board = list(range(0,64))

			#ponemos el tablero a todo 0
			for i in range(64):
				board[i] = 0
 			#recogemos la posicion de los gatos y raton para ponerlos en el board
			board[game.cat1] = 1
			board[game.cat2] = 1
			board[game.cat3] = 1
			board[game.cat4] = 1
			board[game.mouse] = -1
		else:
			#Si no hay ningun juego activo el board es nulo
			context_dict = {}
			context_dict['index'] = True
			context_dict['error'] = "No tienes ningun juego actualmente"

			return render(request, 'server/index.html', context_dict)

		context_dict = status_turn(request)
		context_dict['board'] = board
		context_dict['username'] = username

		cat = request.session['amIcat']

		if cat == True:
			context_dict['mouse'] = "opacity: 0.7"
		else:
			context_dict['cat'] = "opacity: 0.7"

		if request.is_ajax():
			template = "server/game_ajax.html"
		else:
			template = "server/game.html"

		return render(request, template, context=context_dict)
	else:
		#en caso de no estar logeado vaos a login.html con mensaje de error
		return render(request, 'server/login.html', {'error': 'Tienes que logearte primero'})

def winner_or_looser(request):
	#Restringido el acceso a solo usuarios logeados
	if request.user.is_authenticated():

		context_dict = {}

		#A partir del gameID guardado en sesion, obtenemos la instancia del juego
		gameID = request.session['gameID']
		g = Game.objects.filter(id=gameID)
		game = g[0]

		#Obtenemos las posiciones de los gatos y el raton del tablero, para las comprobaciones
		cat1 = game.cat1
		cat2 = game.cat2
		cat3 = game.cat3
		cat4 = game.cat4
		mouse = game.mouse

		cat = request.session['amIcat']

		#obtenemos el gato mas atrasado
		mincat = min(cat1, cat2, cat3, cat4)

		#Si la posicion del raton ha superado la del gato mas atrasado, ha ganado el raton
		if mouse//8 == mincat//8:
			context_dict['final_game'] = True
			del request.session['gameID']
			request.session.modified = True
			if cat == False:
				context_dict['winner'] = True
				context_dict['exclamacion'] = "Enhorabuena"
				context_dict['mensaje'] = "Has conseguido superar a los Gatos"
			else:
				context_dict['winner'] = False
				context_dict['exclamacion'] = "Que Pena"
				context_dict['mensaje'] = "El Raton ha ganado :("


		#creamos la lista de 64 celdas
		board = list(range(0,64))

		#ponemos el tablero a todo 0
		for i in range(64):
			board[i] = 0
			#recogemos la posicion de los gatos y raton para ponerlos en el board
		board[game.cat1] = 1
		board[game.cat2] = 1
		board[game.cat3] = 1
		board[game.cat4] = 1
		board[game.mouse] = -1

		if mouse == 63:
			if board[55] == 1 and board[62] == 1:

				context_dict['final_game'] = True
				del request.session['gameID']
				request.session.modified = True
				if cat == False:
					context_dict['winner'] = False
					context_dict['exclamacion'] = "Que Pena"
					context_dict['mensaje'] = "Los Gatos te han rodeado :("

				else:
					context_dict['winner'] = True
					context_dict['exclamacion'] = "Enhorabuena"
					context_dict['mensaje'] = "Has conseguido redear al Raton"

		#No tenemos que comporbar la casilla 0, porque si raton esta en 0 ha ganado en las condiciones de arriba


		if mouse % 8 == 0:
			if board[mouse-7] == 1 and board[mouse+9] == 1:
				context_dict['final_game'] = True
				del request.session['gameID']
				request.session.modified = True
				if cat == False:
					context_dict['winner'] = False
					context_dict['exclamacion'] = "Que Pena"
					context_dict['mensaje'] = "Los Gatos te han rodeado :("

				else:
					context_dict['winner'] = True
					context_dict['exclamacion'] = "Enhorabuena"
					context_dict['mensaje'] = "Has conseguido redear al Raton"

		if mouse+1 % 8 == 0:
			if board[mouse+7] == 1 and board[mouse-9] == 1:
				context_dict['final_game'] = True
				del request.session['gameID']
				request.session.modified = True
				if cat == False:
					context_dict['winner'] = False
					context_dict['exclamacion'] = "Que Pena"
					context_dict['mensaje'] = "Los Gatos te han rodeado :("

				else:
					context_dict['winner'] = True
					context_dict['exclamacion'] = "Enhorabuena"
					context_dict['mensaje'] = "Has conseguido redear al Raton"

		if mouse <= 7 :
			if board[mouse+7] == 1 and board[mouse+9]:
				context_dict['final_game'] = True
				del request.session['gameID']
				request.session.modified = True
				if cat == False:
					context_dict['winner'] = False
					context_dict['exclamacion'] = "Que Pena"
					context_dict['mensaje'] = "Los Gatos te han rodeado :("

				else:
					context_dict['winner'] = True
					context_dict['exclamacion'] = "Enhorabuena"
					context_dict['mensaje'] = "Has conseguido redear al Raton"

		if mouse >= 56 :
			if board[mouse-7] == 1 and board[mouse-9]:
				context_dict['final_game'] = True
				del request.session['gameID']
				request.session.modified = True
				if cat == False:
					context_dict['winner'] = False
					context_dict['exclamacion'] = "Que Pena"
					context_dict['mensaje'] = "Los Gatos te han rodeado :("

				else:
					context_dict['winner'] = True
					context_dict['exclamacion'] = "Enhorabuena"
					context_dict['mensaje'] = "Has conseguido redear al Raton"




		#comprobacionde si los gatos han ganado
		if mouse > 8 and mouse <55:
			if board[mouse+7] == 1 and board[mouse+9] == 1 and board[mouse-7] == 1 and board[mouse-7] == 1:
				context_dict['final_game'] = True
				del request.session['gameID']
				request.session.modified = True
				if cat == False:
					context_dict['winner'] = False
					context_dict['exclamacion'] = "Que Pena"
					context_dict['mensaje'] = "Los Gatos te han rodeado :("

				else:
					context_dict['winner'] = True
					context_dict['exclamacion'] = "Enhorabuena"
					context_dict['mensaje'] = "Has conseguido redear al Raton"



		return render(request, 'server/final_game.html', context_dict)

	else:
		#en caso de no estar logeado vaos a login.html con mensaje de error
		return render(request, 'server/login.html', {'error': 'Tienes que logearte primero'})

def show(request):

	context_dict = {}
	games = Game.objects.filter().order_by('-id')

	if games.exists():
		game = games[0]
		request.session["showGame"] = game.id

		#creamos la lista de 64 celdas
		board = list(range(0,64))

		#ponemos el tablero a todo 0
		for i in range(64):
			board[i] = 0

		#recogemos la posicion de los gatos y raton para ponerlos en el board
		board[game.cat1] = 1
		board[game.cat2] = 1
		board[game.cat3] = 1
		board[game.cat4] = 1
		board[game.mouse] = -1

		context_dict['board'] = board

		if request.is_ajax():
			template = "server/show_ajax.html"
		else:
			template = "server/show.html"


	else:
		context_dict['error'] = "No hay ningun juego que mirar"
		template = "server/show.html"

	return render(request, template, context=context_dict)

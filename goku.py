from __future__ import division, print_function, unicode_literals
# This code is so you can run the samples without installing the package
import sys
import os
import math
import time
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "tiles, Driver"
from cocos.scenes.transitions import FadeTRTransition
import pyglet
from pyglet.window import key
from pyglet.gl import *
from pyglet import gl
from cocos.director import director
pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer, sprite
from cocos.tiles import load, RectMapCollider


class UILayer(cocos.layer.Layer):

   	#window_height = 540
	#window_width = 960
	kills_legend = 'Kills: '
	heartsheet = pyglet.resource.image('hearts.png')
	heartgrid=pyglet.image.ImageGrid(heartsheet,1,5,80,110)
	heartimage=heartgrid[0,0]
	def __init__(self,game):

		super( UILayer, self ).__init__()
		self.game = game
		width, height = cocos.director.director.get_window_size()
		self.hearts={}
		self.heart1 = cocos.sprite.Sprite(UILayer.heartimage)
		self.heart2 = cocos.sprite.Sprite(UILayer.heartimage)
		self.heart3 = cocos.sprite.Sprite(UILayer.heartimage)
		#labelPos = (width * 0.1, height * 0.95)
		self.numLives=3
		labelPos_kills = (90, 513)
		self.kills_label = cocos.text.Label(
		      UILayer.kills_legend + str(0),
		      font_name = 'Arial',
		      font_size = 20,
		      anchor_x = 'center',
		      anchor_y = 'center',
		      color = (255, 255, 255, 255))
		labelPos_lives= (80,480)
		self.lives_label = cocos.text.Label(
		      "Lives:",
		      font_name = 'Arial',
		      font_size = 20,
		      anchor_x = 'center',
		      anchor_y = 'center',
		      color = (255, 255, 255, 255))
		self.kills_label.position = labelPos_kills
		self.lives_label.position = labelPos_lives
		
		self.add(self.lives_label, z=10)
		self.add(self.kills_label, z=10)
		self.heart1.position = 130, 480
		self.heart2.position = 175, 480
		self.heart3.position = 220, 480
		self.heart1.scale = .5
		self.heart2.scale = .5
		self.heart3.scale = .5
		self.add(self.heart1, z=10)
		self.add(self.heart2, z=10)
		self.add(self.heart3, z=10)
		
	def updatekills(self, number):
	        self.kills_label.element.text =UILayer.kills_legend + str(number)

	def updatelives(self):
		self.numLives = self.numLives-1
		if self.numLives ==2:
			self.heart3.kill()
		if self.numLives == 1:
			self.heart2.kill()
		if self.numLives == 0:
			self.heart1.kill()
		if self.numLives<0:
			cocos.director.director.replace(FadeTRTransition(self.game.get_menu_scene(), 2))


class Background(cocos.layer.Layer):
	def __init__(self):
        	super(Background, self).__init__()
		self.image = pyglet.resource.image('wallpapers.jpg')
	def draw( self ):
        	glColor4ub(255, 255, 255, 255)
        	gl.glPushMatrix()
        	self.transform()
        	self.image.blit(100,0)
        	gl.glPopMatrix()

class Playerlayer(cocos.layer.Layer):
	is_event_handler = True
	backimg=pyglet.resource.image('landscape1.jpg')
	livesremain=3
	#faceLeft=True
	def __init__(self):
		super(Playerlayer, self).__init__()
		self.playerid = 0
		self.villainid=0
		self.fireballid=0
		self.players={}
		self.villains={}
		self.fireballs={}
		self.batch = cocos.batch.BatchNode()
		self.add(self.batch)
		self.add(cocos.sprite.Sprite(Playerlayer.backimg,position=(480,270)),z=-1)
	        self.keys_being_pressed = set()
		self.do(SpriteStepAction())
		self.numkills=0
		self.isSuper=False
	def on_key_press(self, key, modifiers):
        	self.keys_being_pressed.add(key)
		if pyglet.window.key.LEFT == key:
            		self.moveLeft()
		if pyglet.window.key.RIGHT == key:
			self.moveRight()
		if pyglet.window.key.SPACE == key:
			self.shootfireball()
    	def on_key_release(self, key, modifiers):
        	if key in self.keys_being_pressed:
			if pyglet.window.key.LEFT == key:
				if self.playerid in self.players:
					player = self.players[self.playerid]				
					player.removemoveleft()
			if pyglet.window.key.RIGHT == key:
				if self.playerid in self.players:
					player = self.players[self.playerid]				
					player.removemoveright()
			if pyglet.window.key.UP ==key:
				if self.playerid in self.players:
					player = self.players[self.playerid]
					player.jump()
			self.keys_being_pressed.remove(key)
		#if pyglet.window.key.S == key and numkills>4 and isSuper==False:
		#	if self.playerid in self.players:
		#		player = self.players[self.playerid]
		#		player.gosuper()
		
				
			
	
	def addplayer(self):
		gokusheet = pyglet.resource.image('kid_goku.png')
		gokugrid=pyglet.image.ImageGrid(gokusheet,13,13,32,32)
		gokutexture=pyglet.image.TextureGrid(gokugrid)
		playimage=gokugrid[3,0]
		new_player = Player(playimage)
		self.playerid= self.playerid+1
		self.players[self.playerid] = new_player
		new_player.start()
		self.batch.add(new_player)
		#self.add(new_player)
		new_player.shouldDie = False
		new_player.nomove=True
		#playerid++
	def moveRight(self):
		if self.playerid in self.players:
			player = self.players[self.playerid]
			player.moveright()
       	def moveLeft(self):
		if self.playerid in self.players:
			player = self.players[self.playerid]
			player.moveleft()
	def jump(self):
		if self.playerid in self.players:
			player = self.players[self.playerid]
			player.jump()
	def decreasefireball(self):
		self.fireballid = self.fireballid-1
	def shootfireball(self):
		if self.playerid in self.players:
			player = self.players[self.playerid]
		else:
			 return
			#direction to shoot
		isleft = player.ismoveleft
		isright= player.ismoveright
		if self.fireballid <1:
			if isleft:
		        	x, y = player.position
				new_fireball = FireBall(position=(x,y),isLeft=True,isup=False)
				self.batch.add(new_fireball)
				self.fireballid=self.fireballid+1
				self.fireballs[self.fireballid] = new_fireball
		        	new_fireball.start()
			elif isright:
		        	x, y = player.position
				new_fireball = FireBall(position=(x,y),isLeft=False, isup=False)
				self.fireballid=self.fireballid+1
				self.batch.add(new_fireball)
				self.fireballs[self.fireballid] = new_fireball
		        	new_fireball.start()
			else:
				x, y = player.position
				new_fireball = FireBall(position=(x,y),isLeft=False, isup=True)
				self.batch.add(new_fireball)
				self.fireballid=self.fireballid+1
				self.fireballs[self.fireballid] = new_fireball
		        	new_fireball.start()
	def addVillain(self):
		if self.villainid <1:
			new_villain = Villain()	
			self.villainid = self.villainid + 1
	 		self.villains[self.villainid] = new_villain
			self.batch.add(new_villain)
			new_villain.start()
			#self.do(cocos.actions.Delay(5)+cocos.actions.CallFuncS(Playerlayer.addVillain))
	
	def decreasevillain(self):
		self.villainid = self.villainid - 1
	
	def playerkilled(self):
		if self.playerid in self.players:
			self.players[self.playerid]= None
			self.playerid = self.playerid-1
			
	def step(self,dt):
		gotplayer=False
		gotvillain=False
		gotfireball=False
		ui_layer = self.get_ancestor(UILayer)
		if self.playerid in self.players:
			player = self.players[self.playerid]
			player_rect= player.get_rect()
			gotplayer=True
		if self.villainid in self.villains:
			villain = self.villains[self.villainid]
			villain_rect= villain.get_rect()
			gotvillain=True
		if self.fireballid in self.fireballs:
			fireball = self.fireballs[self.fireballid]
			fireball_rect = fireball.get_rect()
			gotfireball=True
		if gotplayer and gotvillain:
			if player_rect.intersects(villain_rect):
				player.killedbyvillain()
				villain.markfordeath()
				ui_layer.updatelives()
		if gotfireball and gotvillain:
			if fireball_rect.intersects(villain_rect):
				self.numkills=self.numkills+1
				ui_layer.updatekills(self.numkills)
				villain.killedbyfire()
				fireball.markForDeath()
		
class SpriteStepAction(cocos.actions.Action):
	def step(self,dt):
		self.target.step(dt)

class Villain (cocos.sprite.Sprite):
	v_image = pyglet.resource.image('villains1.png')
	v_grid=pyglet.image.ImageGrid(v_image,17,29,36,72)
	v_tex=pyglet.image.TextureGrid(v_grid)
	
	#make selection random
	villains=[v_tex[0,6],v_tex[0,7],v_tex[0,8],v_tex[0,9],v_tex[0,10],v_tex[0,11]]
	def __init__( self):
		#villain_image = Villain.v_grid[0,2]
		randY = random.random()*28
		randX = random.random()*16
		villain_image = Villain.v_grid[int(randX),0]
		self.alive=True
		super( Villain, self ).__init__(villain_image)
	def start(self):
		self.do(SpriteStepAction())
		#self.position = (1, 400)
		x= random.random() * 900
		y= random.random() * 500
		if y<40:
			#diff= 40-y
			y= 40
		self.position = x,y
		self.scale = 1
		self.velocity = (75,10 )
		self.do(actions.Move())
		self.rotation= 45
		self.shoulddie=False
		#self.do(cocos.actions.Delay(3.9)+\
			#cocos.actions.CallFuncS(Villain.markfordeath))
	def markfordeath(self):
		self.shoulddie=True
	def killedbyfire(self):
		self.velocity = 0,0
		self.image = explosion_animation
		self.do(cocos.actions.Delay(1)+\
			cocos.actions.CallFuncS(Villain.markfordeath))
	def step (self,dt):
		playlayer=self.get_ancestor(Playerlayer)
		#fireball = playlayer.fireballs[0]
		x,y=self.position
		if x>window_width or x<0 or y<0 or y>window_height:
			self.markfordeath()
		if self.shoulddie == True:
			self.stop()			
			self.kill()
			playlayer.decreasevillain()
			playlayer.addVillain()
		#else:
		
		#x,y = self.velocity
		#self.velocity = (x+.1, y-.5)
		
	
class FireBall(cocos.sprite.Sprite):
	kamehamehaR_image = pyglet.resource.image('kamehameha1.png')
	kamehamehaR_grid=pyglet.image.ImageGrid(kamehamehaR_image,2,13,74,57)
	kameR_tex=pyglet.image.TextureGrid(kamehamehaR_grid)
	kamehamehaR=[kameR_tex[0,6],kameR_tex[0,7],kameR_tex[0,8],kameR_tex[0,9],kameR_tex[0,10],kameR_tex[0,11]]
	kamehamehaL_image = pyglet.resource.image('kamehamehaleft.png')
	kamehamehaL_grid=pyglet.image.ImageGrid(kamehamehaL_image,2,13,74,57)
	kameL_tex=pyglet.image.TextureGrid(kamehamehaL_grid)
	kamehamehaL=[kameL_tex[0,7],kameL_tex[0,6],kameL_tex[0,5],kameL_tex[0,4],kameL_tex[0,3],kameL_tex[0,2]]
	def __init__( self,position,isLeft,isup ):
		self.isleft=isLeft
		self.isup = isup
		fireball_position = position
		#self.image = cocos.sprite.Sprite(FireBall.fireanim)
		fball_image = FireBall.kameR_tex[(0,6)]
		self.alive=True
		super( FireBall, self ).__init__(fball_image,fireball_position)
	def markForDeath(self):
		self.alive=False
	def start(self):
		self.do(SpriteStepAction())
		self.do(cocos.actions.Delay(1.1)+\
			cocos.actions.CallFuncS(FireBall.markForDeath))
		if self.isleft and self.isup==False:
			self.image = pyglet.image.Animation.from_image_sequence(FireBall.kamehamehaL,.2, loop=False)
			self.do(actions.MoveBy((-300,0),1))
		elif self.isleft==False and self.isup==False:
			self.image = pyglet.image.Animation.from_image_sequence(FireBall.kamehamehaR,.2, loop=False)
			self.do(actions.MoveBy((300,0),1))
		elif self.isup==True:
			self.do(actions.MoveBy((0,300),1))
			self.image = pyglet.image.Animation.from_image_sequence(FireBall.kamehamehaR,.2, loop=False)
			self.rotation =-89
	def step(self,dt):
		if self.alive == False:
			self.stop()
			self.kill()
			playlayer=self.get_ancestor(Playerlayer)
			playlayer.decreasefireball()
			
class Player (cocos.sprite.Sprite):
	gokusheet = pyglet.resource.image('kid_goku.png')
	gokugrid=pyglet.image.ImageGrid(gokusheet,13,13,32,31)
	gokutexture=pyglet.image.TextureGrid(gokugrid)
	gokuwalkright=[gokutexture[2,1],gokutexture[2,5]]
	gokuwalkleft=[gokutexture[2,2],gokutexture[2,6]]
	gokustand = gokugrid[3,0]
	leftjump=gokugrid[10,3]
	rightjump=gokugrid[10,2]
	
	
	
	
	
	def __int__(self, player_id=None, id=None, position=(0, 0), rotation=0, scale=1, opacity = 255, color=(255, 255, 255), anchor=None):
		self.player_id = player_id
		self.image = Player.gokugrid[3,0]
		self.alive=True
		super(Player, self).__init__(Player.gokustand, scale=3)
	def moveleft(self):
		if not self.hit and self.goingSuper==False and self.isjump==False:
			self.image=pyglet.image.Animation.from_image_sequence(Player.gokuwalkleft,.05, loop=True)
			self.ismoveleft=True
	def moveright(self):
		if not self.hit and self.goingSuper==False and self.isjump==False:
			self.image=pyglet.image.Animation.from_image_sequence(Player.gokuwalkright,.05, loop=True)
			self.ismoveright=True
	def removemoveleft(self):
		self.ismoveleft=False
	def removemoveright(self):
		self.ismoveright=False
	def jump(self):
		jumpheight=80
		jumpwidth=100
		jumptime=.4
		if self.isjump==False:
			self.isjump=True
			if self.ismoveleft==True:
				self.do(actions.MoveBy((-jumpwidth,jumpheight),jumptime)+actions.MoveBy((-jumpwidth,-jumpheight),jumptime)+actions.CallFuncS(Player.markjumpfinished))
			elif self.ismoveright==True:
				self.do(actions.MoveBy((jumpwidth,jumpheight),jumptime)+actions.MoveBy((jumpwidth,-jumpheight),jumptime)+actions.CallFuncS(Player.markjumpfinished))
			else:
				self.do(actions.MoveBy((0,jumpheight),jumptime)+actions.MoveBy((0,-jumpheight),jumptime)+actions.CallFuncS(Player.markjumpfinished))
	def markjumpfinished(self):
		self.isjump=False
	def changemoveleft(self):
		ismoveleft = False
	def gosuper(self):
		self.isSuper= True
		self.goingSuper = True
		
		
	def start(self):
		self.isjump= False
		self.goingSuper=False
		self.isSuper = False
		self.hit = False
		self.alive=True
		self.scale = 2
		self.position = (400,75)
        	self.do(SpriteStepAction())
		self.ismoveleft=False
		self.ismoveright=False
		self.nomove=True
	def markfordeath(self):
		self.alive=False
	def killedbyvillain(self):
		self.hit=True
		self.image = explosion_animation
		self.do(cocos.actions.Delay(1)+\
			cocos.actions.CallFuncS(Player.markfordeath))
	def step(self, dt):
		if self.alive and not self.hit and self.isjump==False:
			if self.ismoveleft ==False and self.ismoveright==False:
				self.image = Player.gokugrid[3,0]
			elif self.ismoveleft == True and self.ismoveright==False:
				self.do(actions.MoveBy((-7,0),.05))
			elif self.ismoveright == True and self.ismoveleft ==False:
				self.do(actions.MoveBy((7,0),.05))
		x,y=self.position
		if x>window_width:
			self.position = 4,y
		elif x<2:
			self.position = 955,y
		if not self.alive:
			self.stop()
			self.kill()
			playlayer=self.get_ancestor(Playerlayer)
			playlayer.playerkilled()
			self.do(cocos.actions.Delay(4)+cocos.actions.CallFuncS(playlayer.addplayer()))
			
class PlayLayerAction(cocos.actions.Action):
    def handleLocalKeyboard(self):
        #if pyglet.window.key.LEFT in self.target.keys_being_pressed:
            #self.target.moveLeft(0)
        #if pyglet.window.key.RIGHT in self.target.keys_being_pressed:
            #self.target.moveRight(0)
        if pyglet.window.key.UP in self.target.keys_being_pressed:
		x=2
            #self.target.thrustPlayer(self.target.ownID)

    def step(self, dt):
        self.handleLocalKeyboard()
        #CommonLayers.GameSprite.handleCollisions()
        #self.spawnAsteroids()
class IntroMenu(cocos.menu.Menu):
	backimg = pyglet.resource.image('wallpapers.jpg')
	def __init__( self, game):
		super( IntroMenu, self ).__init__()
		self.font_item = {
		    'font_name': 'Arial',
		    'font_size': 32,
		    'bold': True,
		    'color': (220, 200, 220, 100),
		}
		self.game = game
		self.font_item_selected = {
		    'font_name': 'Arial',
		    'font_size': 42,
		    'bold': True,
		    'color': (255, 255, 255, 255),
		}
		l = []
		l.append( cocos.menu.MenuItem('Join Game',
		    self.game.Join_game ) )
		l.append(cocos.menu.MenuItem('Quit', self.game.On_quit ) )
		self.create_menu(l)
	
class Game(object):
	def __init__(self):
		super( Game, self ).__init__()
		director.init(width=960, height=540, autoscale=True, resizable=False)
		menu_layer= IntroMenu(self)
		background_layer = Background()
		background_layer.add(menu_layer)
		self.menu_scene = cocos.scene.Scene(background_layer)
	def On_quit(self):
		pyglet.app.exit()
	def Join_game(self):
		ui_layer = UILayer(self)
		player_layer = Playerlayer()
		player_layer.do(PlayLayerAction())
		player_layer.addplayer()
		player_layer.addVillain()
		ui_layer.add(player_layer)
		main_play_scene = cocos.scene.Scene(ui_layer)
		cocos.director.director.replace(FadeTRTransition(main_play_scene, 2))
	def get_menu_scene(self):
		menu_layer= IntroMenu(self)
		background_layer = Background()
		background_layer.add(menu_layer)
		menu_scene = cocos.scene.Scene(background_layer)
		return menu_scene
	def run(self):
		director.run(self.get_menu_scene())
		
def main():
	global window_height,window_width,explosion_animation
	window_height = 540
	window_width = 960

	small_image = pyglet.resource.image('explosionSmall.png')
    	small_grid = pyglet.image.ImageGrid(small_image, 5, 5)
    	small_textures = pyglet.image.TextureGrid(small_grid)
    	small_textures_list = small_textures[:]
    	frame_period = 0.05
    	explosion_animation = pyglet.image.Animation.from_image_sequence(small_textures_list, frame_period, loop=True)
	game = Game()
	game.run()

	

if __name__ == '__main__':
    main()	


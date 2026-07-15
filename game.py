"""Game state machine for Fruit Slice AI."""
from __future__ import annotations
import json, math, random
import pygame
from bomb import Bomb
from effects import Effects, SoundBank
from fruit import Fruit
from hand_tracker import HandTracker
from settings import *
from ui import Button, camera_preview, text


class FruitSliceGame:
    def __init__(self) -> None:
        pygame.init(); pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock(); self.running = True; self.fullscreen = False
        self.font = pygame.font.Font(None, 34); self.big = pygame.font.Font(None, 76); self.small = pygame.font.Font(None, 23)
        self.tracker = HandTracker(WEBCAM_INDEX); self.sound = SoundBank(); self.effects = Effects()
        self.state, self.difficulty = "menu", "Medium"; self.buttons = []; self.high_scores = self._load_scores()
        self.finger = self.previous_finger = None; self.menu_time = 0; self.reset_game()

    def _load_scores(self):
        try: return json.loads(HIGH_SCORES_FILE.read_text())
        except (OSError, json.JSONDecodeError): return []
    def _save_score(self):
        self.high_scores.append({"score": self.score, "difficulty": self.difficulty})
        self.high_scores = sorted(self.high_scores, key=lambda s:s["score"], reverse=True)[:10]
        DATA_DIR.mkdir(exist_ok=True); HIGH_SCORES_FILE.write_text(json.dumps(self.high_scores, indent=2))
    def reset_game(self):
        self.score, self.lives, self.combo, self.combo_clock = 0, 10, 0, 0
        self.fruits, self.spawn_clock, self.elapsed, self.was_saved = [], 0, 0, False
        self.effects = Effects()
    def run(self):
        while self.running:
            dt = min(self.clock.tick(TARGET_FPS)/1000, .05); self.menu_time += dt
            self._events(); self.finger = self.tracker.update(self.screen.get_size())
            self._update(dt); self._draw(dt)
        self.tracker.close(); pygame.quit()
    def _events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: self.running=False
            elif e.type == pygame.VIDEORESIZE and not self.fullscreen: self.screen=pygame.display.set_mode(e.size, pygame.RESIZABLE)
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11: self._toggle_fullscreen()
    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.screen = pygame.display.set_mode((0,0) if self.fullscreen else (WINDOW_WIDTH,WINDOW_HEIGHT), pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE)
    def _set_buttons(self, labels):
        """Place buttons in screen-specific safe zones instead of over content."""
        w, h = self.screen.get_size()
        layouts = {
            "menu": (h // 2 - 85, 64),
            "difficulty": (h // 2 - 72, 70),
            "settings": (h // 2 - 36, 76),
            "paused": (h // 2 - 40, 72),
            "gameover": (h // 2 + 32, 70),
        }
        if self.state == "instructions":
            centers = [(w // 2, h - 70)]
        elif self.state == "scores":
            # Always below the longest six-row score list.
            centers = [(w // 2, max(400, min(450, h - 70)))]
        else:
            start, spacing = layouts.get(self.state, (h // 2, 72))
            centers = [(w // 2, start + i * spacing) for i in range(len(labels))]
        self.buttons = [Button(label, center) for label, center in zip(labels, centers)]
    def _update(self, dt):
        self.effects.update(dt)
        if self.state == "playing": self._play_update(dt)
        else: self._menu_update(dt)
        self.previous_finger = self.finger
    def _menu_update(self, dt):
        layouts={"menu":["Play","Instructions","Settings","High Scores","Exit"], "difficulty":["Easy","Medium","Hard","Back"], "instructions":["Back"], "settings":["Toggle Full Screen","Back"], "paused":["Resume","Restart","Main Menu"], "gameover":["Play Again","Main Menu","High Scores"], "scores":["Back"]}
        labels=layouts.get(self.state,[])
        if len(self.buttons)!=len(labels) or [b.label for b in self.buttons]!=labels: self._set_buttons(labels)
        for button in self.buttons:
            if button.update(self.finger,dt): self._action(button.label)
    def _action(self, action):
        self.sound.play("click")
        if action=="Play": self.state="difficulty"; self.buttons=[]
        elif action in DIFFICULTIES: self.difficulty=action; self.reset_game(); self.state="playing"; self.buttons=[]
        elif action=="Instructions": self.state="instructions"; self.buttons=[]
        elif action=="Settings": self.state="settings"; self.buttons=[]
        elif action=="High Scores": self.state="scores"; self.buttons=[]
        elif action=="Toggle Full Screen": self._toggle_fullscreen(); self.buttons=[]
        elif action=="Resume": self.state="playing"; self.buttons=[]
        elif action=="Restart" or action=="Play Again": self.reset_game(); self.state="playing"; self.buttons=[]
        elif action=="Main Menu" or action=="Back": self.state="menu"; self.buttons=[]
        elif action=="Exit": self.running=False
    def _play_update(self,dt):
        if self.finger and self.previous_finger and math.dist(self.finger,self.previous_finger)>7:
            for item in self.fruits[:]:
                if item.hit(self.previous_finger,self.finger): self._slice(item)
        self.elapsed+=dt; self.spawn_clock-=dt; cfg=DIFFICULTIES[self.difficulty]
        if self.spawn_clock<=0:
            speed=cfg["speed_multiplier"]*(1+self.elapsed/170)
            self.fruits.append(Bomb(*self.screen.get_size(),speed) if random.random()<cfg["bomb_chance"] else Fruit(*self.screen.get_size(),speed))
            self.spawn_clock=max(.25,cfg["spawn_interval"]-self.elapsed*.0015)*random.uniform(.72,1.15)
        for item in self.fruits[:]:
            item.update(dt)
            if item.is_offscreen(self.screen.get_height()):
                self.fruits.remove(item)
                if not isinstance(item,Bomb): self._lose_life(item.x,item.y,"MISSED")
        self.combo_clock-=dt
        if self.combo_clock<=0: self.combo=0
    def _slice(self,item):
        if item not in self.fruits:return
        self.fruits.remove(item)
        if isinstance(item,Bomb):
            self.effects.burst(item.x,item.y,DANGER_COLOR,44,True); self.sound.play("boom"); self._lose_life(item.x,item.y,"BOMB!")
        else:
            self.combo = self.combo+1 if self.combo_clock>0 else 1; self.combo_clock=1.35
            gained=10+(self.combo-1)*5; self.score+=gained
            self.effects.burst(item.x,item.y,item.color,24); self.effects.label(f"+{gained}"+(f"  x{self.combo} COMBO" if self.combo>1 else ""),item.x,item.y,GOLD)
            self.sound.play("slice")
    def _lose_life(self,x,y,label):
        self.lives-=1; self.effects.label(label,x,y,DANGER_COLOR)
        if self.lives<=0:
            self.state="gameover"; self.buttons=[]; self.sound.play("gameover")
            if not self.was_saved: self._save_score(); self.was_saved=True
    def _background(self):
        w,h=self.screen.get_size()
        for y in range(0,h,3):
            p=y/max(1,h); c=tuple(int(BACKGROUND_TOP[i]+(BACKGROUND_BOTTOM[i]-BACKGROUND_TOP[i])*p) for i in range(3)); pygame.draw.rect(self.screen,c,(0,y,w,3))
        for i in range(10):
            x=(i*181+self.menu_time*20*(i%2*2-1))%w; pygame.draw.circle(self.screen,(255,255,255),(int(x),int(80+i*71)),2)
    def _draw(self,dt):
        self._background(); w,h=self.screen.get_size()
        if self.state=="playing":
            for f in self.fruits:f.draw(self.screen)
            self._hud(w); self.effects.draw(self.screen,self.font)
            # A dwell zone at top-right pauses the game without keyboard input.
            pause=Button("PAUSE",(w-82,32),(120,42)); pause.draw(self.screen,self.small)
            if pause.update(self.finger,dt): self.state="paused"; self.buttons=[]; self.sound.play("click")
        else: self._draw_screen(w,h)
        if self.finger:
            pygame.draw.circle(self.screen,(255,255,255),(int(self.finger[0]),int(self.finger[1])),17,2); pygame.draw.circle(self.screen,ACCENT_COLOR,(int(self.finger[0]),int(self.finger[1])),5)
        camera_preview(self.screen, self.tracker.preview, self.tracker.landmarks, (16, h - 196))
        text(self.screen,self.small,f"{self.clock.get_fps():.0f} FPS",(w-42,h-16),MUTED_TEXT)
        pygame.display.flip()
    def _hud(self,w):
        text(self.screen,self.font,f"SCORE  {self.score}",(25,22),center=False); text(self.screen,self.font,"♥ "*self.lives,(25,58),DANGER_COLOR,False)
        text(self.screen,self.small,self.difficulty.upper(),(w//2,27),GOLD)
        if self.combo>1: text(self.screen,self.font,f"{self.combo}x COMBO",(w//2,64),GOLD)
    def _draw_screen(self,w,h):
        title={"menu":TITLE,"difficulty":"CHOOSE DIFFICULTY","instructions":"HOW TO PLAY","settings":"SETTINGS","paused":"PAUSED","gameover":"GAME OVER","scores":"HIGH SCORES"}.get(self.state,TITLE)
        text(self.screen,self.big,title,(w//2,110),ACCENT_COLOR)
        if self.state=="menu": text(self.screen,self.font,"Slice with your index finger",(w//2,166),MUTED_TEXT)
        if self.state=="instructions":
            card = pygame.Surface((min(w - 120, 790), 190), pygame.SRCALPHA)
            pygame.draw.rect(card, (18, 27, 66, 180), card.get_rect(), border_radius=24)
            pygame.draw.rect(card, (103, 133, 203, 180), card.get_rect(), 2, border_radius=24)
            self.screen.blit(card, card.get_rect(center=(w // 2, 285)))
            lines=["Point your index finger at the camera to move the sword.","Swipe through fruit to slice it. Avoid bombs.","Missing fruit and slicing bombs cost a heart.","Hold your finger over a button to select it."]
            for i,line in enumerate(lines): text(self.screen,self.font,line,(w//2,225+i*35),TEXT_COLOR)
        if self.state=="settings": text(self.screen,self.small,"Use F11 too, if desired. Menus support hand dwell selection.",(w//2,182),MUTED_TEXT)
        if self.state=="gameover": text(self.screen,self.font,f"Final score: {self.score}",(w//2,178),GOLD)
        if self.state=="scores":
            if self.high_scores:
                for i,row in enumerate(self.high_scores[:6]):
                    color = GOLD if i==0 else TEXT_COLOR
                    text(self.screen,self.font,f"{i+1}.  {row['score']:>5}   {row['difficulty']}",(w//2,170+i*34),color)
            else: text(self.screen,self.font,"No scores yet — be the first!",(w//2,195),MUTED_TEXT)
        for b in self.buttons:b.draw(self.screen,self.font)
        if not self.tracker.available: text(self.screen,self.small,self.tracker.error,(w//2,h-35),DANGER_COLOR)

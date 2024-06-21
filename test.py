from mss import mss
import pydirectinput
import cv2
import numpy as np
import pytesseract
from matplotlib import pyplot as plt 
import time
from gymnasium import Env
from gymnasium.spaces import Box, Discrete
import os
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common import env_checker

from stable_baselines3 import DQN

class ZenithJump(Env):
    # Set up the environment action and observation space
    def __init__(self):
        #Subclass model
        super().__init__()
        # setup spaces
        self.observation_space = Box(low=0, high=255, shape=(1,83,100), dtype=np.uint8)
        self.action_space = Discrete(3)
        # Define extraction parameters for the  game
        self.cap = mss()
        self.game_location = {'top': 155, 'left': 710, 'width': 500, 'height': 760}
        self.done_location = {'top': 410, 'left': 850, 'width': 250, 'height': 50}
        self.score_location = {'top': 170, 'left': 800, 'width': 80, 'height': 25}

    # What is called to do something in game
    def step(self, action):
        # Action key - 0 = Space, 1 = Duck, 2 = Do nothing
        action = action.item()
        action_map = {0: 'left', 1: 'right', 2: 'no_op'}
        if action != 2:
            pydirectinput.press(action_map[action])

        # checking if game is done
        done, done_cap = self.get_done()
        truncated = False
        # get next observation
        new_observation = self.get_observation()
        # Reward - point for every frame we are alive
        score, score_cap = self.get_score()
        reward = score - self.last_score
        self.last_score = score

        info = {"score": score}

        return new_observation, reward, done, truncated, info

    # Visualize the game
    def render(self):
        cv2.imshow('Game', np.array(self.cap.grab(self.game_location))[:,:,:3])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.close()

    # Restart the game
    def reset(self, seed=None):
        time.sleep(0.25)
        pydirectinput.click(x=900,y=500)
        pydirectinput.press('space')
        self.last_score = 0
        return self.get_observation()

    # This closes down the obseration space
    def close(self):
        cv2.destroyAllWindows()
    # Get the part of the observation space
    def get_observation(self):
        # Get screen capture of game that we want
        raw = np.array(self.cap.grab(self.game_location))[:,:,:3]
        # Convert to grey scale
        grey = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
        # Resize the image
        resized = cv2.resize(grey, (100, 83))
        # Add channels first
        channel = np.reshape(resized, (1, 83, 100))
        return channel
    
    def get_score(self):
        # Get screen capture of the score area
        score_cap = np.array(self.cap.grab(self.score_location))[:, :, :3]
        # Use OCR to get the text
        score_str = pytesseract.image_to_string(score_cap, config='--psm 7 digits')
        # Extract numbers from the string
        score = ''.join(filter(str.isdigit, score_str))
        # Convert to integer if possible
        score = int(score) if score.isdigit() else 0
        return score, score_cap
    
    
    # Get the done text using OCR
    def get_done(self):
        # Get done screen
        done_cup = np.array(self.cap.grab(self.done_location))[:,:,:3]
        # Valid done text
        done_strings = ["GAME", "GAHE", "GAM", "GA"]

        # Use OCR to get the text
        done = False
        res = pytesseract.image_to_string(done_cup)[:4]
        if res in done_strings:
            done = True

        return done,done_cup



env = ZenithJump()



model = DQN.load("train/new/best_model_200000.zip", env, verbose=1, device="cpu")
for episode in range(50):
    obs = env.reset()
    done = False
    total_reward = 0 
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, truncated, info = env.step(env.action_space.sample())
        total_reward += reward
    print(f"Episode {episode} finished with reward: {total_reward}")
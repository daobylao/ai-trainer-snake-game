# 🧠 AI Training Snake Game

Train your AI by consuming data in this Snake-themed learning adventure!

## 🎮 Game Overview

**AI Training Snake** puts a clever twist on the classic Snake game. Instead of just eating food, you're training an AI by consuming different types of data. As your AI gets smarter (higher IQ), it moves faster and your neural network grows!

## 🎯 Game Concept

- **Snake = AI being trained**
- **Food = Different types of data**
- **Score = IQ Level**
- **Length = Neural Network Size**
- **Speed = Learning Rate (increases with IQ)**

## 📊 Data Types

| Type | Color | IQ Points | Probability | Description |
|------|-------|-----------|-------------|-------------|
| 🟢 Basic Data | Green | +1 IQ | 70% | Common training data |
| 🟡 Quality Data | Yellow | +3 IQ | 20% | High-quality datasets |
| 🔴 Premium Data | Red | +10 IQ | 10% | Rare, premium training data (flashes!) |

## 🎮 Controls

- **⬆️⬇️⬅️➡️ Arrow Keys** - Move your AI
- **SPACE** - Pause/Resume game
- **SPACE/ENTER** - Restart after game over

## 🚀 How to Play

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the game:**
   ```bash
   python snake.py
   ```

3. **Train your AI:**
   - Move around to consume data
   - Avoid walls (AI hallucination!)
   - Avoid hitting yourself (AI confusion!)
   - Watch your IQ and neural network grow!

## ✨ Features

### Visual Effects
- **Brightness Gradient**: Snake gets brighter as IQ increases
- **Head Highlighting**: White outline on snake head
- **Premium Data Flash**: Red data flashes to grab attention
- **Neural Network Visualization**: Snake length represents network size

### Game Mechanics
- **Adaptive Speed**: AI moves faster as it gets smarter
- **Smart Growth**: Premium data makes the snake grow more
- **Pause System**: Training can be paused and resumed
- **High Score Tracking**: Persistent best IQ score

### AI Training Theme
- **Death = Training Failure**
  - Hit walls = AI hallucinated
  - Hit self = AI got confused
- **Growth = Learning**
  - Consuming data increases IQ
  - Neural network expands
- **Speed = Processing Power**
  - Smarter AI processes faster

## 🎨 Enhanced Features

This improved version includes:

- **Better Code Organization**: Clean class structure
- **Improved Visuals**: Gradient effects, better UI
- **Pause Functionality**: Space to pause/resume
- **Enhanced Game Over Screen**: Better feedback
- **Persistent High Scores**: Tracks your best performance
- **Visual Feedback**: Data type indicators, network size display
- **Smooth Gameplay**: 60 FPS with proper timing

## 🏆 Tips for High IQ

1. **Chase Premium Data**: Worth 10x basic data!
2. **Plan Your Route**: Don't trap yourself
3. **Stay Alert**: Speed increases make control harder
4. **Practice**: Neural networks need training time!

## 🛠️ Technical Details

- **Language**: Python 3.x
- **Framework**: Pygame
- **Grid Size**: 40x40 cells
- **Window Size**: 800x800 pixels
- **Frame Rate**: 60 FPS
- **Save System**: High scores saved to `high_score.txt`

## 🎲 Game Balance

- **Base Speed**: 150ms between moves
- **Speed Increase**: 3ms faster per IQ point (max 100ms faster)
- **Minimum Speed**: 60ms between moves
- **Growth Rate**: 1 segment for basic/quality, 2 for premium

---

**Ready to train your AI? Start the game and watch your neural network grow!** 🚀🧠 
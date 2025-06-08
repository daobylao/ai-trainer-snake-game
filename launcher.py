#!/usr/bin/env python3
"""
AI Training Snake Game Launcher
Choose between different game versions!
"""

import sys
import subprocess
import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the game banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║               🧠 AI TRAINING SNAKE GAME 🐍                   ║
    ║                                                              ║
    ║          Train your AI by consuming data and growing         ║
    ║            your neural network in this Snake-style          ║
    ║                    learning adventure!                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_menu():
    """Print the game version selection menu"""
    menu = """
    🎮 CHOOSE YOUR GAME VERSION:
    
    1. 🔥 ENHANCED EDITION (Recommended)
       • Full-screen adaptive resolution
       • Sound effects and particle effects
       • 10 achievements to unlock
       • Screen shake and visual feedback
       • AI level progression with colors
       • WASD + Arrow key support
    
    2. 📖 CLASSIC EDITION
       • Original clean implementation
       • Windowed mode (800x800)
       • Simple and focused gameplay
       • Perfect for beginners
    
    3. ❌ EXIT
    
    ═══════════════════════════════════════════════════════════════
    """
    print(menu)

def run_game(game_file):
    """Run the selected game"""
    try:
        print(f"\n🚀 Launching {game_file}...")
        print("📝 Note: Press ESC to exit the game anytime!")
        print("⏳ Loading...")
        
        # Run the game
        result = subprocess.run([sys.executable, game_file], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("\n✅ Game closed successfully!")
        else:
            print(f"\n⚠️ Game exited with code: {result.returncode}")
            
    except FileNotFoundError:
        print(f"\n❌ Error: {game_file} not found!")
        print("Make sure all game files are in the same directory.")
    except Exception as e:
        print(f"\n❌ Error running game: {e}")

def check_dependencies():
    """Check if pygame is installed"""
    try:
        import pygame
        print("✅ Pygame detected!")
        return True
    except ImportError:
        print("❌ Pygame not found!")
        print("\n📦 Installing pygame...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("✅ Pygame installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install pygame automatically.")
            print("Please run: pip install pygame")
            return False

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        print_banner()
        
        # Check dependencies
        if not check_dependencies():
            input("\nPress Enter to exit...")
            break
        
        print_menu()
        
        try:
            choice = input("🎯 Enter your choice (1-3): ").strip()
            
            if choice == "1":
                if os.path.exists("enhanced_snake.py"):
                    run_game("enhanced_snake.py")
                else:
                    print("\n❌ Enhanced edition not found!")
                    print("Running classic edition instead...")
                    run_game("snake.py")
                    
            elif choice == "2":
                if os.path.exists("snake.py"):
                    run_game("snake.py")
                else:
                    print("\n❌ Classic edition not found!")
                    
            elif choice == "3":
                print("\n👋 Thanks for playing AI Training Snake!")
                print("🧠 Keep training those neural networks! 🐍")
                break
                
            else:
                print("\n❌ Invalid choice! Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        # Wait for user input before returning to menu
        if choice in ["1", "2"]:
            input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main() 
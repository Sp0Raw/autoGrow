##
## Хороший пример с отулючением по нажатию клавиши
##
import keyboard #Using module keyboard
while True:#making a loop
    print("типа хуярим в бесконечном цикле")
    try: #used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('space'): #if key 'a' is pressed
            print('You Pressed Space Key!')
            break #finishing the loop
        else:
            pass
    except:
        break #if user pressed other than the given key the loop will break
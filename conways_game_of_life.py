# Conway's Game of Life
# Code by G.G.Otto

import turtle
from tkinter import *
import tkinter.filedialog as fileopen
import random

class GameFrame(Frame):
    '''represents conway's game of life'''

    def __init__(self, master, startType=None, width=60, height=40, frameMargin=5):
        '''GameFrame(master, width=40, height=40, speed=150, startType="random") -> GameFrame
        constructs the frame for conway's game of life'''
        Frame.__init__(self,master,bg="dim grey")
        self.grid()
    
        # turtle and canvas
        width = width//2*2 + 1
        height = height//2*2 + 1
        self.canvas = Canvas(self, bg="white", width=width*10-2, height=height*10-2)
        self.canvas.grid()
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.tracer(0)
        self.gameTurtle = turtle.RawTurtle(self.screen)
        self.gameTurtle.pu()
        self.gameTurtle.ht()
        self.gameTurtle.shape("square")
        self.gameTurtle.shapesize(0.45)

        self.screen.onclick(self.add_square)
        self.screen.listen()

        # set up cells
        frameMargin = frameMargin//2*2+1
        self.cellDic = {}
        for x in range(int(-(width+frameMargin)/2*10),int((width+frameMargin)/2*10)+1,10):
           for y in range(int(-(height+frameMargin)/2*10),int((height+frameMargin)/2*10)+1,10):
                self.cellDic[x, y] = False

        self.speed = StringVar(value="Normal")
        self.speeds = {"Normal":150, "Fast":20, "Medium":265, "Slow":500}

        # frame for buttons
        buttonFrame = Frame(self)
        # start/stop button
        self.startStopButton = Button(buttonFrame, text="Stop", command=self.toggle_pause)
        self.startStopButton.grid(row=0, column=0)
        # clear button
        Button(buttonFrame, text="Clear", command=self.update_grid).grid(row=0, column=1)
        # load file button
        Button(buttonFrame, text="Load Grid", command=self.load_file).grid(row=0, column=2)
        # save file button
        Button(buttonFrame, text="Save", command=self.save_grid).grid(row=0, column=3)
        # randomize button
        Button(buttonFrame, text="Random Grid", command=self.random_grid).grid(row=0, column=4)
        # speed
        OptionMenu(buttonFrame, self.speed, "Normal", "Fast", "Medium", "Slow").grid(row=0, column=6)
        # revert to last start
        self.revertButton = Button(buttonFrame, text="Reset", command=self.reset, state=DISABLED)
        self.revertButton.grid(row=0, column=5)
        buttonFrame.grid(row=1,column=0)
        
        self.isPlaying = True
        self.master = master
        self.start_game(startType)

    def get_turtle(self):
        '''GameFrame.get_turtle() -> RawTurtle
        returns the turtle of the window'''
        return self.gameTurtle
        
    def update_grid(self, newMap=(())):
        '''GameFrame(newMap) -> None
        updates the grid with newMap'''
        if newMap == (()) and self.isPlaying:
            self.toggle_pause()
            
        self.gameTurtle.clear()
        for cellPos in self.cellDic:
            if cellPos in newMap:
                self.gameTurtle.goto(cellPos)
                self.gameTurtle.stamp()
                self.cellDic[cellPos] = True
            else:
                self.cellDic[cellPos] = False
        self.screen.update()

    def num_alive_around_cell(self, cellPos):
        '''GameFrame.num_alive_around_cell(cellPos) -> int
        returns how many cells are alive and touching cellPos'''
        x, y = cellPos # unpack tuple
        
        # scan through rows and columns
        output = 0 # final count of alive cells
        for xScan in range(x-10,x+11,10):
            for yScan in range(y-10,y+11,10):
                xScan, yScan = int(xScan), int(yScan)
                
                # if cell not in board
                if (xScan,yScan) not in self.cellDic or (xScan,yScan) == cellPos:
                    continue
                if self.cellDic[xScan,yScan]:
                    output += 1
        return output

    def compile_new_map(self):
        '''GameFrame.compile_new_map() -> None
        compiles the new map and updates at the end'''
        if not self.isPlaying:
            return
        
        outputList = [] # final list of cells
        # loop through cells
        for cellPos in self.cellDic:
            isAlive = self.cellDic[cellPos]
            numAlive = self.num_alive_around_cell(cellPos)

            # game rules
            if isAlive and 1 < numAlive < 4:
                outputList.append(cellPos)
            elif not isAlive and numAlive == 3:
                outputList.append(cellPos)
            
        self.update_grid(outputList)
        self.master.after(self.speeds[self.speed.get()],self.compile_new_map)

    def compile_random_map(self):
        '''GameFrame.compile_random_map() -> list
        returns a map that is random'''
        outputList = [] # final list to output
        
        for cellPos in self.cellDic:
            if random.random() > 0.8:
                outputList.append(cellPos)
        return outputList

    def start_game(self, gameType):
        '''GameFrame.start_game(gameType) -> None
        starts the game with gameType'''
        if gameType == None:
            self.lastStart = self.compile_random_map()
        else:
            self.lastStart = self.open_map_file(gameType)
            
        self.revertButton["state"] = ACTIVE
        self.update_grid(self.lastStart)
        self.compile_new_map()

    def add_square(self, x, y):
        '''GameFrame.add_square(x, y) -> None
        adds square at (x,y)'''
        x = round(x/10)*10
        y = round(y/10)*10
        self.gameTurtle.goto(x,y)

        # clear square
        if self.cellDic[x,y]:
            self.cellDic[x,y] = False
            self.gameTurtle.color("white")
        # add square
        else:
            self.cellDic[x,y] = True

        self.gameTurtle.stamp()
        self.gameTurtle.color("black")

    def open_map_file(self, fileName):
        '''GameFrame.open_map_file(fileName) -> None
        opens the file fileName'''
        file = open(fileName, "r")
        fileMap = file.read().split()
        file.close()

        # get output
        output = []
        for cell in fileMap:
            cell = cell.split(",")
            output.append((int(cell[0]),int(cell[1])))
        return output

    def load_file(self):
        '''Game.load_file() -> None
        loads from file'''
        if self.isPlaying:
            self.toggle_pause()
        fileName = fileopen.askopenfilename()
        if fileName == '':
            return
        
        self.update_grid(self.open_map_file(fileName))
            
    def toggle_pause(self):
        '''Game.toggle_pause() -> None
        pauses or plays the game'''
        if self.isPlaying:
            self.isPlaying = False
            self.startStopButton["text"] = "Start"
        else:
            self.isPlaying = True
            self.startStopButton["text"] = "Stop"
            self.lastStart = [cell for cell in self.cellDic if self.cellDic[cell]]
            self.revertButton["state"] = ACTIVE
            self.compile_new_map()

        self.screen.update()

    def random_grid(self):
        '''Game.random_grid() -> None
        loads a random grid'''
        if self.isPlaying:
            self.toggle_pause()
        self.update_grid(self.compile_random_map())

    def save_grid(self):
        '''Game.save_grid() -> None
        saves to grid to a file'''
        string = ''
        for cell in self.cellDic:
            if self.cellDic[cell]:
                string += str(cell[0])+","+str(cell[1])+"\n"

        fileName = fileopen.asksaveasfilename(defaultextension=".txt",filetypes=([("Text file",".txt")]))
        if fileName == '':
            return
        
        file = open(fileName, "w")
        file.write(string)
        file.close()

    def reset(self):
        '''Game.reset() -> None
        resets the game to the last starting position'''
        if self.isPlaying:
            self.toggle_pause()
        self.update_grid(self.lastStart)
                    
root = Tk()
root.title("Conway's Game of Life")
GameFrame(root)
mainloop()
quit()

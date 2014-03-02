import pygtk
import gtk
import sys
import random

if sys.platform=="win32":
    gtk.settings_get_default().set_long_property("gtk-button-images", True, "main") 

GAME_SIZE = 10              # size of game in buttons (i.e. 10x10)
CELL_SIZE = 20              # how big each buttons should be (in pixels)
IMG_FLAG = 'flag.jpg'       # image to display for flags
IMG_BOMB = 'bomb.jpg'       # image to display for bombs
NUM_BOMBS = 10              # how many bombs should be on the screen
BOMB = 'bomb'

class MinesweeperGUI():
    def __init__(self):
        self.createWindow()
        self.createMenu()
        self.logic = MinesweeperLogic(GAME_SIZE)
        self.createGame()
        self.placeImagesAndLabels()
        self.main_win.show_all()
        
    def createWindow(self):
        self.main_win = gtk.Window()
        self.main_win.set_title('Minesweep')
        self.main_win.set_resizable(False)
        self.main_win.set_size_request(CELL_SIZE * GAME_SIZE, CELL_SIZE * GAME_SIZE + 24) #Adding 24px to the height to account for menubar
        self.main_vbox = gtk.VBox(False, 3)
        self.main_win.add(self.main_vbox)
        self.main_win.connect('destroy', self.destroy_handler)
        self.main_win.connect('delete_event', self.delete_handler)

    def createMenu(self):
        self.menu_bar = gtk.MenuBar()
        self.menu = gtk.Menu()
        self.root_menu = gtk.MenuItem('Game')
        self.root_menu.set_submenu(self.menu)
        self.menu.append(self.createMenuItem('New Game', self.restart_handler))
        self.menu.append(self.createMenuItem('Solve', self.solve_handler))
        self.menu.append(self.createMenuItem('Quit', self.destroy_handler))
        self.menu_bar.append(self.root_menu)
        self.main_vbox.pack_start(self.menu_bar, False, False, 0)

    def createMenuItem(self, title, handler):
        menuitem = gtk.MenuItem(title)
        menuitem.connect('activate', handler)
        return menuitem

    def getSmallImage(self, filename):
        image = gtk.Image()
        if filename == IMG_FLAG:
            image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename).scale_simple(CELL_SIZE - 10,CELL_SIZE - 10,gtk.gdk.INTERP_BILINEAR))
        else:
            image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename).scale_simple(CELL_SIZE,CELL_SIZE,gtk.gdk.INTERP_BILINEAR))
        return image

    def createGame(self):
        self.table = myTable(GAME_SIZE, GAME_SIZE)
        for y in range(GAME_SIZE):
            for x in range(GAME_SIZE):
                b = gtk.Button('')
                b.set_size_request(CELL_SIZE, CELL_SIZE)
                b.connect('button_press_event', self.clicked_handler)
                self.table.attachButton(b, x, y)
        self.main_vbox.pack_start(self.table, False, False, 0)

    def clearFlagsAndHideButtons(self):
        for b,index in self.table.cells:
            b.hide()
            i = b.get_image()
            if i is not None:
                i.set_visible(False) 

    def toggleFlag(self, widget):
        i = widget.get_image()
        if i is None:
            widget.set_image(self.getSmallImage(IMG_FLAG))
        elif i is not None and i.get_visible():
            i.hide()
        elif i is not None and i.get_visible() == False:
            i.show()

    def updateDisplay(self):
        locations = self.logic.getBombLocations()
        for row in range(GAME_SIZE):
            for col in range(GAME_SIZE):
                if locations[row][col].getVisible() == True:
                    for b,index in self.table.cells:
                        if index == row * GAME_SIZE + col:
                            b.hide()

    def placeImagesAndLabels(self):
        locations = self.logic.getBombLocations()
        for row in range(GAME_SIZE):
            for col in range(GAME_SIZE):
                if locations[row][col].getContents() == BOMB:
                    image = self.getSmallImage(IMG_BOMB)
                    self.table.attachImage(image, row, col)
                elif locations[row][col].getContents() > 0:
                    label = gtk.Label()
                    label.set_text(str(locations[row][col].getContents()))
                    self.table.attachLabel(label, row, col)

    def processCells(self, button):
        row,col = self.table.getRowColOfButton(button)
        locations = self.logic.getBombLocations()
        if locations[row][col].getContents() == BOMB:
            self.clearFlagsAndHideButtons()
            print 'You landed on a bomb, Game over!'
        else:
            self.logic.checkCell(row,col)

    def run(self):
        gtk.main()

    #Handlers section
    def delete_handler(self, widget, event, data=None):
        return False
    def destroy_handler(self, widget, data=None):
        gtk.main_quit()
    def restart_handler(self, widget, data=None):
        self.logic.reset()
        self.table.clearImages()
        self.table.clearLabels()
        self.clearFlagsAndHideButtons()
        self.placeImagesAndLabels()
        self.updateDisplay()
        self.main_win.show_all()
    def solve_handler(self, widget, data=None):
        self.clearFlagsAndHideButtons()
    def clicked_handler(self, widget, event, data=None):
        if event.button == 1:
            #print('Left clicked')
            self.processCells(widget)
            self.updateDisplay()
        elif event.button == 3:
            #print('Right clicked')
            self.toggleFlag(widget)
    #End handlers section

class myTable(gtk.Table):
    def __init__(self, xsize, ysize):
        gtk.Table.__init__(self, xsize, ysize, True)
        numcells = xsize * ysize
        self.xsize = xsize
        self.ysize = ysize
        self.cells = []
        self.images = []
        self.labels = []
    def attachButton(self, button, row, column):
        index = row * GAME_SIZE + column
        self.cells.append((button, index))
        self.attach(button, row, row+1, column, column+1)
    def getRowColOfButton(self, button):
        self.row = 0
        self.col = 0
        while True:
            for (b, index) in self.cells:
                if b == button:
                    self.row = index / GAME_SIZE
                    self.col = index % GAME_SIZE
                    #print (self.row, self.col)
                    return (self.row, self.col)
            break
    def attachImage(self, image, row, column):
        self.images.append(image)
        self.attach(self.images[-1], row, row+1, column, column+1)
    def attachLabel(self, label, row, column):
        self.labels.append(label)
        self.attach(self.labels[-1], row, row+1, column, column+1)
    def clearImages(self):
        for img in self.images:
            self.remove(img)
    def clearLabels(self):
        for lbl in self.labels:
            self.remove(lbl)


class Cell():
    def __init__(self):
        self.contents = ''
        self.visibility = False
    def setVisible(self):
        self.visibility = True
    def getVisible(self):
        return self.visibility
    def getContents(self):
        return self.contents
    def setContents(self, contents):
        self.contents = contents

class MinesweeperLogic():
    def __init__(self, size):
        self.size = size
        self.reset()
    def reset(self):
        self.bomb_locations = []
        for row in range(self.size):
            r = []
            for col in range(self.size):
                c = Cell()
                r.append(c)
            self.bomb_locations.append(r)
        self.setBombLocations()
        self.setBombCounters()
    def getBombLocations(self):
        return self.bomb_locations
    def setBombLocations(self):
        #for i in range(NUM_BOMBS):
        #    while True:
        #        row = random.randrange(0, GAME_SIZE)
        #        col = random.randrange(0, GAME_SIZE)
        #        if self.bomb_locations[row][col].getContents() != BOMB:
        #            self.bomb_locations[row][col].setContents(BOMB)
        #            break
        for i in range(NUM_BOMBS):
            row = random.randrange(0, GAME_SIZE)
            col = random.randrange(0, GAME_SIZE)
            self.bomb_locations[row][col].setContents(BOMB)

    def setBombCounters(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.bomb_locations[row][col].getContents() != BOMB:
                    self.bomb_locations[row][col].setContents(self.setBombCountNumbers(row,col))
    def setBombCountNumbers(self, row, col):
        count = 0
        #can I check north?
        if row > 0:
            count += self.isBomb(row-1, col)
        #can I check south?
        if row < GAME_SIZE-2:
            count += self.isBomb(row+1, col)
        #can I check west?
        if col > 0:
            count += self.isBomb(row, col-1)
        #can I check east?
        if col < GAME_SIZE-2:
            count += self.isBomb(row, col+1)
        #can I check northwest?
        if row > 0 and col > 0:
            count += self.isBomb(row-1, col-1)
        #can I check southwest?
        if row < GAME_SIZE-2 and col > 0:
            count += self.isBomb(row+1, col-1)
        #can I check northeast?
        if row > 0 and col < GAME_SIZE-2:
            count += self.isBomb(row-1, col+1)
        #can I check southeast?
        if row < GAME_SIZE-2 and col < GAME_SIZE-2:
            count += self.isBomb(row+1, col+1)
        return count
    def isBomb(self, row, col):
        if row < 0 or row > GAME_SIZE-1 or col < 0 or col > GAME_SIZE-1:
            return 0
        if self.bomb_locations[row][col].getContents() == BOMB:
            return 1
        else:
            return 0
    def checkCell(self, row, col):
        #outside bounds
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return
        if self.bomb_locations[row][col].getVisible()==True:
            return
        cell_contents = self.bomb_locations[row][col].getContents()
        #if it is a number, unhide that cell
        if cell_contents > 0 and cell_contents != BOMB:
            self.bomb_locations[row][col].setVisible()
        elif cell_contents == BOMB:
            return
        else:
            self.bomb_locations[row][col].setVisible()
            #call `checkCell` on the cell to the right
            self.checkCell(row,col+1)
            #call `checkCell` on the cell to the left
            self.checkCell(row,col-1)
            #call `checkCell` on the cell above
            self.checkCell(row-1,col)
            #call `checkCell` on the cell below
            self.checkCell(row+1,col)

m = MinesweeperGUI()
m.run()
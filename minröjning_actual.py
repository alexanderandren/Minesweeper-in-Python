"""
Titel: Minröjning
Uppgift nr: 168
Författare: Alexander Andrén
Datum: 2019-03-15
Kurs: DD100N

Programmet är ett spel med Microsofts "Minesweeper" som förebild.
Det skapar en spelplan av rutor, och gömmer "minor" under vissa av dem.
För att vinna spelet måste spelaren klicka på alla rutor som ej har
någon mina. Som ledtråd får spelaren veta hur många minor det ligger
intill en rutan hen har klickat på.
"""

from random import randint
from tkinter import *
from time import *
from tkinter import messagebox

######################################
########                      ########
########  Square & Minefield  ########
########                      ########        
######################################

class Square:
    """ Beskriver en ruta på minfältet. Metoder: ändra attribut eller beskriva innehållet. 
    mine (bool), om rutan är mina eller inte. 
    adjacent (int), antal minor rutan gränsar till 0-8.
    flagged (bool), om rutan är flaggad eller inte. 
    visible (bool), om rutan är synlig eller inte. """
    def __init__(self):
        """ Skapar en ny ruta utan tilldelade värden. 
        Inparametrar: self.
        Returvärde: None. """
        self.mine = False
        self.adjacent = 0
        self.flagged = False
        self.visible = False

    def __repr__(self):
        """ Returnerar symbol som beskriver rutans innehåll. 
        Inparametrar: self.
        Returvärde: Char som beskriver rutan 'F'/'M'/' '/'1-8'/. """
        if self.visible:
            if self.mine:
                return "M"
            elif self.adjacent == 0:
                return " "
            else:                
                return str(self.adjacent)
        elif self.flagged:
            return "F"
        else:
            return " "

    def flag(self):
        """ Om rutan inte är synlig, ändrar attributet flagged.
        Inparametrar: self.
        Returvärde: None. """
        if not self.visible:
            self.flagged = not self.flagged

    def stepOn(self):
        """ 'Kliver på rutan'. Tar bort flaggor, gör ev rutan synlig, kollar om spelaren sprängs (mina). 
        Om rutan är tom returnerar isEmpty == True, som grund för anrop att visa intilliggande.
        OBS: tom ruta görs synlig av den andra funktionen (ej här). 
        Inparametrar: self.
        Returvärde: isAlive, isEmpty (bool)."""
        # OBS: self.visible kan ej sättas för samtliga rutor direkt.
        # Attributet används som kriterie för att hitta ett slut för
        # den rekursiva funktionen App.revealEmpty(self, row, col). 
        isEmpty = False
        isAlive = True
        self.flagged = False
        if self.adjacent == 0:
            isEmpty = True
        elif self.mine:
            self.visible = True
            isAlive = False
        else:
            self.visible = True
        return isAlive, isEmpty

class MineField:
    """ Beskriver en spelplan, metoder för att skapa ny spelplan.
    Attribut: field (matris); nrOfRows, nrOfCols (int);
    minesFactor (float för att beräkna antal minor); nrOfMines (int)
    """
    def __init__(self, rows, cols, diffPercent):
        """ Skapar ett nytt MineField-objekt.
        Inparametrar: self.
                      rows, cols, diffPercent (int).
        Returvärde: None. """
        self.field = None
        self.nrOfRows = rows
        self.nrOfCols = cols
        self.minesFactor = float(diffPercent / 100)
        self.nrOfMines = int(rows * cols * self.minesFactor)

    def newField(self):
        """ Skapar spelplanen via anrop till egna metoder, sparar till self.field.
        Inparametrar: self.
        Returvärde: field (matris). """
        self.field = self.createFieldMatrix(self.nrOfRows, self.nrOfCols)
        self.placeMines() 

    def createFieldMatrix(self, rows, cols):
        """ Skapar en matris (currentField) av tuples med objekt av klass Square.
        Inparametrar: self. rows, cols (int). 
        Returvärde: currentField (matris av tuples). """
        currentField = []
        for row in range(rows):
            currentRow = []
            for col in range(cols):
                currentRow.append(Square())
            currentField.append(tuple(currentRow))
        return tuple(currentField)

    def placeMines(self):
        """ Placerar ut minorna i matrisen field.
        Anropar self.addAdjacent för att räkna ut antal intilliggande minor.
        Inparametrar: self.
        Returvärde: None. """
        i = self.nrOfMines
        while i > 0:
            row = randint(0, self.nrOfRows - 1)
            col = randint(0, self.nrOfCols - 1)
            if self.field[row][col].mine == False:
                self.field[row][col].mine = True
                self.addAdjacent(row, col)
                i -= 1

    def addAdjacent(self, row, col):
        """ Lägger till +1 till self.adjacent på samtliga rutor runt en mina.
        Inparametrar: self, row & col, x/y koordinaterna för minan.
        Returvärde: None. """
        for i in range(-1, 2):
            for j in range(-1, 2):
                if -1 < (row + i) < self.nrOfRows and -1 < (col + j) < self.nrOfCols: 
                    self.field[row + i][col + j].adjacent += 1

    def checkGameWon(self): 
        """ Kontrollerar om spelet är vunnet.
        Inparmetrar: self.
        Returvärde: True om spelet är vunnet, annars False. """
        # Metod 1: Flaggor.
        goodFlag, badFlag = self.checkFlags()          
        if badFlag < 1 and goodFlag == self.nrOfMines:
            return True
        # Metod 2: Spelplanen röjd. 
        for row in self.field:
            for square in row:
                if not square.mine and not square.visible:
                    return False
        return True

    def checkFlags(self): 
        """ Kontrollerar antalet korrekt och inkorrekt placerade flaggor.
        Inparametrar: self.
        Returvärde: goodFlag & badFlag (integers). """
        goodFlag = 0
        badFlag = 0
        for row in self.field:
            for square in row:
                if square.flagged:
                    if square.mine:
                        goodFlag += 1
                    else:
                        badFlag +=1
        return goodFlag, badFlag
              
######################################
########                      ########
########         Timer        ########
########                      ########        
######################################

class Timer:
    """ Beskriver en timer. Attribut: starttid, stoptid, totaltid.
        Metoder: read(), start(), stop(). """
    def __init__(self):
        """ Skapar ett nollställt Timer-objekt.
        Inparametrar: self.
        Returvärde: None. """
        self.startTime = 0.0
        self.endTime = 0.0
        self.totalTime = 0.0

    def read(self):
        """ Läser av totaltiden.
        Inparametrar: self.
        Returvärde: self.totalTime. """
        return self.totalTime

    def start(self):
        """ Startar timern.
        Inparametrar: self.
        Returvärde: None. """
        self.startTime = time()

    def stop(self):
        """ Stoppar timern samt räknar ut totaltiden.
        Inparametrar: self.
        Returvärde: None. """
        self.endTime = time()
        self.totalTime = self.endTime - self.startTime

######################################
########                      ########
########  Scoreboard & Score  ########
########                      ########        
######################################

class Scoreboard():
    """ Beskriver en topplista. Metoder: läsa/spara till fil, skapa topplista,
    jämföra nytt resultat, lägga in nytt resultat.
    Attribut: filename, highscore (lista med Score-objekt), new (Score-objekt att jämföra)."""
    def __init__(self, filename):
        """ Skapar en ny topplista via anrop till self.readHighscore(filename).
        Listan består av objekt av Score-klass.
        Skapar self.new för att spara info om senaste resultat. 
        Inparametrar: self. filename (string)
        Returvärde: None. """
        self.filename = filename
        self.highscore = self.readHighscore(filename)
        self.new = None
    
    def readHighscore(self, filename):
        """ Skapar Score-objekt i en lista baserat på textfil, returnerar listan. 
        Inparametrar: filename (str).
        Returvärde: standings (lista Square-objekt). """
        standings = []
        try:
            file = open(filename,"r")
            name = file.readline().strip()
            while name:
                try:
                    score = int(file.readline().strip())
                    time = float(file.readline().strip())
                    result = Score(name, score, time)
                    standings.append(result)
                    name = file.readline().strip()
                except ValueError:
                    messagebox.showwarning("Fel vid inläsning", "Något blev fel vid inläsning av " + filename + ".\nInnehållet kommer skrivas över vid vinst.")
                    standings = []
                    break
            file.close()
            standings.sort()
        except FileNotFoundError:
            messagebox.showwarning("Topplistan saknas", "Kan ej hitta " + filename + ".\nEn ny fil kommer skapas vid vinst.")
        return standings

    def saveHighscore(self, filename): 
        """ Sparar tio-i-topp listan i en fil. 
        Inparametrar: self, filename (str).
        Returvärde: None. """ 
        file = open(filename,"w")
        for score in self.highscore:
          file.write(score.name + "\n")
          file.write(str(score.score) + "\n")
          file.write(str(score.time) + "\n")
        file.close()

    def madeHighscore(self, score, time):
        """ Metoden kontrollerar om ett nytt resultat ska in i topplistan.
        Inparametrar: self, points (int), time (float).
        Returvärde: True om in på topplistan, False annars. """
        self.new = Score("NoName", score, time)
        if len(self.highscore) < 10:
            return True
        elif self.new < self.highscore[-1]:
            return True
        else:
            return False  
        
    def newHighscore(self, name):
        """ Lägger till nytt resultat baserat på tidigare sparad input i self.new
        samt name. Sorterar därefter listan och sparar. 
        Inparametrar: self. name (str).
        Returvärde: None. """
        name = name.strip()
        # Om rutan är tom sparas ingenting till topplistan. 
        if len(name) == 0:
            return
        # Om topplistan är full (10 inlägg) tas det sämsta resultatet bort.
        if len(self.highscore) == 10:
            del self.highscore[-1]
        # Om namnet är längre än 10 bokstäver tas allt efter bokstav 10 bort.
        name = name[:10]    
        self.new.name = name
        self.highscore.append(self.new)
        self.highscore.sort()
        self.saveHighscore(self.filename)

    def getBoard(self):
        """ Returnerar topplistan som en sträng.
        Inparametrar: self.
        Returvärde: results (str)."""
        results = "\t\tTopp tio\n   Namn      :  Poäng  :    Sek  \n\n"
        for i in self.highscore:
            results += ('   ' + str(i) + '\n')
        return results

class Score:
    """ Beskriver ett resultat. Metoder: __init__, __repr__, __gt__.
    Attribut: name (str), score (int), time (float). """
    def __init__(self, name, score, time):
        """ Skapar ett nytt resultat med namn, poäng, tid.
        Inparametrar: self. name (str), score (int), time (float).
        Returvärde: None. """
        self.name = name
        self.score = int(score)
        self.time = float(time)

    def __repr__(self):
        """ Returnerar en resultatsträng, 'namn : poäng tid'."""
        return str(f"{self.name:10}") + ':' + str(f"{self.score:-6}") + '   :' + str(f"{self.time:-8.2f}")

    def __gt__(self, other):
        """ Jämför två Score-objekt. Bäst resultat och tid sorteras först. """
        if self.score < other.score:
            return True
        elif self.score == other.score:
            if other.time < self.time:
                return True
            else:
                return False
        else:
            return False

######################################
########                      ########
########          App         ########
########                      ########        
######################################

class App(Tk):
    """ Beskriver det grafiska gränssnittet. Metoder: för grafik och spelgång. 
        Attribut: timer (Timer()); mineField (MineField(), skapas vid anrop till self.startNewGame());
        scoreBoard (ScoreBoard()); diffPercent, rows, cols, buttonSize(IntVar() för inställningar via GUI);
        name (StringVar()); fieldFrame (Frame-widget som håller spelplanen,
        skapas vid anrop till self.newGame())."""
    def __init__(self, filename):
        """ Konstruktormedtoden skapar nytt spelfönster och attribut genom anrop till egna metoder.
        Inparametrar: self. filename (str), filen där highscore sparas. 
        Returvärde: None. """
        super().__init__()
        self.title("Osquar & Trofast Minröjning AB")
        self.config(bg = "black")
        self.setDefaultAttributes()
        self.scoreBoard = Scoreboard(filename)
        self.timer = Timer()
        self.createLayout()   
        
    def setDefaultAttributes(self):
        """ Skapar de attribut som håller objektvariabler.
        Inparametrar: self.
        Returvärde: None."""
        self.diffPercent, self.rows, self.cols, self.buttonSize = IntVar(), IntVar(), IntVar(), IntVar()
        self.diffPercent.set(12)
        self.rows.set(9)
        self.cols.set(9)
        self.buttonSize.set(14)
        self.name = StringVar()
        self.name.set("Osquar")

    def createLayout(self):
        """ Skapar huvudsaklig layout för programmet.
        Två Frames (menuFrame & self.fieldFrame) samt menu via anrop till self.createMenu().
        Inparametrar: self.
        Returvärde: None. """
        menuFrame = Frame(self, bg = "black", padx = 13, pady = 13)
        menuFrame.pack()
        self.createMenu(menuFrame)
        # self.fieldFrame skapas här endast för att ha något att förstöra
        # första gången self.newField() anropas. 
        self.fieldFrame = Frame(self)

    def createMenu(self, menuFrame):
        """ Skapar knappar och inställningar i self.menuFrame, motsvarande en menu.
        Inparametrar: self. menuFrame (Frame-widget som håller menyknapparna). 
        Returvärde: None. """
        fontAll = ('Courier', 11, 'bold')
        Button(menuFrame, text = "Nytt Spel", font = fontAll, height = 1, width = 13, bg = "gold", command = self.startNewGame).grid(row = 1, column = 1)
        Button(menuFrame, text = "Tio-I-Topp", font = fontAll, height = 1, width = 13, bg = "gold", command = self.showTopTen).grid(row = 2, column = 1)
        Button(menuFrame, text = "Instruktioner", font = fontAll, height = 1, width = 13, bg = "gold", command = self.showInstructions).grid(row = 1, column = 2)
        Button(menuFrame, text = "Inställningar", font = fontAll, height = 1, width = 13, bg = "gold", command = self.showSettings).grid(row = 2, column = 2)
        # Raden nedanför kan avmarkeras för att skapa möjlighet att testa vinst-beroende funktioner. 
        # Button(menuFrame, text = "Vinn nu!", font = fontAll, height = 1, width = 13, bg = "red", command = lambda alive = True: self.gameOver(alive)).grid(row = 3, column = 1)

    def showSettings(self):
        """ Skapar en ny ruta med inställningar för spelet.
        Inparametrar: self.
        Returvärde: None. """
        fontAll = ('Courier', 11, 'bold')
        settings = Toplevel(self, bg = "black")
        settings.title("Inställningar")
        setFrame = Frame(settings, bg = "black", padx = 13, pady = 13)
        setFrame.pack()
        Label(setFrame, text = "Rader", fg = "gold", bg = "black", font = fontAll, anchor = S, height = 1, width = 12).grid(row = 1, column = 2)
        Label(setFrame, text = "Kolumner", fg = "gold", bg = "black", font = fontAll, anchor = S, height = 1, width = 12).grid(row = 2, column = 2)
        Label(setFrame, text = "Minor %", fg = "gold", bg = "black", font = fontAll, anchor = S, height = 1, width = 12).grid(row = 3, column = 2)
        Label(setFrame, text = "Textstorlek", fg = "gold", bg = "black", font = fontAll, anchor = S, height = 1, width = 12).grid(row = 4, column = 2)
        Scale(setFrame, from_ = 9, to = 16, fg = "gold", bg = "black", borderwidth = 0, font = fontAll, orient = HORIZONTAL, variable = self.rows).grid(row = 1, column = 3)
        Scale(setFrame, from_ = 9, to = 30, fg = "gold", bg = "black", borderwidth = 0, font = fontAll, orient = HORIZONTAL, variable = self.cols).grid(row = 2, column = 3)
        Scale(setFrame, from_ = 12, to = 20, fg = "gold", bg = "black", borderwidth = 0, font = fontAll, orient = HORIZONTAL, variable = self.diffPercent).grid(row = 3, column = 3)
        Scale(setFrame, from_ = 8, to = 14, fg = "gold", bg = "black", borderwidth = 0, font = fontAll, orient = HORIZONTAL, variable = self.buttonSize).grid(row = 4, column = 3)
        # En knapp som stänger fönstret, och en labelframe som skapar avstånd nedåt. 
        Button(settings, text = "OK", font = fontAll, height = 1, width = 10, command = settings.destroy, bg = "gold").pack()
        LabelFrame(settings, height = 13, width = 13, borderwidth = 0, bg = "black").pack()
         
    def startNewGame(self):
        """ Skapar ett nytt Minefieldobjekt samt anropar self.drawField()
        och self.timer.start(). Värden för mineField hämtas från sliderna i GUIn. 
        Inparametrar: self.
        Returvärde: None. """
        rows, cols, diffPercent = self.rows.get(), self.cols.get(), self.diffPercent.get()
        self.mineField = MineField(rows, cols, diffPercent)
        self.mineField.newField()
        self.drawField()
        self.timer.start()

    def showInstructions(self):
        """ Skapar en ny ruta med instruktionerna för spelet.
        Inparametrar: self.
        Returvärde: None. """
        instructions = Toplevel(self)
        instructions.title("Minröjning 101")
        txt = Text(instructions, width = 57, font = ('Courier', 12, 'bold'), bg = 'black', fg = 'gold')
        txt.pack()
        txt.insert(INSERT, """\t*********** INSTRUKTIONER ***********

\tVinn:
- Genom att göra alla rutor utan mina synliga, eller...
- genom att 'flagga' alla rutor med minor.

\tVänsterklick:
- Undersöker en ruta.
- M = Mina, och spelet är förlorat.
- 1-8 = Antal minor som angränsar till den rutan.
- Tom = Inga minor finns intill. Alla intilliggande
  rutor utan mina visas också. 

\tHögerklick:
- Flaggar en ruta som misstänkt mina.
- Kom ihåg, om alla minor är flaggade, är det samma
  sak som att alla minor är röjda. Det är dock bara
  minorna som får ha flaggor för att vinna så. 

\tVälj spelplan:
- Öppna inställningarna via huvudfönstret för att
  välja storlek och svårighetsgrad.""")

    def showTopTen(self):
        """ Skapar en ny ruta aktuell toplista som hämtas från self.scoreBoard.getBoard().
        Inparametrar: self.
        Returvärde: None. """
        topten = Toplevel(self)
        topten.title("Sjukt bra minröjare")
        txt = Text(topten, width = 36, height = 14, font = ('Courier', 12, 'bold'), bg = 'black', fg = 'gold')
        txt.pack()
        txt.insert(INSERT, self.scoreBoard.getBoard())

    def drawField(self):
        """ Skapar knappar för samtliga 'Square'-objekt i minefield.
        Inparametrar: self.
        Returvärde: None. """
        self.createNewField()
        y = 1
        for row in self.mineField.field:
            x = 1
            for square in row:
                btn = Button(self.fieldFrame, text = square, font = ('Arial', self.buttonSize.get(), 'bold'), bg = 'green', width = 2, command = lambda row = y, col = x: self.play(row, col, False))
                btn.bind("<Button-3>", lambda e, row = y, col = x : self.play(row, col, True))
                btn.grid(row = y, column = x)
                x += 1
            y += 1
        # self.fieldFrame.pack()

    def createNewField(self):
        """ Förstör self.fieldFrame och skapar ny.
        Inparametrar: self.
        Returvärde: None."""
        self.fieldFrame.destroy()
        self.fieldFrame = Frame(self)
        self.fieldFrame.pack()

    def play(self, row, col, flag): 
        """ 'Spelmotorn' - anropas när en ruta klickas på. Hämtar aktuell ruta och knapp
        från self.getSquareButton(row, col) och utvärderar om spelet är vunnet/förlorat eller
        rutan ska flaggas. Om spelet är slut, anropar self.gameOver(alive), annars fortsätter spelet. 
        Inparametrar: self. row, col (int). flag (bool).
        Returvärde: None. """
        square, button = self.getSquareButton(row, col)
        alive = True
        if flag:
            self.placeFlag(square, button)
        else:
            alive = self.clickOn(square, button, row, col)
        if not alive or self.mineField.checkGameWon():
            self.timer.stop()
            self.gameOver(alive)

    def clickOn(self, square, button, row, col):
        """ Funktionen anropas när en ruta vänsterklickas på. Öppnar rutan. 
        Inparametrar: self. square - Square-objektet. button - Button-objektet.
                      row, col - int koordinater för rutan som klickats på.
        Returvärde: alive - boolean. """
        alive, empty = square.stepOn()
        if empty:
            self.revealEmpty(row, col)
        button.config(text = square, relief = SUNKEN, bg = "saddlebrown")
        return alive

    def placeFlag(self, square, button):
        """ Flaggar rutan som högerklickatsklickats på. 
        Inparametrar: self. square - Square-objektet. button - Button-objektet.
        Returvärde: None. """
        if not square.visible:
            square.flag()
            button.config(text = square)
                                                              
    def getSquareButton(self, row, col):
        """ Hämtar Square-objektet ur minfältet, och Button-objeketet ur listan grid_slaves.
        Inparametrar: self. row, col - int koordinater för vilken ruta som klickats på.
        Returvärde: square - Square-objektet. button - Button-objektet."""
        square = self.mineField.field[row-1][col-1]
        button = self.fieldFrame.grid_slaves(row = row, column = col)[0]
        return square, button
        
    def revealEmpty(self, row, col):
        """ Rekursiv funktion som visar alla rutor kring tomma rutor. 
        Inparametrar: self. row - int. col - int.
        Returvärde: None. """
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 < (row + i) < self.mineField.nrOfRows + 1 and 0 < (col + j) < self.mineField.nrOfCols + 1:
                    square, button = self.getSquareButton(row + i, col + j)
                    alive, empty = square.stepOn()
                    button.config(text = square, relief = SUNKEN, bg = "saddlebrown")
                    if empty and not square.visible:
                        # square.visible används som stop för den rekursiva funktionen.
                        # Därför görs aktuell square.visible = True först här. 
                        square.visible = True
                        self.revealEmpty((row + i), (col + j))

    def showField(self):
        """ Visar hela spelplanen. 
        Inparametrar: self.
        Returvärde: None. """
        for row in range(0, self.mineField.nrOfRows):
            for col in range(0, self.mineField.nrOfCols):
                square, button = self.getSquareButton(row + 1, col + 1)
                square.visible = True
                button.config(text = square, relief = SUNKEN, command = self.doNothing, bg = "saddlebrown")

    def doNothing(self):
        """ En funktion som inte gör någonting. Används för att göra
        knapparna på spelplanen funktionslösa när spelet är slut. """
        pass

    def gameOver(self, alive):
        """ Anropar funktion för att visa planen, räknar ut poäng samt anropar
        funktioner för att spara till topplistan och visa resultat. 
        Inparametrar: self, alive - True/False. 
        Returvärde: None. """
        self.showField()
        if alive:
            time = self.timer.read()
            # Poängen ges av 'spelplanens storlek' subtraherat med 'tiden i sekunder'.
            # Det multipliceras med 'procent minor' faktor '10'.
            # Alla värden sparas i och hämtas från aktuellt mineField, då värdena från sliders
            # kan ändras när spelet börjat. 
            points = int((self.mineField.nrOfCols * self.mineField.nrOfRows - time) * self.mineField.minesFactor * 10) 
            if points < 0:
                points = 0
            if self.scoreBoard.madeHighscore(points, time):
                self.showVictory(points, time, True)
                self.getPlayerName()
                # Här väntar koden på att popup-fönstret stängs.
                self.scoreBoard.newHighscore(self.name.get())
            else:
                self.showVictory(points, time, False)      
        else:
            self.showDefeat()
            
    def showVictory(self, points, time, placed):
        """ Visar resultat vid vinst.
        Inparametrar: self. points (int). time (float).
                      placed (bool), True om in på topplistan. 
        Returvärde: None. """
        if placed:
            msg = "\n\nDu är bland världens tio bästa minröjare!"
        else:
            msg = "\n\nTyvärr räcker det inte för placering..."
        messagebox.showinfo("Bra jobbat!", "Du fick " + str(points) + " poäng med tiden " + str(f"{time:.2f}") + " sekunder" + msg)     

    def showDefeat(self):
        """ Visar resultat vid förlust.
        Inparametrar: self.
        Returvärde: None."""
        goodFlag, badFlag = self.mineField.checkFlags()
        messagebox.showerror("Ouch...", "Ajdå, det där såg ut att göra ont.\n\n" +
                            "Du flaggade " + str(goodFlag) + ' av ' + str(self.mineField.nrOfMines) + ' minor, och satte ' + str(badFlag) + ' flaggor fel.')
    
    def getPlayerName(self):
        """ Skapar en ruta att fylla i sitt namn.
        Inparametrar: self.
        Returvärde: None. """
        popup = Toplevel(self, bg = "black", padx = 13, pady = 13)
        popup.title("Chicken Dinner!")
        Label(popup, text = "Vad heter du?", font = ('Courier', 14, 'bold'), bg = "black", fg = "gold").pack()
        nameBox = Entry(popup, textvariable = self.name, bg = "black", fg = "gold", font = ('Courier', 14, 'bold'), width = 10)
        nameBox.pack()
        LabelFrame(popup, height = 7, bg = "black", borderwidth = 0).pack()
        Button(popup, text = "WINNER", font = ('Courier', 12, 'bold'), command = popup.destroy, bg = "gold").pack()
        # .grab_set() gör popup modalt. 
        popup.grab_set()
        self.wait_window(popup)
                           
######################################
########                      ########
########         Main         ########
########                      ########        
######################################

def main(filename):
    """ Huvudprogrammet. Skapar instans av App(), startar mainloop().
    Inparametrar: filename (str) - .txt fil.
    Returvärde: None. """
    app = App(filename)
    app.mainloop()

FILENAME = "highscore.txt"
main(FILENAME)

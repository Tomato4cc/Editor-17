# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import shutil
from struct import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ui.uio import Ui_Editor
from ui.playero import Ui_Player

class PlayerItem(QListWidgetItem):
    def __init__(self, player=None):
        super().__init__()
        self.player = player
        
class PlayerTableItem(QTableWidgetItem):
    def __init__(self, player=None):
        super().__init__()
        self.player = player
        
class TeamTableItem(QTableWidgetItem):
    def __init__(self, team=None):
        super().__init__()
        self.team = team

class Player(QMainWindow, Ui_Player):
    def __init__(self, parent, player, origin, item, item2):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('img/icon.png'))
        self.player = player
        self.parent = parent
        self.origin = origin
        self.item = item
        self.item2 = item2
        self.skill = 0
        self.com = 0
        
        self._STATS = [self.pattprow, self.pdefprow, self.pgoalkeeping, self.pdribbling, self.pfinishing, self.plowpass, self.ploftedpass, self.pheader, self.pswerve, self.pcatching, self.pclearing, self.preflexes, self.pbodycontrol, self.pphyscont, self.pkickpower, self.pexplopower, self.pballcontrol, self.pballwinning, self.pjump, self.pcoverage, self.pplacekicking, self.pstamina, self.pspeed]
        self._PLAYABLES = {0:self.poscf, 1:self.posss, 2:self.poslwf, 3:self.posrwf, 4:self.posamf, 5:self.posdmf, 6:self.poscmf, 7:self.poslmf, 8:self.posrmf, 9:self.poscb, 10:self.poslb, 11:self.posrb, 12:self.posgk}
        self._COMSTYLES = [self.ptrickster, self.pmazingrun, self.pspeedbullet, self.pincisiverun, self.plongball, self.pearlycross, self.plongranger]
        self._SKILLS = [self.pscissors, self.pflipflap, self.pmarseille, self.psombrero, self.pcutbehind, self.pscotch, self.pheading, self.plrd, self.pknuckle, self.pacrofinish, self.pheeltrick, self.pfts, self.potp, self.pweightedpass, self.ppinpointcross, self.pcurler, self.prabona, self.plowloftpass, self.plowpunt, self.plongthrow, self.pgklongthrow, self.pmalicia, self.pmanmark, self.ptrackback, self.pacroclear, self.pcaptaincy, self.psupersub, self.pfightspirit]
        
        #Connect signals
        self.pcancel.clicked.connect(self.cancel)
        self.pacancel.clicked.connect(self.cancel)
        self.paccept.clicked.connect(self.save)
        self.paaccept.clicked.connect(self.save)
        self.page.editingFinished.connect(lambda: self.restrict(self.page, 15, 50))
        self.page.textEdited.connect(self.checke)
        self.pheight.editingFinished.connect(lambda: self.restrict(self.pheight, 155, 210))
        self.pheight.textEdited.connect(self.checke)
        self.pweight.editingFinished.connect(lambda: self.restrict(self.pweight, 0, 0))
        self.pweight.textEdited.connect(self.checke)
        self.pboots.textEdited.connect(self.checke)
        self.pgkgloves.textEdited.connect(self.checke)
        self.makegold.clicked.connect(lambda: self.medal(99, Editor.full))
        self.makesilver.clicked.connect(lambda: self.medal(88, Editor.silver))
        self.makebronze.clicked.connect(lambda: self.medal(77, Editor.bronze))
        self.padplus.clicked.connect(lambda: self.adjust(0))
        self.padminus.clicked.connect(lambda: self.adjust(1))
        self.padequ.clicked.connect(lambda: self.adjust(2))
        self.pfpc.clicked.connect(self.fpc)
        self.pnofpc.clicked.connect(self.nofpc)
        self.ppset.clicked.connect(self.phys)
        
        #Disabled for now
        #self.tabWidget.currentChanged.connect(self.tabresize)
        
        #Keyboard shortcuts
        QShortcut(QKeySequence("Shift+Return"), self, self.save)
        QShortcut(QKeySequence("Escape"), self, self.cancel)
        
        for id, button in Ui_Player._PLAYABLES.items():
            button.clicked.connect(self.playable)
            
        for field in Ui_Player._STATS:
            field.editingFinished.connect(self.stat)
            field.textEdited.connect(self.checke)
            
        for box in Ui_Player._SKILLS:
            box.clicked.connect(self.cskill)
        
        for box in Ui_Player._COMSTYLES:
            box.clicked.connect(self.ccom)
        
        #Sloppy way to keep track of amount of player skills
        for i in range(28):
            if(self.player['playerskills'][i]):
                self.skill = self.skill + 1
        
        #Same sloppy way for COM styles
        for i in range(6):
            if(self.player['comstyles'][i]):
                self.com = self.com + 1
    
    #Set all the physique sliders with one button
    def phys(self):
        valid = 0
        str = self.ppsete.text()
        if(len(str) > 1):
            sign = str[0:1]
            rest = str[1:]
            if((sign.isdigit() or sign == "-" or sign == "+") and rest.isdigit()):
                valid = 1
        else:
            if(str.isdigit()):
                valid = 1
    
        if(valid == 1):
            val = int(self.ppsete.text())
            if(val < -7):
                val = -7
            elif(val > 7):
                val = 7
                
            self.pneckl.setValue(val)
            self.pnecks.setValue(val)
            self.pshoulderh.setValue(val)
            self.pshoulderw.setValue(val)
            self.pchestm.setValue(val)
            self.pwaists.setValue(val)
            self.parms.setValue(val)
            self.pthighs.setValue(val)
            self.pcalfs.setValue(val)
            self.plegl.setValue(val)
            self.parml.setValue(val)
            self.pheadw.setValue(val)
            self.pheadl.setValue(val)
            self.pheadd.setValue(val)
  
    #Set FPC settings
    def fpc(self):
        self.pskincol.setCurrentIndex(7)
        self.pboots.setText("38")
        self.pshirttail.setCurrentIndex(0)
        self.psocks.setCurrentIndex(2)
        self.pankletape.setChecked(0)
        self.pglasses.setCurrentIndex(0)
        self.pwristtape.setCurrentIndex(0)
        
        if(self.pregpos.currentIndex() == 0):
            self.pgkgloves.setText("12")
            self.psleeves.setCurrentIndex(1)
        else:
            self.psleeves.setCurrentIndex(2)
            
    def nofpc(self):
        self.pskincol.setCurrentIndex(1)
        self.pboots.setText("0")
        self.pshirttail.setCurrentIndex(1)
        self.psocks.setCurrentIndex(0)
        #self.pankletape.setChecked(0)
        #self.pglasses.setCurrentIndex(0)
        self.pwristtape.setCurrentIndex(0)
        
        if(self.pregpos.currentIndex() == 0):
            self.pgkgloves.setText("0")
            self.psleeves.setCurrentIndex(1)
        else:
            self.psleeves.setCurrentIndex(1)
        
    #Resize window on tab change
    #Currently disabled, it works but I'm not sure if it's a good idea
    #so it's included but not enabled.
    def tabresize(self, index):
        '''if(index == 1):
            self.setMinimumSize(QSize(485, 610))
            self.setMaximumSize(QSize(485, 610))
            self.resize(485, 610)'''
        if(index == 99999):
            self.setMinimumSize(QSize(1110, 870))
            self.setMaximumSize(QSize(1110, 870))
            self.resize(1110, 870)
    
    #Close window on cancel press
    def cancel(self):
        self.close()
    
    #Process COM style checkbox changes
    def ccom(self):
        send = self.sender()
        if(send.isChecked() == 1):
            if(self.com < 4 or (self.com == 4 and send.isChecked() == 0)):
                self.com = self.com + 1
            else:
                self.com = self.com + 1
                for box in self._COMSTYLES:
                    if(box.isChecked() == 0):
                        box.setEnabled(0)
        else:
            self.com = self.com - 1
            if(self.com < 10):
                for box in self._COMSTYLES:
                    box.setEnabled(1)
        self.label_46.setText("COM Styles (" + str(self.com) + "/5)")
    
    #Process skill checkbox changes
    #TODO: cleanup?
    def cskill(self):
        send = self.sender()
        if(send.isChecked() == 1):
            if(self.skill < 9 or (self.skill == 9 and send.isChecked() == 0)):
                self.skill = self.skill + 1
            else:
                self.skill = self.skill + 1
                for box in self._SKILLS:
                    if(box.isChecked() == 0):
                        box.setEnabled(0)
        else:
            self.skill = self.skill - 1
            if(self.skill < 10):
                for box in self._SKILLS:
                    box.setEnabled(1)
        self.label_44.setText("Player Skills (" + str(self.skill) + "/10)")
    
    #Handle stat adjust buttons
    def adjust(self, mode):
        #0 for +, 1 for -, 2 for =
        if(self.padjust.text() != ""): #Make sure there's input
            val = int(self.padjust.text())
            for field in self._STATS:
                if(mode == 0):
                    new = int(field.text()) + val
                elif(mode == 1):
                    new = int(field.text()) - val
                elif(mode == 2):
                    new = val
                    
                if(new < 40):
                    new = 40
                    
                if(new >= 99):
                    new = 99
                    pal = Editor.full
                elif(new >= 90):
                    pal = Editor.gold
                elif(new >= 80):
                    pal = Editor.silver
                elif(new >= 70):
                    pal = Editor.bronze
                else:
                    pal = Editor.nonmed
                    
                field.setText(str(new))
                field.setPalette(pal)
    
    #Handle medal buttons and set the stats/palette in one go
    def medal(self, stat, palette):
        for field in self._STATS:
            field.setText(str(stat))
            field.setPalette(palette)
    
    #Make sure height, weight and age fall in the PES accepted ranges
    def restrict(self, source, mn, mx):
        if(mn == 0):
            mn = max(30, int(self.pheight.text())-129)
        if(mx == 0):
            mx = int(self.pheight.text())-81
        if(int(source.text()) < mn):
            source.setText(str(mn))
        if(int(source.text()) > mx):
            source.setText(str(mx))
            
        if(source == self.pheight):
            h = int(self.pheight.text())
            w = int(self.pweight.text())
            if(w < max(30, h-129)):
                self.pweight.setText(str(max(30, h-129)))
            elif(w > h-81):
                self.pweight.setText(str(h-81))
    
    #Make sure input fields have valid input and are not empty or too small
    def checke(self):
        send = self.sender()
        if(send.text() == ""):
            if(send == self.page):
                send.setText("15")
            elif(send == self.pweight):
                send.setText(str(max(30, int(self.pheight.text())-129)))
            elif(send == self.pheight):
                send.setText("155")
                h = 155
                w = int(self.pweight.text())
                if(w < max(30, h-129)):
                    self.pweight.setText(str(max(30, h-129)))
            elif(send == self.pboots or send == self.pgkgloves):
                send.setText("0")
            else:
                send.setText("40")
    
    #Make sure stats are not too low and set field palettes
    def stat(self):
        send = self.sender()
        val = int(send.text())
        if(val < 40 or send.text() == ""):
            send.setText("40")
            send.setPalette(Editor.nonmed)
        if(val < 70):
            send.setPalette(Editor.nonmed)
        elif(val >= 70 and val < 80):
            send.setPalette(Editor.bronze)
        elif(val >= 80 and val < 90):
            send.setPalette(Editor.silver)
        elif(val >= 90 and val < 99):
            send.setPalette(Editor.gold)
        elif(val == 99):
            send.setPalette(Editor.full)
    
    #Handle playable position buttons
    def playable(self):
        bt = self.sender()
        bid = 0
        for id, button in self._PLAYABLES.items():
            if(button == bt):
                bid = id
        if(self.player['playables'][bid] == 0):
            bt.setStyleSheet("background-color: #FFFF00")
            self.player['playables'][bid] = 1
        elif(self.player['playables'][bid] == 1):
            bt.setStyleSheet("background-color: #FF0000")
            self.player['playables'][bid] = 2
        elif(self.player['playables'][bid] == 2):
            bt.setStyleSheet("")
            self.player['playables'][bid] = 0
    
    #Save the data for current player
    def save(self):
        b = open('out/data.dat', 'r+b')
        
        #First set the in-editor variables
        self.player['pid'] = int(self.pid.text())
        self.player['commid'] = int(self.pcommid.text())
        self.player['nationality'] = self.pnationality.currentData()
        self.player['height'] = int(self.pheight.text())
        self.player['weight'] = int(self.pweight.text())
        self.player['goal1'] = self.pgoalcel1.currentData()
        self.player['goal2'] = self.pgoalcel2.currentData()
        
        self.player['attprow'] = int(self.pattprow.text())
        self.player['defprow'] = int(self.pdefprow.text())
        self.player['goalkeeping'] = int(self.pgoalkeeping.text())
        self.player['dribbling'] = int(self.pdribbling.text())
        self.player['fkmotion'] = self.pfkmot.currentData()
        
        self.player['finishing'] = int(self.pfinishing.text())
        self.player['lowpass'] = int(self.plowpass.text())
        self.player['loftedpass'] = int(self.ploftedpass.text())
        self.player['header'] = int(self.pheader.text())
        self.player['form'] = self.pform.currentData()
        self.player['editedplayer'] = 1 #Reset flag
        
        self.player['swerve'] = int(self.pswerve.text())
        self.player['catching'] = int(self.pcatching.text())
        self.player['clearing'] = int(self.pclearing.text())
        self.player['reflexes'] = int(self.preflexes.text())
        self.player['injuryres'] = self.pinjuryres.currentData()
        self.player['editedbasic'] = 1 #Reset flag
        
        self.player['bodycontrol'] = int(self.pbodycontrol.text())
        self.player['physical'] = int(self.pphyscont.text())
        self.player['kickingpower'] = int(self.pkickpower.text())
        self.player['explosivepower'] = int(self.pexplopower.text())
        self.player['dribblearmmotion'] = self.pdribarm.currentData()
        self.player['editedregpos'] = 1 #Reset flag
        
        self.player['age'] = int(self.page.text())
        self.player['regpos'] = self.pregpos.currentData()
        self.player['playstyle'] = self.pplayingstyle.currentData()
        
        self.player['ballcontrol'] = int(self.pballcontrol.text())
        self.player['ballwinning'] = int(self.pballwinning.text())
        self.player['wfacc'] = self.pwfacc.currentData()
        
        self.player['jump'] = int(self.pjump.text())
        self.player['runarmmotion'] = self.prunarm.currentData()
        self.player['ckmotion'] = self.pckmot.currentData()
        self.player['coverage'] = int(self.pcoverage.text())
        self.player['wfusage'] = self.pwfusage.currentData()
        
        self.player['dhunchmotion'] = self.pdribhunch.currentData()
        self.player['rhunchmotion'] = self.prunhunch.currentData()
        self.player['pkmotion'] = self.ppkmot.currentData()
        self.player['placekicking'] = int(self.pplacekicking.text())
        self.player['playposedited'] = 1 #Reset flag
        self.player['abilityedited'] = 1 #Reset flag
        self.player['skillsedited'] = 1 #Reset flag
        
        self.player['stamina'] = int(self.pstamina.text())
        self.player['speed'] = int(self.pspeed.text())
        self.player['playstyleedited'] = 1 #Reset flag
        self.player['comedited'] = 1 #Reset flag
        
        self.player['motionedited'] = 1 #Reset flag
        self.player['basecopy'] = 0 #Reset flag
        self.player['strfoot'] = self.pfooting.currentData()
        
        i = 0
        for box in Ui_Player._COMSTYLES:
            if(box.isChecked()):
                self.player['comstyles'][i] = 1
            else:
                self.player['comstyles'][i] = 0
            i = i + 1
        
        i = 0
        for box in Ui_Player._SKILLS:
            if(box.isChecked()):
                self.player['playerskills'][i] = 1
            else:
                self.player['playerskills'][i] = 0
            i = i + 1
        
        self.player['name'] = self.pname.text()
        self.player['print'] = self.pshirtname.text()
        
        self.player['facee'] = int(self.pfacee.isChecked())
        self.player['haire'] = int(self.phaire.isChecked())
        self.player['physe'] = int(self.pphyse.isChecked())
        self.player['stripe'] = int(self.pstripe.isChecked())
        self.player['boots'] = int(self.pboots.text())
        self.player['gkgloves'] = int(self.pgkgloves.text())
        
        self.player['skincolour'] = self.pskincol.currentData()
        
        self.player['glasses'] = self.pglasses.currentData()
        self.player['unders'] = self.pshorts.currentData()
        self.player['wtape'] = self.pwristtape.currentData()
        self.player['sleeves'] = self.psleeves.currentData()
        self.player['socks'] = self.psocks.currentData()
        self.player['shirttail'] = self.pshirttail.currentData()
        self.player['ankletape'] = int(self.pankletape.isChecked())
        
        self.player['neckl'] = self.pneckl.value() + 7
        self.player['necks'] = self.pnecks.value() + 7
        self.player['shoulderh'] = self.pshoulderh.value() + 7
        self.player['shoulderw'] = self.pshoulderw.value() + 7
        self.player['chestm'] = self.pchestm.value() + 7
        self.player['waists'] = self.pwaists.value() + 7
        self.player['arms'] = self.parms.value() + 7
        self.player['thighs'] = self.pthighs.value() + 7
        self.player['calfs'] = self.pcalfs.value() + 7
        self.player['legl'] = self.plegl.value() + 7
        self.player['arml'] = self.parml.value() + 7
        self.player['headl'] = self.pheadl.value() + 7
        self.player['headw'] = self.pheadw.value() + 7
        self.player['headd'] = self.pheadd.value() + 7
        
        #Then write to file
        b.seek(120 + self.player['findex']*188)
        b.write(pack('<I', self.player['pid']))
        if(self.player['commid'] == 0):
            b.write(pack('>I', 0xFFFFFFFF))
        else:
            b.write(pack('<I', self.player['commid']))
        b.seek(2, 1) #Skip unknown entry
        b.write(pack('<H', self.player['nationality']))
        b.write(pack('<B', self.player['height']))
        b.write(pack('<B', self.player['weight']))
        b.write(pack('<B', self.player['goal1']))
        b.write(pack('<B', self.player['goal2']))
        
        dat = self.player['attprow']
        dat |= self.player['defprow'] << 7
        dat |= self.player['goalkeeping'] << 14
        dat |= self.player['dribbling'] << 21
        dat |= self.player['fkmotion'] << 28
        b.write(pack('<I', dat))
        
        dat = self.player['finishing']
        dat |= self.player['lowpass'] << 7
        dat |= self.player['loftedpass'] << 14
        dat |= self.player['header'] << 21
        dat |= self.player['form'] << 28
        dat |= self.player['editedplayer'] << 31
        b.write(pack('<I', dat))
        
        dat = self.player['swerve']
        dat |= self.player['catching'] << 7
        dat |= self.player['clearing'] << 14
        dat |= self.player['reflexes'] << 21
        dat |= self.player['injuryres'] << 28
        dat |= self.player['unknownb'] << 30
        dat |= self.player['editedbasic'] << 31
        b.write(pack('<I', dat))
        
        dat = self.player['bodycontrol']
        dat |= self.player['physical'] << 7
        dat |= self.player['kickingpower'] << 14
        dat |= self.player['explosivepower'] << 21
        dat |= self.player['dribblearmmotion'] << 28
        dat |= self.player['editedregpos'] << 31
        b.write(pack('<I', dat))
        
        dat = self.player['age']
        dat |= self.player['regpos'] << 6
        dat |= self.player['unknownc'] << 10
        dat |= self.player['playstyle'] << 11
        b.write(pack('<H', dat))
        
        dat = self.player['ballcontrol']
        dat |= self.player['ballwinning'] << 7
        dat |= self.player['wfacc'] << 14
        b.write(pack('<H', dat))
        
        dat = self.player['jump']
        dat |= self.player['runarmmotion'] << 7
        dat |= self.player['ckmotion'] << 10
        dat |= self.player['coverage'] << 13
        dat |= self.player['wfusage'] << 20
        dat |= self.player['playables'][0] << 22
        dat |= self.player['playables'][1] << 24
        dat |= self.player['playables'][2] << 26
        dat |= self.player['playables'][3] << 28
        dat |= self.player['playables'][4] << 30
        b.write(pack('<I', dat))
        
        dat = self.player['playables'][5]
        dat |= self.player['playables'][6] << 2
        dat |= self.player['playables'][7] << 4
        dat |= self.player['playables'][8] << 6
        dat |= self.player['playables'][9] << 8
        dat |= self.player['playables'][10] << 10
        dat |= self.player['playables'][11] << 12
        dat |= self.player['playables'][12] << 14
        b.write(pack('<H', dat))
        
        dat = self.player['dhunchmotion']
        dat |= self.player['rhunchmotion'] << 2
        dat |= self.player['pkmotion'] << 4
        dat |= self.player['placekicking'] << 6
        dat |= self.player['playposedited'] << 13
        dat |= self.player['abilityedited'] << 14
        dat |= self.player['skillsedited'] << 15
        b.write(pack('<H', dat))

        dat = self.player['stamina']
        dat |= self.player['speed'] << 7
        dat |= self.player['playstyleedited'] << 14
        dat |= self.player['comedited'] << 15
        b.write(pack('<H', dat))

        dat = self.player['motionedited']
        dat |= self.player['basecopy'] << 1
        dat |= self.player['unknownd'] << 2
        dat |= self.player['strfoot'] << 3
        dat |= self.player['unknowne'] << 4
        dat |= self.player['comstyles'][0] << 5
        dat |= self.player['comstyles'][1] << 6
        dat |= self.player['comstyles'][2] << 7
        dat |= self.player['comstyles'][3] << 8
        dat |= self.player['comstyles'][4] << 9
        dat |= self.player['comstyles'][5] << 10
        dat |= self.player['comstyles'][6] << 11
        dat |= self.player['playerskills'][0] << 12
        dat |= self.player['playerskills'][1] << 13
        dat |= self.player['playerskills'][2] << 14
        dat |= self.player['playerskills'][3] << 15
        dat |= self.player['playerskills'][4] << 16
        dat |= self.player['playerskills'][5] << 17
        dat |= self.player['playerskills'][6] << 18
        dat |= self.player['playerskills'][7] << 19
        dat |= self.player['playerskills'][8] << 20
        dat |= self.player['playerskills'][9] << 21
        dat |= self.player['playerskills'][10] << 22
        dat |= self.player['playerskills'][11] << 23
        dat |= self.player['playerskills'][12] << 24
        dat |= self.player['playerskills'][13] << 25
        dat |= self.player['playerskills'][14] << 26
        dat |= self.player['playerskills'][15] << 27
        dat |= self.player['playerskills'][16] << 28
        dat |= self.player['playerskills'][17] << 29
        dat |= self.player['playerskills'][18] << 30
        dat |= self.player['playerskills'][19] << 31
        b.write(pack('<I', dat))

        dat = self.player['playerskills'][20]
        dat |= self.player['playerskills'][21] << 1
        dat |= self.player['playerskills'][22] << 2
        dat |= self.player['playerskills'][23] << 3
        dat |= self.player['playerskills'][24] << 4
        dat |= self.player['playerskills'][25] << 5
        dat |= self.player['playerskills'][26] << 6
        dat |= self.player['playerskills'][27] << 7
        b.write(pack('<B', dat))

        b.write(pack('<B', self.player['unknownf']))
        na = self.player['name'].encode('utf-8')[:45]
        #Terrible way of limiting amount of bytes in string with multi-byte characters, but it werks
        na = na.decode('utf-8', errors='ignore')
        na = na.encode('utf-8')
        pr = self.player['print'].upper().encode('utf-8')[:17]
        pr = pr.decode('utf-8', errors='ignore')
        pr = pr.encode('utf-8')
        b.write(pack("%ds%dx" % (len(na), 46-len(na)), na))
        b.write(pack("%ds%dx" % (len(pr), 18-len(pr)), pr))
        
        b.seek(4, 1)
        dat = self.player['facee']
        dat |= self.player['haire'] << 1
        dat |= self.player['physe'] << 2
        dat |= self.player['stripe'] << 3
        dat |= self.player['boots'] << 4
        dat |= self.player['gkgloves'] << 18
        dat |= self.player['appunknownb'] << 28
        b.write(pack('<I', dat))
        
        b.seek(4, 1)
        
        dat = self.player['neckl']
        dat |= self.player['necks'] << 4
        dat |= self.player['shoulderh'] << 8
        dat |= self.player['shoulderw'] << 12
        dat |= self.player['chestm'] << 16
        dat |= self.player['waists'] << 20
        dat |= self.player['arms'] << 24
        dat |= self.player['arml'] << 28
        b.write(pack('<I', dat))
        
        dat = self.player['thighs']
        dat |= self.player['calfs'] << 4
        dat |= self.player['legl'] << 8
        dat |= self.player['headl'] << 12
        dat |= self.player['headw'] << 16
        dat |= self.player['headd'] << 20
        dat |= self.player['wtapeextra'] << 24
        dat |= self.player['wtape'] << 30
        b.write(pack('<I', dat))

        dat = self.player['glassescol']
        dat |= self.player['glasses'] << 3
        dat |= self.player['sleeves'] << 6
        dat |= self.player['inners'] << 8
        dat |= self.player['socks'] << 10
        dat |= self.player['unders'] << 12
        dat |= self.player['shirttail'] << 14
        dat |= self.player['ankletape'] << 15
        b.write(pack('<H', dat))
        
        b.seek(23, 1)
        dat = self.player['skincolour']
        dat |= self.player['appunknownf'] << 3
        b.write(pack('<B', dat))
        
        b.seek(26, 1)
        
        b.close()
        
        Editor.players[self.player['pid']] = self.player #Write in-editor variables to main dictionary
        Editor.saved = 1 #Set flag for exit confirm
        Editor.playup(self.parent, self.origin, self.item, self.item2) #Let Editor class handle things like current selected player and list status
        
        self.close() #Done, close window
        
class Editor(QMainWindow, Ui_Editor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('img/icon.png'))
        
        #Connect menu signals
        self.actionLOAD_OF.triggered.connect(self.from_edit)
        self.actionSave.triggered.connect(lambda: self.save(0))
        self.actionSave_As.triggered.connect(lambda: self.save(1))
        self.actionExit.triggered.connect(self.closef)
        self.actionDump.triggered.connect(self.dump)
        
        #Connect signals
        self.teamDropdown1.currentIndexChanged.connect(lambda: self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players))
        self.teamDropdown2.currentIndexChanged.connect(lambda: self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players))
        
        self.teamPlayerList1.itemSelectionChanged.connect(lambda: self.player(self.players[self.teamPlayerList1.currentItem().player]))
        self.teamPlayerList2.itemSelectionChanged.connect(lambda: self.player(self.players[self.teamPlayerList2.currentItem().player]))
        self.teamPlayerList1.cellDoubleClicked.connect(self.editp)
        self.teamPlayerList2.cellDoubleClicked.connect(self.editp)
        self.teamPlayerList1.enterPressed.connect(self.editpc)
        self.teamPlayerList2.enterPressed.connect(self.editpc)
        
        self.teamTable.itemSelectionChanged.connect(self.team)
        
        self.playerList.itemSelectionChanged.connect(lambda: self.player(self.players[self.playerList.currentItem().player]))
        #Currently disabled for being a little bitch
        #self.playerList.enterPressed.connect(self.editpc)
        #self.playerList.itemDoubleClicked.connect(self.editpc)
        
        self.bssb.clicked.connect(self.bulk)
        self.bslwb.clicked.connect(self.bulk)
        
        self.p1srslider.valueChanged.connect(self.slider)
        self.p1dlslider.valueChanged.connect(self.slider)
        self.p1compslider.valueChanged.connect(self.slider)
        self.p2srslider.valueChanged.connect(self.slider)
        self.p2dlslider.valueChanged.connect(self.slider)
        self.p2compslider.valueChanged.connect(self.slider)
        self.p3srslider.valueChanged.connect(self.slider)
        self.p3dlslider.valueChanged.connect(self.slider)
        self.p3compslider.valueChanged.connect(self.slider)
        self.p1atts.clicked.connect(self.gameplan)
        self.p1buildup.clicked.connect(self.gameplan)
        self.p1atta.clicked.connect(self.gameplan)
        self.p1pos.clicked.connect(self.gameplan)
        self.p1defs.clicked.connect(self.gameplan)
        self.p1contain.clicked.connect(self.gameplan)
        self.p1press.clicked.connect(self.gameplan)
        self.p2atts.clicked.connect(self.gameplan)
        self.p2buildup.clicked.connect(self.gameplan)
        self.p2atta.clicked.connect(self.gameplan)
        self.p2pos.clicked.connect(self.gameplan)
        self.p2defs.clicked.connect(self.gameplan)
        self.p2contain.clicked.connect(self.gameplan)
        self.p2press.clicked.connect(self.gameplan)
        self.p3atts.clicked.connect(self.gameplan)
        self.p3buildup.clicked.connect(self.gameplan)
        self.p3atta.clicked.connect(self.gameplan)
        self.p3pos.clicked.connect(self.gameplan)
        self.p3defs.clicked.connect(self.gameplan)
        self.p3contain.clicked.connect(self.gameplan)
        self.p3press.clicked.connect(self.gameplan)
        self.p1att1.currentIndexChanged.connect(self.gameplan)
        self.p1att2.currentIndexChanged.connect(self.gameplan)
        self.p1def1.currentIndexChanged.connect(self.gameplan)
        self.p1def2.currentIndexChanged.connect(self.gameplan)
        self.p2att1.currentIndexChanged.connect(self.gameplan)
        self.p2att2.currentIndexChanged.connect(self.gameplan)
        self.p2def1.currentIndexChanged.connect(self.gameplan)
        self.p2def2.currentIndexChanged.connect(self.gameplan)
        self.p3att1.currentIndexChanged.connect(self.gameplan)
        self.p3att2.currentIndexChanged.connect(self.gameplan)
        self.p3def1.currentIndexChanged.connect(self.gameplan)
        self.p3def2.currentIndexChanged.connect(self.gameplan)
        
        self.resflags.clicked.connect(self.flags)
        self.restflags.clicked.connect(self.tflags)
        self.resbcopy.clicked.connect(self.bcopy)
        self.taccept.clicked.connect(self.saveteam)
        
        #Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.save(0))
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, lambda: self.save(1))
    
    skillcount = 0 #Amount of skills
    comcount = 0 #Amount of COM styles
    players = {} #Main player dictionary
    teams = {} #Main team dictionary
    saved = 0 #Flag for exit confirm, set if a player has been edited
    loaded = 0 #Flag to check if EDIT data has been loaded
    efile = None #Location of EDIT file
    iii = 0
    opath = os.path.expanduser('~/Documents/KONAMI/Pro Evolution Soccer 2017/save/') #Default path for PES save folder
    
    #Check if saved savepath file exists and use it if it does
    if(os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tdata.txt'))):
        ob = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tdata.txt'), 'r')
        opath = ob.read()
        ob.close()
    
    #Set palettes for different stats
    nonmed = QPalette()
    nonmed.setColor(9, QColor(255, 255, 255, 255));
    bronze = QPalette()
    bronze.setColor(9, QColor(173, 255, 47, 255));
    silver = QPalette()
    silver.setColor(9, QColor(255, 255, 0, 255));
    gold = QPalette()
    gold.setColor(9, QColor(255, 165, 0, 255));
    full = QPalette()
    full.setColor(9, QColor(255, 0, 0, 255));
    
    #Store possible player positions in convenient dict
    _POSLIST = {0:"GK", 1:"CB", 2:"LB", 3:"RB", 4:"DMF", 5:"CMF", 6:"LMF", 7:"RMF", 8:"AMF", 9:"LWF", 10:"RWF", 11:"SS", 12:"CF"}
    #Store all cards in a convenient dict
    _CARDS = {0:"Scissors Feint", 1:"Flip Flap", 2:"Marseille Turn", 3:"Sombrero", 4:"Cut Behind & Turn", 5:"Scotch Move", 6:"Heading", 7:"Long Range Drive", 8:"Knuckle Shot", 9:"Acrobatic Finishing", 10:"Heel Trick", 11:"First-time Short", 12:"One-touch Pass", 13:"Weighted Pass", 14:"Pinpoint Crossing", 15:"Outside Curler", 16:"Rabona", 17:"Low-lofted Pass", 18:"Low Punt Trajectory", 19:"Long Throw", 20:"GK Long Throw", 21:"Malicia", 22:"Man Marking", 23:"Track Back", 24:"Acrobatic Clear", 25:"Captaincy", 26:"Super Sub", 27:"Fighting Spirit"}
    #Store all COMs in a convenient dict
    _COMS = {0:"Trickser", 1:"Mazing Run", 2:"Speeding Bullet", 3:"Incisive Run", 4:"Long Ball Expert", 5:"Early Cross", 6:"Long Ranger"}
    
    #Load player data from EDIT, populate dicts, fill player lists, generally just do everything
    def from_edit(self):
        f = QFileDialog.getOpenFileName(self, 'Edit File', self.opath, "")
        if(f and f[0].replace(" ", "") != ""):
            ob = open('tdata.txt', 'w')
            ob.write(f[0])
            ob.close()
            if(os.path.exists('out')):
                shutil.rmtree('out')
            subprocess.call(['lib/decrypter17.exe', f[0], 'out'])
            self.efile = f[0]
            if(os.path.exists('out')):
                b = open('out/data.dat', 'rb')
                
                #Process teams
                b.seek(96)
                tc = unpack('<H', b.read(2))[0]
                for i in range(tc):
                    b.seek(3948120 + (i)*480)
                    tl = {}
                    tid = unpack('<I', b.read(4))[0]
                    b.seek(148, 1)
                    tn = b.read(70).decode('utf-8').rstrip(' \t\r\n\0')
                    tsn = b.read(125).decode('utf-8').rstrip(' \t\r\n\0')
                    
                    b.seek(4676240 + (i)*164)
                    b.seek(4, 1)
                    players = []
                    for j in range(32):
                        pid = unpack('<I', b.read(4))[0]
                        if(pid != 0):
                            players.append(pid)
                            
                    b.seek(4676240 + (i)*164)
                    b.seek(132, 1)
                    nums = []
                    for j in range(len(players)):
                        num = unpack('<B', b.read(1))[0]
                        nums.append(num)
                    
                    tl['name'] = tn
                    tl['short'] = tsn
                    tl['players'] = players
                    tl['nums'] = nums
                    tl['tid'] = tid
                    tl['tindex'] = i
                    self.teams[tid] = tl
                #Also process team game plans
                b.seek(4785728, 0)
                for i in range(tc):
                    tgamep = {}
                    tid = unpack('<I', b.read(4))[0]
                    b.seek(99, 1) #Skip to attacking style
                    tgamep['p1atts'] = unpack('<B', b.read(1))[0]
                    tgamep['p1buildup'] = unpack('<B', b.read(1))[0]
                    tgamep['p1atta'] = unpack('<B', b.read(1))[0]
                    tgamep['p1pos'] = unpack('<B', b.read(1))[0]
                    tgamep['p1def'] = unpack('<B', b.read(1))[0]
                    tgamep['p1contain'] = unpack('<B', b.read(1))[0]
                    tgamep['p1press'] = unpack('<B', b.read(1))[0]
                    b.seek(2, 1)
                    tgamep['p1off1'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p1off2'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p1def1'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p1def2'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p1sr'] = unpack('<B', b.read(1))[0]
                    b.seek(1, 1)
                    tgamep['p1dl'] = unpack('<B', b.read(1))[0]
                    tgamep['p1comp'] = unpack('<B', b.read(1))[0]
                    b.seek(16, 1)
                    b.seek(99, 1) #Skip to attacking style
                    tgamep['p2atts'] = unpack('<B', b.read(1))[0]
                    tgamep['p2buildup'] = unpack('<B', b.read(1))[0]
                    tgamep['p2atta'] = unpack('<B', b.read(1))[0]
                    tgamep['p2pos'] = unpack('<B', b.read(1))[0]
                    tgamep['p2def'] = unpack('<B', b.read(1))[0]
                    tgamep['p2contain'] = unpack('<B', b.read(1))[0]
                    tgamep['p2press'] = unpack('<B', b.read(1))[0]
                    b.seek(2, 1)
                    tgamep['p2off1'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p2off2'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p2def1'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p2def2'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p2sr'] = unpack('<B', b.read(1))[0]
                    b.seek(1, 1)
                    tgamep['p2dl'] = unpack('<B', b.read(1))[0]
                    tgamep['p2comp'] = unpack('<B', b.read(1))[0]
                    b.seek(16, 1)
                    b.seek(99, 1) #Skip to attacking style
                    tgamep['p3atts'] = unpack('<B', b.read(1))[0]
                    tgamep['p3buildup'] = unpack('<B', b.read(1))[0]
                    tgamep['p3atta'] = unpack('<B', b.read(1))[0]
                    tgamep['p3pos'] = unpack('<B', b.read(1))[0]
                    tgamep['p3def'] = unpack('<B', b.read(1))[0]
                    tgamep['p3contain'] = unpack('<B', b.read(1))[0]
                    tgamep['p3press'] = unpack('<B', b.read(1))[0]
                    b.seek(2, 1)
                    tgamep['p3off1'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p3off2'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p3def1'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p3def2'] = unpack('<B', b.read(1))[0]
                    b.seek(7, 1)
                    tgamep['p3sr'] = unpack('<B', b.read(1))[0]
                    b.seek(1, 1)
                    tgamep['p3dl'] = unpack('<B', b.read(1))[0]
                    tgamep['p3comp'] = unpack('<B', b.read(1))[0]
                    b.seek(16, 1)
                    b.seek(144, 1)
                    self.teams[tid]['tactics'] = tgamep
                print(len(self.teams))
                    
                #Process players
                b.seek(92)
                pc = unpack('<H', b.read(2))[0]
                b.seek(120)
                for i in range(pc):
                    pid = unpack('<I', b.read(4))[0]
                    pdata = {}
                    playables = {}
                    playerskills = {}
                    comstyles = {}
                    
                    pdata['pid'] = pid
                    pdata['commid'] = unpack('<I', b.read(4))[0]
                    b.seek(2, 1) #Skip unknown entry
                    pdata['nationality'] = unpack('<H', b.read(2))[0]
                    if(pdata['nationality'] == 0):
                        pdata['nationality'] = 231
                    pdata['height'] = unpack('<B', b.read(1))[0]
                    pdata['weight'] = unpack('<B', b.read(1))[0]
                    pdata['goal1'] = unpack('<B', b.read(1))[0]
                    pdata['goal2'] = unpack('<B', b.read(1))[0]
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['attprow'] = (dat & 0b1111111)
                    pdata['defprow'] = (dat >> 7 & 0b1111111)
                    pdata['goalkeeping'] = (dat >> 14 & 0b1111111)
                    pdata['dribbling'] = (dat >> 21 & 0b1111111)
                    pdata['fkmotion'] = (dat >> 28 & 0b1111)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['finishing'] = (dat & 0b1111111)
                    pdata['lowpass'] = (dat >> 7 & 0b1111111)
                    pdata['loftedpass'] = (dat >> 14 & 0b1111111)
                    pdata['header'] = (dat >> 21 & 0b1111111)
                    pdata['form'] = (dat >> 28 & 0b111)
                    pdata['editedplayer'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['swerve'] = (dat & 0b1111111)
                    pdata['catching'] = (dat >> 7 & 0b1111111)
                    pdata['clearing'] = (dat >> 14 & 0b1111111)
                    pdata['reflexes'] = (dat >> 21 & 0b1111111)
                    pdata['injuryres'] = (dat >> 28 & 0b11)
                    pdata['unknownb'] = (dat >> 30 & 0b1)
                    pdata['editedbasic'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['bodycontrol'] = (dat & 0b1111111)
                    pdata['physical'] = (dat >> 7 & 0b1111111)
                    pdata['kickingpower'] = (dat >> 14 & 0b1111111)
                    pdata['explosivepower'] = (dat >> 21 & 0b1111111)
                    pdata['dribblearmmotion'] = (dat >> 28 & 0b111)
                    pdata['editedregpos'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['age'] = (dat & 0b111111)
                    pdata['regpos'] = (dat >> 6 & 0b1111)
                    pdata['unknownc'] = (dat >> 10 & 0b1)
                    pdata['playstyle'] = (dat >> 11 & 0b11111)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['ballcontrol'] = (dat & 0b1111111)
                    pdata['ballwinning'] = (dat >> 7 & 0b1111111)
                    pdata['wfacc'] = (dat >> 14 & 0b11)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['jump'] = (dat & 0b1111111)
                    pdata['runarmmotion'] = (dat >> 7 & 0b111)
                    pdata['ckmotion'] = (dat >> 10 & 0b111)
                    pdata['coverage'] = (dat >> 13 & 0b1111111)
                    pdata['wfusage'] = (dat >> 20 & 0b11)
                    #Playables: CF SS LWF RWF AMF DMF CMF LMF RMF CB LB RB GK
                    playables[0] = (dat >> 22 & 0b11)
                    playables[1] = (dat >> 24 & 0b11)
                    playables[2] = (dat >> 26 & 0b11)
                    playables[3] = (dat >> 28 & 0b11)
                    playables[4] = (dat >> 30 & 0b11)
                    
                    dat = unpack('<H', b.read(2))[0]
                    playables[5] = (dat & 0b11)
                    playables[6] = (dat >> 2 & 0b11)
                    playables[7] = (dat >> 4 & 0b11)
                    playables[8] = (dat >> 6 & 0b11)
                    playables[9] = (dat >> 8 & 0b11)
                    playables[10] = (dat >> 10 & 0b11)
                    playables[11] = (dat >> 12 & 0b11)
                    playables[12] = (dat >> 14 & 0b11)
                    
                    pdata['playables'] = playables
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['dhunchmotion'] = (dat & 0b11)
                    pdata['rhunchmotion'] = (dat >> 2 & 0b11)
                    pdata['pkmotion'] = (dat >> 4 & 0b11)
                    pdata['placekicking'] = (dat >> 6 & 0b1111111)
                    pdata['playposedited'] = (dat >> 13 & 0b1)
                    pdata['abilityedited'] = (dat >> 14 & 0b1)
                    pdata['skillsedited'] = (dat >> 15 & 0b1)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['stamina'] = (dat & 0b1111111)
                    pdata['speed'] = (dat >> 7 & 0b1111111)
                    pdata['playstyleedited'] = (dat >> 14 & 0b1)
                    pdata['comedited'] = (dat >> 15 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['motionedited'] = (dat & 0b1)
                    pdata['basecopy'] = (dat >> 1 & 0b1)
                    pdata['unknownd'] = (dat >> 2 & 0b1)
                    pdata['strfoot'] = (dat >> 3 & 0b1)
                    pdata['unknowne'] = (dat >> 4 & 0b1)
                    #COM Styles: trickster mazerun speedbullet incisiverun lbexpert earlycross longranger
                    comstyles[0] = (dat >> 5 & 0b1)
                    comstyles[1] = (dat >> 6 & 0b1)
                    comstyles[2] = (dat >> 7 & 0b1)
                    comstyles[3] = (dat >> 8 & 0b1)
                    comstyles[4] = (dat >> 9 & 0b1)
                    comstyles[5] = (dat >> 10 & 0b1)
                    comstyles[6] = (dat >> 11 & 0b1)
                    
                    pdata['comstyles'] = comstyles
                    
                    #Player Skills: scissors flipflap marseille sombrero cutbehind scotch heading lrd knuckle acrofinish heeltrick ftp otp weightpass pinpoint curler rabona lowlofted lowpunt longthrow gklongthrow malicia manmark trackback acroclear captaincy supersub fightspirit
                    playerskills[0] = (dat >> 12 & 0b1)
                    playerskills[1] = (dat >> 13 & 0b1)
                    playerskills[2] = (dat >> 14 & 0b1)
                    playerskills[3] = (dat >> 15 & 0b1)
                    playerskills[4] = (dat >> 16 & 0b1)
                    playerskills[5] = (dat >> 17 & 0b1)
                    playerskills[6] = (dat >> 18 & 0b1)
                    playerskills[7] = (dat >> 19 & 0b1)
                    playerskills[8] = (dat >> 20 & 0b1)
                    playerskills[9] = (dat >> 21 & 0b1)
                    playerskills[10] = (dat >> 22 & 0b1)
                    playerskills[11] = (dat >> 23 & 0b1)
                    playerskills[12] = (dat >> 24 & 0b1)
                    playerskills[13] = (dat >> 25 & 0b1)
                    playerskills[14] = (dat >> 26 & 0b1)
                    playerskills[15] = (dat >> 27 & 0b1)
                    playerskills[16] = (dat >> 28 & 0b1)
                    playerskills[17] = (dat >> 29 & 0b1)
                    playerskills[18] = (dat >> 30 & 0b1)
                    playerskills[19] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<B', b.read(1))[0]
                    playerskills[20] = (dat & 0b1)
                    playerskills[21] = (dat >> 1 & 0b1)
                    playerskills[22] = (dat >> 2 & 0b1)
                    playerskills[23] = (dat >> 3 & 0b1)
                    playerskills[24] = (dat >> 4 & 0b1)
                    playerskills[25] = (dat >> 5 & 0b1)
                    playerskills[26] = (dat >> 6 & 0b1)
                    playerskills[27] = (dat >> 7 & 0b1)
                    
                    pdata['playerskills'] = playerskills
                    
                    pdata['unknownf'] = unpack('<B', b.read(1))[0]
                    pdata['name'] = b.read(46).decode('utf-8', errors='ignore').rstrip(' \t\r\n\0')
                    pdata['print'] = b.read(18).replace(b'\xfe', b'').decode('utf-8', errors='ignore').rstrip(' \t\r\n\0')
                    #Below is for when /mlp/'s print name padding gets fixed
                    #pdata['print'] = b.read(18).decode('utf-8').rstrip(' \t\r\n\0')
                    
                    b.seek(4, 1)
                    dat = unpack('<I', b.read(4))[0]
                    pdata['facee'] = (dat & 0b1)
                    pdata['haire'] = (dat >> 1 & 0b1)
                    pdata['physe'] = (dat >> 2 & 0b1)
                    pdata['stripe'] = (dat >> 3 & 0b1)
                    pdata['boots'] = (dat >> 4 & 0b11111111111111)
                    pdata['gkgloves'] = (dat >> 18 & 0b1111111111)
                    pdata['appunknownb'] = (dat >> 28 & 0b1111)
                    
                    b.seek(4, 1)
                    dat = unpack('<I', b.read(4))[0]
                    pdata['neckl'] = (dat & 0b1111)
                    pdata['necks'] = (dat >> 4 & 0b1111)
                    pdata['shoulderh'] = (dat >> 8 & 0b1111)
                    pdata['shoulderw'] = (dat >> 12 & 0b1111)
                    pdata['chestm'] = (dat >> 16 & 0b1111)
                    pdata['waists'] = (dat >> 20 & 0b1111)
                    pdata['arms'] = (dat >> 24 & 0b1111)
                    pdata['arml'] = (dat >> 28 & 0b1111)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['thighs'] = (dat & 0b1111)
                    pdata['calfs'] = (dat >> 4 & 0b1111)
                    pdata['legl'] = (dat >> 8 & 0b1111)
                    pdata['headl'] = (dat >> 12 & 0b1111)
                    pdata['headw'] = (dat >> 16 & 0b1111)
                    pdata['headd'] = (dat >> 20 & 0b1111)
                    pdata['wtapeextra'] = (dat >> 24 & 0b111111)
                    pdata['wtape'] = (dat >> 30 & 0b11)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['glassescol'] = (dat & 0b111)
                    pdata['glasses'] = (dat >> 3 & 0b111)
                    pdata['sleeves'] = (dat >> 6 & 0b11)
                    pdata['inners'] = (dat >> 8 & 0b11)
                    pdata['socks'] = (dat >> 10 & 0b11)
                    pdata['unders'] = (dat >> 12 & 0b11)
                    pdata['shirttail'] = (dat >> 14 & 0b1)
                    pdata['ankletape'] = (dat >> 15 & 0b1)
                    
                    b.seek(23, 1)
                    dat = unpack('<B', b.read(1))[0]
                    pdata['skincolour'] = (dat & 0b111)
                    pdata['appunknownf'] = (dat >> 3 & 0b11111)
                    
                    #TODO: find a better way to do this
                    for tid, tdata in self.teams.items():
                        if(pdata['pid'] in tdata['players']):
                            pdata['tid'] = tid
                    
                    pdata['findex'] = i
                    
                    b.seek(26, 1)
                    
                    self.players[pid] = pdata
                
                b.close()
                
                #Fill player list in GUI
                print(len(self.players))
                self.playerList.clear()
                for id, data in sorted(self.players.items()):
                    item = PlayerItem()
                    item.player = id
                    item.setText(data['name'])
                    self.playerList.addItem(item)
                    
                #Fill team list in GUI
                i = 0
                self.teamTable.clearContents()
                self.teamTable.setRowCount(0)
                for id, data in sorted(self.teams.items()):
                    list = self.teamTable
                    list.insertRow(i)
            
                    item = TeamTableItem()
                    item.team = id
                    item.setText(str(data['tid']))
                    list.setItem(i, 0, item)
                    
                    item = TeamTableItem()
                    item.team = id
                    item.setText(data['short'])
                    list.setItem(i, 1, item)
                    
                    item = TeamTableItem()
                    item.team = id
                    item.setText(data['name'])
                    list.setItem(i, 2, item)
                    i = i + 1
                    
                #Fill team dropdowns
                self.teamDropdown1.blockSignals(1)
                self.teamDropdown2.blockSignals(1)
                self.teamDropdown1.clear()
                self.teamDropdown2.clear()
                for tid, tdata in self.teams.items():
                    self.teamDropdown1.addItem(tdata['name'], tid)
                    self.teamDropdown2.addItem(tdata['name'], tid)
                self.teamDropdown1.setCurrentIndex(0)
                self.teamDropdown2.setCurrentIndex(0)
                self.teamDropdown1.blockSignals(0)
                self.teamDropdown2.blockSignals(0)
                    
                #Manually fire changed signal on team player tables
                self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players)
                self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players)
                
                #Manually set selected player
                self.player(self.players[self.teamPlayerList1.currentItem().player])
                
                #Manually set selected team
                aaa = self.teamTable.setCurrentItem(self.teamTable.item(0, 0))
                
                #Set loaded flag
                self.loaded = 1
  
    def dump(self):
        if(self.loaded != 1):
           n = QMessageBox.information(self, 'Savedata not loaded', "Please load savedata before trying to datadump", QMessageBox.Ok)
        else:
            f = QFileDialog.getSaveFileName(self, 'CSV Dump', self.opath, "")
            if(f and f[0].replace(" ", "") != "") :
                csv = open(f[0], 'w', encoding='utf-8')
                csv.write('Player ID\n')
                csv.write('Player Name\n')
                csv.write('Team Name\n')
                csv.write('Playerappearance: height, weight, age, nationality, boots, gk gloves, goal1, goal2\n')
                csv.write('Playerstats: ability, form, footing, wf acc, wf usage, injury res\n')
                csv.write('Playerstyles: playstyle, regpos, playables (CF, SS, LWF, RWF, AMF, DMF, CMF, LMF, RMF, CB, LB, RB, GK)\n')
                csv.write('Playercards\n')
                csv.write('COM\n\n')
                #print(self.players[70101])
                for id, player in self.players.items():
                
                    #First go through some data that needs processing before it's usable
                    #Starting with ability, try to squeeze it into a single value instead of 23
                    abs = []
                    abs.append(player['attprow'])
                    abs.append(player['defprow'])
                    abs.append(player['goalkeeping'])
                    abs.append(player['dribbling'])
                    abs.append(player['finishing'])
                    abs.append(player['lowpass'])
                    abs.append(player['loftedpass'])
                    abs.append(player['header'])
                    abs.append(player['swerve'])
                    abs.append(player['catching'])
                    abs.append(player['clearing'])
                    abs.append(player['reflexes'])
                    abs.append(player['bodycontrol'])
                    abs.append(player['physical'])
                    abs.append(player['kickingpower'])
                    abs.append(player['explosivepower'])
                    abs.append(player['ballcontrol'])
                    abs.append(player['ballwinning'])
                    abs.append(player['jump'])
                    abs.append(player['coverage'])
                    abs.append(player['placekicking'])
                    abs.append(player['stamina'])
                    abs.append(player['speed'])
                    ab = max(set(abs), key=abs.count) #And we should have our ability
                    
                    if(player['strfoot'] == 0):
                        foot = "Right"
                    else:
                        foot = "Left"
                        
                    playables = ""
                    for id, val in player['playables'].items():
                        if(id == 0):
                            playables = playables + str(val)
                        else:
                            playables = playables + ', ' + str(val)
                    
                    cards = ""
                    ca = 0
                    for id, val in player['playerskills'].items():
                        if(val == 1):
                            if(ca == 0):
                                cards = cards + self._CARDS[id]
                                ca = 1
                            else:
                                cards = cards + ', ' + self._CARDS[id]
                    if(cards == ''):
                        cards = "None"
                            
                    coms = ""
                    ca = 0
                    for id, val in player['comstyles'].items():
                        if(val == 1):
                            if(ca == 0):
                                coms = coms + self._COMS[id]
                                ca = 1
                            else:
                                coms = coms + ', ' + self._COMS[id]
                    if(coms == ''):
                        coms = "None"
                
                    csv.write(str(player['pid']) + '\n')
                    csv.write(player['name'].split('\x00')[0].encode('utf-8').decode('utf-8', errors='ignore') + '\n') #Don't think too hard about it
                    csv.write(self.teams[player['tid']]['name'].split('\x00')[0].encode('utf-8').decode('utf-8', errors='ignore') + '\n')
                    csv.write(str(player['height']) + ', ' + str(player['weight']) + ', ' + str(player['age']) + ', ' + Ui_Player._NATIONALITIES[player['nationality']] + ', ' + str(player['boots']) + ', ' + str(player['gkgloves']) + ', ' + str(player['goal1']) + ', ' + str(player['goal2']) + '\n')
                    csv.write(str(ab) + ', ' + str(player['form']+1) + ', ' + foot + ', ' + str(player['wfacc']+1) + ', ' + str(player['wfusage']+1) + ', ' + str(player['injuryres']+1) + '\n')
                    csv.write(Ui_Player._PLAYSTYLES[player['playstyle']] + ', ' + Ui_Player._POSITIONS[player['regpos']] + ', ' + playables + '\n')
                    csv.write(cards + '\n')
                    csv.write(coms + '\n\n')
                    
                print("Datadump complete")
  
    def bulk(self):
        team = self.teams[self.teamTable.currentItem().team]
        if(self.sender() == self.bssb):
            stat = int(self.bsse.text())
            if(stat < 40):
                stat = 40
            elif(stat > 99):
                stat = 99
            for id in team['players']:
                self.players[id]['attprow'] = stat
                self.players[id]['defprow'] = stat
                self.players[id]['goalkeeping'] = stat
                self.players[id]['dribbling'] = stat
                self.players[id]['finishing'] = stat
                self.players[id]['lowpass'] = stat
                self.players[id]['loftedpass'] = stat
                self.players[id]['header'] = stat
                self.players[id]['swerve'] = stat
                self.players[id]['catching'] = stat
                self.players[id]['clearing'] = stat
                self.players[id]['reflexes'] = stat
                self.players[id]['bodycontrol'] = stat
                self.players[id]['physical'] = stat
                self.players[id]['kickingpower'] = stat
                self.players[id]['explosivepower'] = stat
                self.players[id]['ballcontrol'] = stat
                self.players[id]['ballwinning'] = stat
                self.players[id]['jump'] = stat
                self.players[id]['coverage'] = stat
                self.players[id]['placekicking'] = stat
                self.players[id]['stamina'] = stat
                self.players[id]['speed'] = stat
            #Manually trigger an item selection changed signal to make sure the UI is also aware of the stat changes
            self.player(self.players[self.teamPlayerList1.currentItem().player])
        elif(self.sender() == self.bslwb):
            for id in team['players']:
                self.players[id]['wtape'] = 2
            #Write changes to file
            b = open('out/data.dat', 'r+b')
            for id in team['players']:
                b.seek(120 + self.players[id]['findex']*188) #Skip to correct entry
                b.seek(116, 1) #Skip to appearance block
                b.seek(19, 1) #Skip to wrist tape
                dat = self.players[id]['wtapeextra']
                dat |= self.players[id]['wtape'] << 6
                b.write(pack('B', dat))
            b.close()
            #Manually trigger an item selection changed signal to make sure the UI is also aware of the stat changes
            self.player(self.players[self.teamPlayerList1.currentItem().player])
    
    def gameplan(self):
        team = self.teams[self.teamTable.currentItem().team]
        bt = self.sender()
        
        if(bt == self.p1atts):
            if(team['tactics']['p1atts'] == 0):
                team['tactics']['p1atts'] = 1
                bt.setText("Possession Game")
            else:
                team['tactics']['p1atts'] = 0
                bt.setText("Counter Attack")
        elif(bt == self.p1buildup):
            if(team['tactics']['p1buildup'] == 0):
                team['tactics']['p1buildup'] = 1
                bt.setText("Short-Pass")
            else:
                team['tactics']['p1buildup'] = 0
                bt.setText("Long-Pass")
        elif(bt == self.p1atta):
            if(team['tactics']['p1atta'] == 0):
                team['tactics']['p1atta'] = 1
                bt.setText("Center")
            else:
                team['tactics']['p1atta'] = 0
                bt.setText("Wide")
        elif(bt == self.p1pos):
            if(team['tactics']['p1pos'] == 0):
                team['tactics']['p1pos'] = 1
                bt.setText("Flexible")
            else:
                team['tactics']['p1pos'] = 0
                bt.setText("Maintain Formation")
        elif(bt == self.p1defs):
            if(team['tactics']['p1def'] == 0):
                team['tactics']['p1def'] = 1
                bt.setText("All-Out Defence")
            else:
                team['tactics']['p1def'] = 0
                bt.setText("Frontline Pressure")
        elif(bt == self.p1contain):
            if(team['tactics']['p1contain'] == 0):
                team['tactics']['p1contain'] = 1
                bt.setText("Wide")
            else:
                team['tactics']['p1contain'] = 0
                bt.setText("Middle")
        elif(bt == self.p1press):
            if(team['tactics']['p1press'] == 0):
                team['tactics']['p1press'] = 1
                bt.setText("Conservative")
            else:
                team['tactics']['p1press'] = 0
                bt.setText("Aggressive")
                
        elif(bt == self.p2atts):
            if(team['tactics']['p2atts'] == 0):
                team['tactics']['p2atts'] = 1
                bt.setText("Possession Game")
            else:
                team['tactics']['p2atts'] = 0
                bt.setText("Counter Attack")
        elif(bt == self.p2buildup):
            if(team['tactics']['p2buildup'] == 0):
                team['tactics']['p2buildup'] = 1
                bt.setText("Short-Pass")
            else:
                team['tactics']['p2buildup'] = 0
                bt.setText("Long-Pass")
        elif(bt == self.p2atta):
            if(team['tactics']['p2atta'] == 0):
                team['tactics']['p2atta'] = 1
                bt.setText("Center")
            else:
                team['tactics']['p2atta'] = 0
                bt.setText("Wide")
        elif(bt == self.p2pos):
            if(team['tactics']['p2pos'] == 0):
                team['tactics']['p2pos'] = 1
                bt.setText("Flexible")
            else:
                team['tactics']['p2pos'] = 0
                bt.setText("Maintain Formation")
        elif(bt == self.p2defs):
            if(team['tactics']['p2def'] == 0):
                team['tactics']['p2def'] = 1
                bt.setText("All-Out Defence")
            else:
                team['tactics']['p2def'] = 0
                bt.setText("Frontline Pressure")
        elif(bt == self.p2contain):
            if(team['tactics']['p2contain'] == 0):
                team['tactics']['p2contain'] = 1
                bt.setText("Wide")
            else:
                team['tactics']['p2contain'] = 0
                bt.setText("Middle")
        elif(bt == self.p2press):
            if(team['tactics']['p2press'] == 0):
                team['tactics']['p2press'] = 1
                bt.setText("Conservative")
            else:
                team['tactics']['p2press'] = 0
                bt.setText("Aggressive")
                
        elif(bt == self.p3atts):
            if(team['tactics']['p3atts'] == 0):
                team['tactics']['p3atts'] = 1
                bt.setText("Possession Game")
            else:
                team['tactics']['p3atts'] = 0
                bt.setText("Counter Attack")
        elif(bt == self.p3buildup):
            if(team['tactics']['p3buildup'] == 0):
                team['tactics']['p3buildup'] = 1
                bt.setText("Short-Pass")
            else:
                team['tactics']['p3buildup'] = 0
                bt.setText("Long-Pass")
        elif(bt == self.p3atta):
            if(team['tactics']['p3atta'] == 0):
                team['tactics']['p3atta'] = 1
                bt.setText("Center")
            else:
                team['tactics']['p3atta'] = 0
                bt.setText("Wide")
        elif(bt == self.p3pos):
            if(team['tactics']['p3pos'] == 0):
                team['tactics']['p3pos'] = 1
                bt.setText("Flexible")
            else:
                team['tactics']['p3pos'] = 0
                bt.setText("Maintain Formation")
        elif(bt == self.p3defs):
            if(team['tactics']['p3def'] == 0):
                team['tactics']['p3def'] = 1
                bt.setText("All-Out Defence")
            else:
                team['tactics']['p3def'] = 0
                bt.setText("Frontline Pressure")
        elif(bt == self.p3contain):
            if(team['tactics']['p3contain'] == 0):
                team['tactics']['p3contain'] = 1
                bt.setText("Wide")
            else:
                team['tactics']['p3contain'] = 0
                bt.setText("Middle")
        elif(bt == self.p3press):
            if(team['tactics']['p3press'] == 0):
                team['tactics']['p3press'] = 1
                bt.setText("Conservative")
            else:
                team['tactics']['p3press'] = 0
                bt.setText("Aggressive")
        
        elif(bt == self.p1att1):
            team['tactics']['p1off1'] = self.p1att1.currentIndex()
        elif(bt == self.p1att2):
            team['tactics']['p1off2'] = self.p1att2.currentIndex()
        elif(bt == self.p1def1):
            if(self.p1def1.currentIndex() == 0):
                team['tactics']['p1def1'] = 0
            else:
                team['tactics']['p1def1'] = self.p1def1.currentIndex() + 7
        elif(bt == self.p1def2):
            if(self.p1def2.currentIndex() == 0):
                team['tactics']['p1def2'] = 0
            else:
                team['tactics']['p1def2'] = self.p1def2.currentIndex() + 7
                
        elif(bt == self.p2att1):
            team['tactics']['p2off1'] = self.p2att1.currentIndex()
        elif(bt == self.p2att2):
            team['tactics']['p2off2'] = self.p2att2.currentIndex()
        elif(bt == self.p2def1):
            if(self.p2def1.currentIndex() == 0):
                team['tactics']['p2def1'] = 0
            else:
                team['tactics']['p2def1'] = self.p2def1.currentIndex() + 7
        elif(bt == self.p2def2):
            if(self.p2def2.currentIndex() == 0):
                team['tactics']['p2def2'] = 0
            else:
                team['tactics']['p2def2'] = self.p2def2.currentIndex() + 7
                
        elif(bt == self.p3att1):
            team['tactics']['p3off1'] = self.p3att1.currentIndex()
        elif(bt == self.p3att2):
            team['tactics']['p3off2'] = self.p3att2.currentIndex()
        elif(bt == self.p3def1):
            if(self.p3def1.currentIndex() == 0):
                team['tactics']['p3def1'] = 0
            else:
                team['tactics']['p3def1'] = self.p3def1.currentIndex() + 7
        elif(bt == self.p3def2):
            if(self.p3def2.currentIndex() == 0):
                team['tactics']['p3def2'] = 0
            else:
                team['tactics']['p3def2'] = self.p3def2.currentIndex() + 7
    
    def slider(self):
        team = self.teams[self.teamTable.currentItem().team]
        sl = self.sender()
        
        if(sl == self.p1srslider):
            team['tactics']['p1sr'] = sl.value()
            self.p1srlabel.setText(str(sl.value()))
        elif(sl == self.p1dlslider):
            team['tactics']['p1dl'] = sl.value()
            self.p1dllabel.setText(str(sl.value()))
        elif(sl == self.p1compslider):
            team['tactics']['p1comp'] = sl.value()
            self.p1complabel.setText(str(sl.value()))
        elif(sl == self.p2srslider):
            team['tactics']['p2sr'] = sl.value()
            self.p2srlabel.setText(str(sl.value()))
        elif(sl == self.p2dlslider):
            team['tactics']['p2dl'] = sl.value()
            self.p2dllabel.setText(str(sl.value()))
        elif(sl == self.p2compslider):
            team['tactics']['p2comp'] = sl.value()
            self.p2complabel.setText(str(sl.value()))
        elif(sl == self.p3srslider):
            team['tactics']['p3sr'] = sl.value()
            self.p3srlabel.setText(str(sl.value()))
        elif(sl == self.p3dlslider):
            team['tactics']['p3dl'] = sl.value()
            self.p3dllabel.setText(str(sl.value()))
        elif(sl == self.p3compslider):
            team['tactics']['p3comp'] = sl.value()
            self.p3complabel.setText(str(sl.value()))
    
    def team(self):
        team = self.teams[self.teamTable.currentItem().team]
        
        self.tname.setText(team['name'])
        self.tshort.setText(team['short'])
        
        if(team['tactics']['p1atts'] == 0):
            self.p1atts.setText("Counter Attack")
        else:
            self.p1atts.setText("Possession Game")
        if(team['tactics']['p1buildup'] == 0):
            self.p1buildup.setText("Long-Pass")
        else:
            self.p1buildup.setText("Short-Pass")
        if(team['tactics']['p1atta'] == 0):
            self.p1atta.setText("Wide")
        else:
            self.p1atta.setText("Centre")
        if(team['tactics']['p1pos'] == 0):
            self.p1pos.setText("Maintain Formation")
        else:
            self.p1pos.setText("Flexible")
        if(team['tactics']['p1def'] == 0):
            self.p1defs.setText("Frontline Pressure")
        else:
            self.p1defs.setText("All-Out Defence")
        if(team['tactics']['p1contain'] == 0):
            self.p1contain.setText("Middle")
        else:
            self.p1contain.setText("Wide")
        if(team['tactics']['p1press'] == 0):
            self.p1press.setText("Aggressive")
        else:
            self.p1press.setText("Conservative")
        self.p1srslider.setValue(team['tactics']['p1sr'])
        self.p1dlslider.setValue(team['tactics']['p1dl'])
        self.p1compslider.setValue(team['tactics']['p1comp'])
        self.p1att1.setCurrentIndex(team['tactics']['p1off1'])
        self.p1att2.setCurrentIndex(team['tactics']['p1off2'])
        if(team['tactics']['p1def1'] == 0):
            self.p1def1.setCurrentIndex(0)
        else:
            self.p1def1.setCurrentIndex(team['tactics']['p1def1'] - 7)
        if(team['tactics']['p1def2'] == 0):
            self.p1def2.setCurrentIndex(0)
        else:
            self.p1def2.setCurrentIndex(team['tactics']['p1def2'] - 7)
            
        if(team['tactics']['p2atts'] == 0):
            self.p2atts.setText("Counter Attack")
        else:
            self.p2atts.setText("Possession Game")
        if(team['tactics']['p2buildup'] == 0):
            self.p2buildup.setText("Long-Pass")
        else:
            self.p2buildup.setText("Short-Pass")
        if(team['tactics']['p2atta'] == 0):
            self.p2atta.setText("Wide")
        else:
            self.p2atta.setText("Centre")
        if(team['tactics']['p2pos'] == 0):
            self.p2pos.setText("Maintain Formation")
        else:
            self.p2pos.setText("Flexible")
        if(team['tactics']['p2def'] == 0):
            self.p2defs.setText("Frontline Pressure")
        else:
            self.p2defs.setText("All-Out Defence")
        if(team['tactics']['p2contain'] == 0):
            self.p2contain.setText("Middle")
        else:
            self.p2contain.setText("Wide")
        if(team['tactics']['p2press'] == 0):
            self.p2press.setText("Aggressive")
        else:
            self.p2press.setText("Conservative")
        self.p2srslider.setValue(team['tactics']['p2sr'])
        self.p2dlslider.setValue(team['tactics']['p2dl'])
        self.p2compslider.setValue(team['tactics']['p2comp'])
        self.p2att1.setCurrentIndex(team['tactics']['p2off1'])
        self.p2att2.setCurrentIndex(team['tactics']['p2off2'])
        if(team['tactics']['p2def1'] == 0):
            self.p2def1.setCurrentIndex(0)
        else:
            self.p2def1.setCurrentIndex(team['tactics']['p2def1'] - 7)
        if(team['tactics']['p2def2'] == 0):
            self.p2def2.setCurrentIndex(0)
        else:
            self.p2def2.setCurrentIndex(team['tactics']['p2def2'] - 7)
            
            
        if(team['tactics']['p3atts'] == 0):
            self.p3atts.setText("Counter Attack")
        else:
            self.p3atts.setText("Possession Game")
        if(team['tactics']['p3buildup'] == 0):
            self.p3buildup.setText("Long-Pass")
        else:
            self.p3buildup.setText("Short-Pass")
        if(team['tactics']['p3atta'] == 0):
            self.p3atta.setText("Wide")
        else:
            self.p3atta.setText("Centre")
        if(team['tactics']['p3pos'] == 0):
            self.p3pos.setText("Maintain Formation")
        else:
            self.p3pos.setText("Flexible")
        if(team['tactics']['p3def'] == 0):
            self.p3defs.setText("Frontline Pressure")
        else:
            self.p3defs.setText("All-Out Defence")
        if(team['tactics']['p3contain'] == 0):
            self.p3contain.setText("Middle")
        else:
            self.p3contain.setText("Wide")
        if(team['tactics']['p3press'] == 0):
            self.p3press.setText("Aggressive")
        else:
            self.p3press.setText("Conservative")
        self.p3srslider.setValue(team['tactics']['p3sr'])
        self.p3dlslider.setValue(team['tactics']['p3dl'])
        self.p3compslider.setValue(team['tactics']['p3comp'])
        self.p3att1.setCurrentIndex(team['tactics']['p3off1'])
        self.p3att2.setCurrentIndex(team['tactics']['p3off2'])
        if(team['tactics']['p3def1'] == 0):
            self.p3def1.setCurrentIndex(0)
        else:
            self.p3def1.setCurrentIndex(team['tactics']['p3def1'] - 7)
        if(team['tactics']['p3def2'] == 0):
            self.p3def2.setCurrentIndex(0)
        else:
            self.p3def2.setCurrentIndex(team['tactics']['p3def2'] - 7)
        
    def saveteam(self):
        if(self.loaded == 1):
            #First move unsaved changes to main team dictionary
            team = self.teamTable.currentItem().team
            
            self.teams[team]['name'] = self.tname.text()
            self.teams[team]['short'] = self.tshort.text()
            
            row = self.teamTable.currentItem().row()
            self.teamTable.item(row, 1).setText(self.teams[team]['short'])
            self.teamTable.item(row, 2).setText(self.teams[team]['name'])
            self.teamDropdown1.setItemText(row, self.teams[team]['name'])
            self.teamDropdown2.setItemText(row, self.teams[team]['name'])
            
            #Then save changes to file
            b = open('out/data.dat', 'r+b')
            b.seek(3948120 + self.teams[team]['tindex']*480) #Skip to correct entry
            b.seek(152, 1) #Skip to name field
            
            na = self.tname.text().encode('utf-8')[:69]
            #Terrible way of limiting amount of bytes in string with multi-byte characters, but it werks
            na = na.decode('utf-8', errors='ignore')
            na = na.encode('utf-8')
            sh = self.tshort.text().encode('utf-8')[:3]
            sh = sh.decode('utf-8', errors='ignore')
            sh = sh.encode('utf-8')
            b.write(pack("%ds%dx" % (len(na), 70-len(na)), na))
            b.write(pack("%ds%dx" % (len(sh), 3-len(sh)), sh))
            
            #Also save gameplan changes
            b.seek(4785728 + self.teams[team]['tindex']*628)
            b.seek(103, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1atts']))
            b.write(pack('<B', self.teams[team]['tactics']['p1buildup']))
            b.write(pack('<B', self.teams[team]['tactics']['p1atta']))
            b.write(pack('<B', self.teams[team]['tactics']['p1pos']))
            b.write(pack('<B', self.teams[team]['tactics']['p1def']))
            b.write(pack('<B', self.teams[team]['tactics']['p1contain']))
            b.write(pack('<B', self.teams[team]['tactics']['p1press']))
            b.seek(2, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1off1']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1off2']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1def1']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1def2']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1sr']))
            b.seek(1, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p1dl']))
            b.write(pack('<B', self.teams[team]['tactics']['p1comp']))
            b.seek(16, 1)
            
            b.seek(99, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2atts']))
            b.write(pack('<B', self.teams[team]['tactics']['p2buildup']))
            b.write(pack('<B', self.teams[team]['tactics']['p2atta']))
            b.write(pack('<B', self.teams[team]['tactics']['p2pos']))
            b.write(pack('<B', self.teams[team]['tactics']['p2def']))
            b.write(pack('<B', self.teams[team]['tactics']['p2contain']))
            b.write(pack('<B', self.teams[team]['tactics']['p2press']))
            b.seek(2, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2off1']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2off2']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2def1']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2def2']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2sr']))
            b.seek(1, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p2dl']))
            b.write(pack('<B', self.teams[team]['tactics']['p2comp']))
            b.seek(16, 1)
            
            b.seek(99, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3atts']))
            b.write(pack('<B', self.teams[team]['tactics']['p3buildup']))
            b.write(pack('<B', self.teams[team]['tactics']['p3atta']))
            b.write(pack('<B', self.teams[team]['tactics']['p3pos']))
            b.write(pack('<B', self.teams[team]['tactics']['p3def']))
            b.write(pack('<B', self.teams[team]['tactics']['p3contain']))
            b.write(pack('<B', self.teams[team]['tactics']['p3press']))
            b.seek(2, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3off1']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3off2']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3def1']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3def2']))
            b.seek(7, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3sr']))
            b.seek(1, 1)
            b.write(pack('<B', self.teams[team]['tactics']['p3dl']))
            b.write(pack('<B', self.teams[team]['tactics']['p3comp']))
            b.seek(16, 1)
            
            
            b.close()
    
    def playerlist(self, list, team, players):
        self.teamPlayerList1.blockSignals(1)
        self.teamPlayerList2.blockSignals(1)
        list.setRowCount(0)
        pl = team['players']
        i = 0
        for player in pl:
            nr = team['nums'][i]
            name = players[player]['name']
            pos = self._POSLIST[players[player]['regpos']]
            
            list.insertRow(i)
            
            item = PlayerTableItem()
            item.player = player
            item.setText(pos)
            list.setItem(i, 0, item)
            
            item = PlayerTableItem()
            item.player = player
            item.setText(name)
            list.setItem(i, 1, item)
            
            item = PlayerTableItem()
            item.player = player
            item.setText(str(nr))
            list.setItem(i, 2, item)
            
            i = i + 1
        self.teamPlayerList1.blockSignals(0)
        self.teamPlayerList2.blockSignals(0)
        list.setCurrentCell(0, 1)
    
    def playup(self, origin, item, item2):
        self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players)
        self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players)
        if(origin == self.teamPlayerList1):
            origin.setCurrentIndex(item[0])
            self.teamPlayerList2.setCurrentIndex(item2[0])
        else:
            origin.setCurrentIndex(item[0])
            self.teamPlayerList1.setCurrentIndex(item2[0])
    
    def player(self, player):
        team = self.teams[player['tid']]
        if(player['pid'] in team['players']):
            self.pname.setText(str(player['name']))
            self.shirtname.setText(str(player['print']))
            self.commid.setText(str(player['commid']))
            self.number.setText(str(team['nums'][team['players'].index(player['pid'])]))
            self.club.setText(str(team['name']))
            self.nation.setText(Ui_Player._NATIONALITIES[player['nationality']])
            
            self.attprow.setText(str(player['attprow']))
            self.defprow.setText(str(player['defprow']))
            self.goalkeeping.setText(str(player['goalkeeping']))
            self.dribble.setText(str(player['dribbling']))
            self.finish.setText(str(player['finishing']))
            self.lowpass.setText(str(player['lowpass']))
            self.loftedpass.setText(str(player['loftedpass']))
            self.header.setText(str(player['header']))
            self.swerve.setText(str(player['swerve']))
            self.catching.setText(str(player['catching']))
            self.clearing.setText(str(player['clearing']))
            self.reflexes.setText(str(player['reflexes']))
            self.bodycontrol.setText(str(player['bodycontrol']))
            self.physcont.setText(str(player['physical']))
            self.kickpower.setText(str(player['kickingpower']))
            self.explopower.setText(str(player['explosivepower']))
            self.ballcontrol.setText(str(player['ballcontrol']))
            self.ballwinning.setText(str(player['ballwinning']))
            self.jump.setText(str(player['jump']))
            self.placekicking.setText(str(player['coverage']))
            self.coverage.setText(str(player['placekicking']))
            self.stamina.setText(str(player['stamina']))
            self.speed.setText(str(player['speed']))
            self.ide.setText("ID: " + str(player['pid']))
            self.facee.setText("Face: " + str(player['facee']))
            self.edite.setText("Edit: " + str(player['editedplayer']))
            self.agee.setText("Age: " + str(player['age']))
            self.bodye.setText("Body: " + str(player['height']) + "/" + str(player['weight']))
            if(player['strfoot'] == 0):
                self.foote.setText("Foot: " + 'Right')
            else:
                self.foote.setText("Foot: " + 'Left')
            self.pose.setText("Pos: " + self._POSLIST[player['regpos']])
            
            #Set colours
            for field in Ui_Editor._PDATAFIELDS:
                val = int(field.text())
                if(val >= 70):
                    if(val < 80):
                        field.setPalette(self.bronze)
                    elif(val >= 80 and val < 90):
                        field.setPalette(self.silver)
                    elif(val >= 90 and val < 99):
                        field.setPalette(self.gold)
                    elif(val == 99):
                        field.setPalette(self.full)
                else:
                    field.setPalette(self.nonmed)

    def editpc(self):
        row = self.sender().currentRow()
        if(self.sender() == self.playerList):
            self.editp(row, -1)
        else:
            column = self.sender().currentColumn()
            self.editp(row, column)
                    
    def editp(self, row, column):
        if(column == -1):
            player = self.players[self.sender().item(row).player]
        else:
            player = self.players[self.sender().item(row, column).player]
        item = self.sender().selectionModel().selectedRows()
        if(self.sender() == self.teamPlayerList1):
            item2 = self.teamPlayerList2.selectionModel().selectedRows()
        else:
            item2 = self.teamPlayerList1.selectionModel().selectedRows()
        p = Player(self, player, self.sender(), item, item2)
        p.pid.setText(str(player['pid']))
        p.pname.setText(player['name'])
        p.pshirtname.setText(player['print'])
        p.pcommid.setText(str(player['commid']))
        p.pnationality.setCurrentIndex(Ui_Player._NATINDEX[player['nationality']])
        p.pplayingstyle.setCurrentIndex(player['playstyle'])
        p.page.setText(str(player['age']))
        p.pheight.setText(str(player['height']))
        p.pweight.setText(str(player['weight']))
        p.pform.setCurrentIndex(player['form'])
        p.pfooting.setCurrentIndex(player['strfoot'])
        p.pwfacc.setCurrentIndex(player['wfacc'])
        p.pwfusage.setCurrentIndex(player['wfusage'])
        p.pinjuryres.setCurrentIndex(player['injuryres'])
        
        p.pregpos.setCurrentIndex(player['regpos'])
        for id, pos in player['playables'].items():
            if(int(pos) == 1):
                Ui_Player._PLAYABLES[id].setStyleSheet("background-color: #FFFF00")
            elif(int(pos) == 2):
                Ui_Player._PLAYABLES[id].setStyleSheet("background-color: #FF0000")
                
        p.pattprow.setText(str(player['attprow']))
        p.pdefprow.setText(str(player['defprow']))
        p.pgoalkeeping.setText(str(player['goalkeeping']))
        p.pdribbling.setText(str(player['dribbling']))
        p.pfinishing.setText(str(player['finishing']))
        p.plowpass.setText(str(player['lowpass']))
        p.ploftedpass.setText(str(player['loftedpass']))
        p.pheader.setText(str(player['header']))
        p.pswerve.setText(str(player['swerve']))
        p.pcatching.setText(str(player['catching']))
        p.pclearing.setText(str(player['clearing']))
        p.preflexes.setText(str(player['reflexes']))
        p.pbodycontrol.setText(str(player['bodycontrol']))
        p.pphyscont.setText(str(player['physical']))
        p.pkickpower.setText(str(player['kickingpower']))
        p.pexplopower.setText(str(player['explosivepower']))
        p.pballcontrol.setText(str(player['ballcontrol']))
        p.pballwinning.setText(str(player['ballwinning']))
        p.pjump.setText(str(player['jump']))
        p.pcoverage.setText(str(player['coverage']))
        p.pplacekicking.setText(str(player['placekicking']))
        p.pstamina.setText(str(player['stamina']))
        p.pspeed.setText(str(player['speed']))
        
        for field in Ui_Player._STATS:
            stat = int(field.text())
            if(stat >= 70):
                if(stat < 80):
                    field.setPalette(self.bronze)
                elif(stat >= 80 and stat < 90):
                    field.setPalette(self.silver)
                elif(stat >= 90 and stat < 99):
                    field.setPalette(self.gold)
                elif(stat == 99):
                    field.setPalette(self.full)
            else:
                field.setPalette(self.nonmed)
        i = 0
        self.skillcount = 0
        for box in Ui_Player._SKILLS:
            if(i > 27):
                i = 0
            if(player['playerskills'][i]):
                box.setChecked(1)
                self.skillcount = self.skillcount + 1
            i = i + 1
        p.label_44.setText("Player Skills (" + str(self.skillcount) + "/10)")
        
        i = 0
        self.comcount = 0
        for box in Ui_Player._COMSTYLES:
            if(i > 6):
                i = 0
            if(player['comstyles'][i]):
                box.setChecked(1)
                self.comcount = self.comcount + 1
            i = i + 1
        p.label_46.setText("COM Styles (" + str(self.comcount) + "/5)")
        
        p.pdribhunch.setCurrentIndex(player['dhunchmotion'])
        p.pdribarm.setCurrentIndex(player['dribblearmmotion'])
        p.prunhunch.setCurrentIndex(player['rhunchmotion'])
        p.prunarm.setCurrentIndex(player['runarmmotion'])
        p.pckmot.setCurrentIndex(player['ckmotion'])
        p.pfkmot.setCurrentIndex(player['fkmotion'])
        p.ppkmot.setCurrentIndex(player['pkmotion'])
        
        p.pgoalcel1.setCurrentIndex(player['goal1'])
        p.pgoalcel2.setCurrentIndex(player['goal2'])
        
        p.pfacee.setChecked(player['facee'])
        p.phaire.setChecked(player['haire'])
        p.pphyse.setChecked(player['physe'])
        p.pstripe.setChecked(player['stripe']) 
        p.pskincol.setCurrentIndex(player['skincolour'])
        p.pgkgloves.setText(str(player['gkgloves']))
        p.pboots.setText(str(player['boots']))
        p.pwristtape.setCurrentIndex(player['wtape'])
        p.psleeves.setCurrentIndex(player['sleeves'])
        p.pshirttail.setCurrentIndex(player['shirttail'])
        p.psocks.setCurrentIndex(player['socks'])
        p.pankletape.setChecked(player['ankletape'])
        p.pglasses.setCurrentIndex(player['glasses'])
        p.pshorts.setCurrentIndex(player['unders'])
        
        p.pneckl.setValue(player['neckl']-7)
        p.pnecks.setValue(player['necks']-7)
        p.pshoulderh.setValue(player['shoulderh']-7)
        p.pshoulderw.setValue(player['shoulderw']-7)
        p.pchestm.setValue(player['chestm']-7)
        p.pwaists.setValue(player['waists']-7)
        p.parms.setValue(player['arms']-7)
        p.pthighs.setValue(player['thighs']-7)
        p.pcalfs.setValue(player['calfs']-7)
        p.plegl.setValue(player['legl']-7)
        p.parml.setValue(player['arml']-7)
        p.pheadw.setValue(player['headw']-7)
        p.pheadl.setValue(player['headl']-7)
        p.pheadd.setValue(player['headd']-7)
        
        p.show()
    
    def flags(self):
        if(self.loaded == 1):
            b = open('out/data.dat', 'r+b')
            for pid, data in self.players.items():
                data['facee'] = 0
                data['haire'] = 0
                data['physe'] = 0
                data['stripe'] = 0
                
                dat = data['facee']
                dat |= data['haire'] << 1
                dat |= data['physe'] << 2
                dat |= data['stripe'] << 3
                dat |= data['boots'] << 4
                dat |= data['gkgloves'] << 18
                dat |= data['appunknownb'] << 28
                
                b.seek(120 + data['findex']*188)
                b.seek(120, 1)
                b.write(pack('<I', dat))
            b.close()
            n = QMessageBox.information(self, 'Flags Reset', "All player flags reset successfully", QMessageBox.Ok)
    
    def tflags(self):
        if(self.loaded == 1):
            b = open('out/data.dat', 'r+b')
            b.seek(3948120)
            for pid, data in self.teams.items():
                b.seek(24, 1)
                b.write(pack('>I', 0x00100000))
                b.seek(452, 1)
            b.close()
            n = QMessageBox.information(self, 'Flags Reset', "All team flags reset successfully", QMessageBox.Ok)
    
    def bcopy(self):
        if(self.loaded == 1):
            b = open('out/data.dat', 'r+b')
            for pid, data in self.players.items():
                b.seek(120 + data['findex']*188)
                b.seek(124, 1)
                b.write(pack('<I', data['pid']))
            b.close()
            n = QMessageBox.information(self, 'Flags Reset', "All base copy IDs fixed successfully", QMessageBox.Ok)
    
    def setfpc(self):
        team = self.teamTable.currentItem().team
        b = open('out/data.dat', 'r+b')
        for pid in self.teams[team]['players']:
            self.players[pid]['boots'] = 38
            self.players[pid]['skincolour'] = 7
            self.players[pid]['glasses'] = 0
            self.players[pid]['unders'] = 0
            self.players[pid]['wtape'] = 0
            self.players[pid]['socks'] = 2
            self.players[pid]['shirttail'] = 0
            self.players[pid]['ankletape'] = 0
            self.players[pid]['sleeves'] = 2
            
            if(self.players[pid]['regpos'] == 0):
                self.players[pid]['sleeves'] = 1
                self.players[pid]['gkgloves'] = 12
                
            b.seek(120 + 188*self.players[pid]['findex'])
            b.seek(120, 1)
            
            dat = self.players[pid]['facee']
            dat |= self.players[pid]['haire'] << 1
            dat |= self.players[pid]['physe'] << 2
            dat |= self.players[pid]['stripe'] << 3
            dat |= self.players[pid]['boots'] << 4
            dat |= self.players[pid]['gkgloves'] << 18
            dat |= self.players[pid]['appunknownb'] << 28
            b.write(pack('<I', dat))
            
            b.seek(11, 1)
            
            dat = self.players[pid]['wtapeextra']
            dat |= self.players[pid]['wtape'] << 6
            b.write(pack('<B', dat))

            dat = self.players[pid]['glassescol']
            dat |= self.players[pid]['glasses'] << 3
            dat |= self.players[pid]['sleeves'] << 6
            dat |= self.players[pid]['inners'] << 8
            dat |= self.players[pid]['socks'] << 10
            dat |= self.players[pid]['unders'] << 12
            dat |= self.players[pid]['shirttail'] << 14
            dat |= self.players[pid]['ankletape'] << 15
            b.write(pack('<H', dat))
            
            b.seek(23, 1)
            dat = self.players[pid]['skincolour']
            dat |= self.players[pid]['appunknownf'] << 3
            b.write(pack('<B', dat))
            
        b.close()
        n = QMessageBox.information(self, 'FPC Applied', "FPC settings applied successfully", QMessageBox.Ok)
    
    def restfpc(self):
        team = self.teamTable.currentItem().team
        b = open('out/data.dat', 'r+b')
        for pid in self.teams[team]['players']:
            self.players[pid]['wtape'] = 2
    
            b.seek(120 + 188*self.players[pid]['findex'])
            b.seek(135, 1)
            
            dat = self.players[pid]['wtapeextra']
            dat |= self.players[pid]['wtape'] << 6
            b.write(pack('<B', dat))
        b.close()
        n = QMessageBox.information(self, 'Restore Applied', "Player restore settings applied successfully", QMessageBox.Ok)
    
    def save(self, type):
        if(type == 0):
            subprocess.call(['lib/encrypter17.exe', 'out', self.efile])
            n = QMessageBox.information(self, 'File Saved', "EDIT file saved successfully", QMessageBox.Ok)
        elif(type == 1):
            f = QFileDialog.getSaveFileName(self, 'Edit File', self.opath, "")
            subprocess.call(['lib/encrypter17.exe', 'out', f[0]])
            n = QMessageBox.information(self, 'File Saved', "EDIT file saved successfully", QMessageBox.Ok)
    
    def closeEvent(self, event):
        if(self.saved == 1):
            n = QMessageBox.question(self, 'Close Application', "Unsaved changes will be lost. Are you sure you want to exit?", QMessageBox.Yes, QMessageBox.No)
            if(n == QMessageBox.Yes):
                event.accept()
            if(n == QMessageBox.No):
                event.ignore()
                
    def closef(self):
        if(self.saved == 1):
            n = QMessageBox.question(self, 'Close Application', "Unsaved changes will be lost. Are you sure you want to exit?", QMessageBox.Yes, QMessageBox.No)
            if(n == QMessageBox.Yes):
                sys.exit(0)
        else:
            sys.exit(0)
                        
if __name__ == "__main__":
    p = QApplication(sys.argv)
    w = Editor()
    w.show()
    sys.exit(p.exec_())
#!/usr/bin/python
#! coding: utf-8
u'''
Created on 15.12.2013

@author: Volker Süß, Marvin Süß

12.03.2016 vs + Quasi rewrite, da ab jetzt repr() und eval() verwendet werden sollen
30.01.2016 vs + Dict werden jetzt korrekt unterstützt. XML aus alten Versionen (bis 1.2.0 )sind mit den neuen Versionen kompatibel.
                Alte Versionen sind mit neuen XML aus Versionen < 1.2.0 in denen ein dict geschrieben wurde nicht mehr kompatibel.
                Tuple werden jetzt auch als Tuple wiederhergestellt aus der XML. 
26.01.2016 ms + CheckName-Funktion sauber definiert und Entsprechende Meldung eingebaut
20.01.2016 vs + Pfad als Option ermöglichen - Damit Speicherung an beliebigem Ort ohne das Working-Directory zu verlassen
14.01.2016 vs + Als Variablentyp auch eine list zulassen
28.12.2015 vs + jetzt kompatibel mit Python 2 und 3. Auch die xml kann mit beiden Versionen gelesen und geschrieben werden
                Einziges Problem könnten unicode-String aus Python 3 sein, wenn diese in Python 2 gelesen werden sollen 
27.12.2015 vs + Python 3#fähiger Branch
20.05.2014 ms + Funktion check_name überprüft nun die Bezeichnungen
11.05.2014 vs + Dicts werden jetzt auch unterstützt
10.05.2014 vs + Das Schreiben von Tupeln scheint schonmal soweit zu gehen (auch verschachtelte Tupel)
06.05.2014 ms + get_all - Liefert das Dict mit allen Variablen (Alternative ist der direkte Zugriff -> ini.variablen)
06.05.2014 ms + Test Variablennamen auf ungültige Zeichen
06.05.2014 ms + must_exist - Erstellt kein neues XML
08.01.2014 vs + Filename wird um / bereinigt
05.01.2014 vs + str2boolean - etwas eleganter gelöst
03.01.2014 ms + Dateiname der xml kann festgelegt werden

todo:


'''
import os
import re
import sys
#import types # in Python3 nicht mehr nötig - für Kompatibilität muss das irgendwie umschifft werden
import xml.etree.ElementTree as ET


class ini_v121(object):
    '''
    Soll sich um die Speicherung von diversen Ini-Einstellungen
    kümmern. Permanente Speicherung in einem XML-File  
    '''

    
    def __init__(self, fn='ini', must_exist=False,path=None):
        '''
        Versucht das (fn).xml File im aktuellen Pfad zu lesen. Falls es nicht gelingt ->
        auch nicht so schlimm ;)
        '''
        self._init_allgemein(fn, must_exist, path) # Hier der allgemeine Teil, der auch in V2 verwendet wird
        self.typen = {}
        self.pythonv = sys.version_info[0]
        #print(self.pythonv)
        # Hier die unterstützten Datentypen
        
        self.typen[self.__py2_3(str(int))] = int
        self.typen[self.__py2_3(str(float))] = float
        self.typen[self.__py2_3(str(str))] = str
        if self.pythonv == 2:
            self.typen[self.__py2_3(str(unicode))] = unicode
        self.typen[self.__py2_3(str(bool))] = self.__str2boolean
        self.typen[self.__py2_3(str(tuple))] = ''
        self.typen[self.__py2_3(str(dict))] = ''
        self.typen[self.__py2_3(str(list))] = ''
 
        # bis hierher
        
        
        try:
            self.tree = ET.parse(self.filepath)
        except:# muss genauer werden! (welche genaue exception soll abgefangen werden?)
            if must_exist == False:
                self.root = ET.Element('Variablen')
                self.tree = ET.ElementTree(self.root)
            else:
                raise
        self.variablen = {}
        self.root = self.tree.getroot()
        
        for i in self.root:
#            try:
            name = i.tag
            typ1 = i.attrib['Type']
            typp = self.__py2_3(typ1)
            if typp == self.__py2_3(str(tuple)) or typp == self.__py2_3(str(dict)) or typp == self.__py2_3(str(list)):
                # Hier also tuple/dict und damit Spezialbehandlung
                value = self.__tupledict(i,typp)
            else:
                value = self.typen[typp](i.attrib['Value'])
#             except:
#                 print("Unbekannter Variablentyp oder was auch immer")

            self.variablen[name] = value
    
    def _init_allgemein(self,fn='ini', must_exist=False,path=None):
        u'''
        Ein paar Teile der Init-Funktion, die auch in der neuen Version angewendet werden
        '''
        if path==None:
            self.cwd = os.getcwd()
        else:
            self.cwd = path 
        self.fn = fn+'.xml'
        self.fn = self.fn.replace("/"," ")
        self.filepath = os.path.join(self.cwd,self.fn)
    def __py2_3(self,name):
        ''' Setzt die Bezeichnung von Variablentypen in die entsprechende Python-Version um
            Python 2 -> type ...
            Python 3 -> class ...
            
            Besonderheit bei Python 3 -> Unicode gibt es nicht mehr -> Jetzt alles string.
            Das könnte im Zweifel bei der Verwendung einer Python3 ini.xml in Python2 Probleme machen.
            Sollte aber nicht der Standardfall sein
            '''
        if self.pythonv == 2:
            out = name.replace('class','type')
        else:
            if name == "<type 'unicode'>":
                out = str(str)
            else:
                out = name.replace('type','class')
        return out        
    def __save(self):
        
        #fpath = os.path.join(self.cwd,self.fn)
        self.tree.write(self.filepath)
    
    def __str2boolean(self,wert):
            if wert == 'True':
                return True
            else:
                return False
    def __tupledict(self,werte,typ):
        '''
        Behandelt die Tuple/Dicts/List beim Einlesen
        '''
        if typ == self.__py2_3(str(tuple)) or typ == self.__py2_3(str(list)) :
            value = []
        elif typ == self.__py2_3(str(dict)):
            value = {}
        else:
            raise TypeError
        for i in list(werte):
            typ1 = self.__py2_3(i.attrib['Type'])
            if typ1 == str(tuple) or typ1 == str(dict) or typ1 == str(list):
                # Hier also tuple und damit Spezialbehandlung
                if typ == str(tuple) or typ == str(list):
                    value.append(self.__tupledict(i,typ1))
                elif typ == str(dict):
                    tmp = self.__tupledict(i, typ1) # Typ1 sollte an der Stelle immer Tuple sein!
                    value[tmp[0]] = tmp[1]
                else:
                    raise TypeError
            else:
                if typ == str(tuple) or typ == str(list):
                    #Hier also tuple und damit Spezialbehandlung
                    value.append(self.typen[typ1](i.attrib['Value']))
                elif typ == str(dict):
                    u''' Hier sollten wir korrekterweise nicht mehr rauskommen, aber für Kompatibilität mit
                         der alten Version bleibt die alte Variante aktiv '''
                    value[i.tag] = self.typen[typ1](i.attrib['Value'])
        if typ == str(tuple):
            value = tuple(value)
        return value
    
    def del_ini(self,bezeichnung):
        ''' Löscht die gewählte Variable '''
        t1 = self.root.find(bezeichnung)
        self.root.remove(t1)
        self.__save()
        
    def __check_typ(self,variable):
        '''
        Prüft den Typ und gibt True zurück falls i.O.
        '''
        typ1 = str(type(variable))
        
        if typ1 in self.typen:
            return True
        else:
            print("Falscher Datentyp "+typ1)
            raise TypeError
            return False
    
    def _check_name(self, name):
        erlaubtes_muster = r"[a-zA-Z]+[a-zA-Z0-9_.-]*$"
        match = re.match(erlaubtes_muster, name)
        if match == None or match.group(0) != name:
            raise NameError("Die Bezeichnung soll mit einem Buchstaben beginnen und darf dann nur noch Buchstaben, Ziffern, Unterstriche, Punkte und Minusse beinhalten: " + name)
        return 0
    
    def add_ini(self,bezeichnung,variable):
        '''
        Setzt den Wert einer Variable - Eventuell vorhandene Werte werden ersetzt
        '''
        
        self._check_name(bezeichnung)
        
        t1 = self.root.find(bezeichnung) # Löschen einer früheren Version der Variable
        if t1 == None:
            pass
        else:
            self.root.remove(t1)
        '''
        Die Elementerzeugung sollten wir einen eigenen Funktion überlassen, die auch
        rekursiv aufgerufen werden kann. Die endgültige Rückgabe wird dann dem Root
        hinzugefügt.
        '''
        el = self._make_element(bezeichnung, variable)
        #iNew = ET.Element(bezeichnung)
        #iNew.set('Type', str(type(variable)))
        
            # Zuerst Check der Typen der 
        #iNew.set('Value', str(variable))
        
        self.root.append(el)
        self.variablen[bezeichnung] = variable
        self.__save()
    
    def rename_ini(self):
        ''' Platzhalter für Funktion '''
        return
    def _make_element(self,bezeichnung, variable):
        '''
        Fügt dem Parent als neues Element die Variable hinzu
        '''
        self._check_name(bezeichnung) # erstmal prüfen ob alles im grünen Bereich, was den Namen angeht
        iNew = ET.Element(bezeichnung)
        self.__check_typ(variable)
        iNew.set('Type', str(type(variable)))
        
        if type(variable) == tuple or type(variable) == list:
            zae = 0
            for i in variable:
                el = self._make_element('t'+str(zae), i)
                iNew.append(el)
                zae = zae + 1
        else:
            if type(variable) == dict:
                ''' Dann also ein Dict - auch das ein Spezialfall '''
                u''' Mir schwebt in etwa vor:
                Das Dict wird im Grunde wie eine Liste von key, value gespeichert. Die einzelnen Keys
                müssen dazu (ähnlich wie bei List oben) mit 'k0','k1' usw. bezeichnet werden
                '''
                zae = 0
                for i,j in variable.items():
                    
                    el = self._make_element('k'+str(zae),(i, j))
                    iNew.append(el)
                    zae += 1
            else:
                iNew.set('Value',str(variable))
        return iNew
        
    
    def get_ini(self,bezeichnung):
        ''' Gibt den Wert einer Variable zurück 
        Falls keiner da ist None'''
        try:
            ergebnis = self.variablen[bezeichnung]
        except:
            return None
        return ergebnis
    
    def get_all(self):
        u'''Gibt einfach ein dictionary mit allen
        Variablen und ihren Werten zurück. Falls
        keine Variablen gespeichert sind wird None
        zurückgegeben.'''
        if self.variablen != {}:
            return self.variablen
        else:
            return None

class ini(ini_v121):
    u'''
    Rewrite mit Verwendung von repr() und eval() für Umwandlung in String und reverse
    
    Neue Versionen der XML-Files werden in der XML durch ein Versions-Tag gekennzeichnet.
    
    Damit können auch alte Versionen gelesen werden. Geschrieben werden dann immer neue
    Versionen.
    '''
    def __init__(self, fn='ini', must_exist=False,path=None):
        self.INI_XML_Version = 200
        self._init_allgemein(fn, must_exist, path) # Hier der allgemeine Teil, der auch in V2 verwendet wird
        # Jetzt ist zu checken, ob das übergeben xml aus der alten Version stammt
        self.variablen = {} # Hier sind alle Objekte in einem Dict gespeichert
        try:
            self.tree = ET.parse(self.filepath)
            # File existiert also -> Jetzt check ob Version >=200 oder ob überhaupt Version
            trueroot = self.tree.getroot()
            if trueroot.tag == 'ini_xml': # Dann sollte auch eine Version geschlüsselt sein
                v = trueroot.find('Version')
                version = v.find('Version')
                vers = eval(version.attrib['Value'])
                if vers >= 200: # ab Version 2.0.0 
                    # Aktuelle Version - Einlesen der Variablen
                    self.root = trueroot.find('Variablen')
                    
                    for i in list(self.root):
                        name = i.tag
                        value = i.attrib['Value']
                        self.variablen[name] = eval(value) # Wieder in Originalobjekt umsetzen
                    
            else: # Dann also eine alte Version und wir setzen um
                iniold = ini_v121(fn,must_exist,path)
                self._create_tree(self.INI_XML_Version)
                for i in iniold.get_all():
                    self.add_ini(i[0], i[1])
                del(iniold)
                      
            
            
            
        except:# muss genauer werden! (welche genaue exception soll abgefangen werden?)
            if must_exist == False:
                self._create_tree(self.INI_XML_Version)
                
            else:
                raise
        
    def _create_tree(self,version):
        self.trueroot = ET.Element('ini_xml')
        self.root = ET.Element('Variablen')
        self.version = ET.Element('Version')
        self.version.append(self._make_element('Version',version)) 
        self.trueroot.append(self.version)
        self.trueroot.append(self.root)
        self.tree = ET.ElementTree(self.trueroot)
    def _make_element(self, bezeichnung, variable):
        u'''
        Fügt dem Parent als neues Element die Variable hinzu
        '''
        self._check_name(bezeichnung) # erstmal prüfen ob alles im grünen Bereich, was den Namen angeht
        iNew = ET.Element(bezeichnung)
        iNew.set('Value',repr(variable))
        return iNew
def main(argv):
    import sys
    print(sys.version)
    #pfad = os.path.expanduser('~')
    test = ini('test2')
    try:
        for i in test.get_all().items():
            print(type(i[1]),i)
            print(test.get_ini(i[0]))
    except:
        pass
    print('Nicht vorhandene Variable abfragen = ',test.get_ini('nichtvorhanden'))
    bb = []
    bb.append('list1')
    bb.append('list2')
    test.add_ini('Liste', bb)
    aa = {}
    aa[100] = 102
    aa['test2'] = 'jslkd'
    aa[u'olaä'] = u'Müller'
    test.add_ini('dicttest',aa)
    test.add_ini("Test2",19.0)
    test.add_ini("Boolscher", False)
    test.add_ini("Test3", u"Müller")
    print(u'Müller')
    test.add_ini('Test',(20,(12,20,aa)))
    #test.del_ini('Test3')
    #test.add_ini("geht_nicht&", 1)# enthält nicht erlaubtes Sonderzeichen
    #test.add_ini("5geht_nicht", 2)# beginnt mit Ziffer statt Buchstabe
    #test.add_ini("geht_\t_nicht", 3)# hat Whitespace im Namen
    #test.add_ini("geht_nicht\n", 4)# hat einen Zeilenumbruch im Namen
    for i in test.get_all().items():
        print(type(i[1]),i,test.get_ini(i[0]))
        
    print("Durch")
    del test
    return 0;
# run the main if we're not being imported:
if __name__ == "__main__": sys.exit(main(sys.argv))

        

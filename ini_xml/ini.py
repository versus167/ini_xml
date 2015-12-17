#!/usr/bin/python
#! coding: utf-8
'''
Created on 15.12.2013

@author: Volker Süß, Marvin Süß

tEst
20.05.2014 ms + Funktion check_name überprüft nun die Bezeichnungen
11.05.2014 vs + Dicts werden jetzt auch unterstützt
10.05.2014 vs + Das Schreiben von tuplen scheint schonmal soweit zu gehen (auch verschachtelte tuple)
06.05.2014 ms + get_all - Liefert das Dict mit allen Variablen (Alternative ist der direkte Zugriff -> ini.variablen)
06.05.2014 ms + Test Variablennamen auf ungültige Zeichen
06.05.2014 ms + must_exist - Erstellt kein neues XML
08.01.2014 vs + Filename wird um / bereinigt
05.01.2014 vs + str2boolean - etwas eleganter gelöst
03.01.2014 ms + Dateiname der xml kann festgelegt werden

todo:
__check_name(...) weiter ausbauen

'''
import xml.etree.ElementTree as ET
import sys
import types 
import os

    
class ini(object):
    '''
    Soll sich um die Speicherung von diversen Ini-Einstellungen
    kümmern. Permanente Speicherung in einem XML-File  
    '''

    
    def __init__(self, fn='ini', must_exist=False):
        '''
        Versucht das (fn).xml File im aktuellen Pfad zu lesen. Falls es nicht gelingt ->
        auch nicht so schlimm ;)
        '''
        self.cwd = os.getcwd()
        self.typen = {}
        
        # Hier die unterstützten Datentypen
        
        self.typen[str(types.IntType)] = int
        self.typen[str(types.FloatType)] = float
        self.typen[str(types.StringType)] = str
        self.typen[str(types.UnicodeType)] = unicode
        self.typen[str(types.BooleanType)] = self.__str2boolean__
        self.typen[str(types.TupleType)] = ''
        self.typen[str(types.DictionaryType)] = ''
 
        # bis hierher
        
        self.fn = fn+'.xml'
        self.fn = self.fn.replace("/"," ")
        try:
            self.tree = ET.parse(self.fn)
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
            if typ1 == str(types.TupleType) or typ1 == str(types.DictionaryType):
                # Hier also tuple/dict und damit Spezialbehandlung
                value = self.__tupledict__(i,typ1)
            else:
                value = self.typen[typ1](i.attrib['Value'])
#             except:
#                 print("Unbekannter Variablentyp oder was auch immer")

            self.variablen[name] = value
            
    def __save__(self):
        
        fpath = os.path.join(self.cwd,self.fn)
        self.tree.write(fpath)
    
    def __str2boolean__(self,wert):
            if wert == 'True':
                return True
            else:
                return False
    def __tupledict__(self,werte,typ):
        '''
        Behandelt die Tuple/Dicts beim Einlesen
        '''
        if typ == str(types.TupleType):
            value = []
        elif typ == str(types.DictionaryType):
            value = {}
        else:
            raise TypeError
        for i in list(werte):
            typ1 = i.attrib['Type']
            if typ1 == str(types.TupleType) or typ1 == str(types.DictionaryType):
                # Hier also tuple und damit Spezialbehandlung
                if typ == str(types.TupleType):
                    value.append(self.__tupledict__(i,typ1))
                elif typ == str(types.DictionaryType):
                    value[i.tag] = self.__tupledict__(i,typ1)
                else:
                    raise TypeError
            else:
                if typ == str(types.TupleType):
                    #Hier also tuple und damit Spezialbehandlung
                    value.append(self.typen[typ1](i.attrib['Value']))
                elif typ == str(types.DictionaryType):
                    value[i.tag] = self.typen[typ1](i.attrib['Value'])
        return value
    
    def del_ini(self,bezeichnung):
        ''' Löscht die gewählte Variable '''
        t1 = self.root.find(bezeichnung)
        self.root.remove(t1)
        self.__save__()
        
    def __check_typ(self,variable):
        '''
        Prüft den Typ und gibt True zurück falls i.O.
        '''
        typ1 = str(type(variable))
        
        if self.typen.has_key(typ1):
            return True
        else:
            print("Falscher Datentyp "+typ1)
            raise TypeError
            return False
    
    def __check_name(self,name):
        for zeichen in "*/&%$<>":
            if zeichen in name:
                raise NameError("Achtung: "+name+" aber */&%$<> sind nicht erlaubt")
        return 0
    
    def add_ini(self,bezeichnung,variable):
        '''
        Setzt den Wert einer Variable - Eventuell vorhandene Werte werden ersetzt
        '''
        
        self.__check_name(bezeichnung)
        
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
        el = self.__make_element(bezeichnung, variable)
        #iNew = ET.Element(bezeichnung)
        #iNew.set('Type', str(type(variable)))
        
            # Zuerst Check der Typen der 
        #iNew.set('Value', str(variable))
        
        self.root.append(el)
        self.variablen[bezeichnung] = variable
        self.__save__()
    
    def __make_element(self,bezeichnung, variable):
        '''
        Fügt dem Parent als neues Element die Variable hinzu
        '''
        self.__check_name(bezeichnung) # erstmal prüfen ob alles im grünen Bereich, was den Namen angeht
        iNew = ET.Element(bezeichnung)
        self.__check_typ(variable)
        iNew.set('Type', str(type(variable)))
        
        if type(variable) == types.TupleType:
            zae = 0
            for i in variable:
                el = self.__make_element('t'+str(zae), i)
                iNew.append(el)
                zae = zae + 1
        else:
            if type(variable) == types.DictionaryType:
                ''' Dann also ein Dict - auch das ein Spezialfall '''
                for i,j in variable.items():
                    el = self.__make_element(i, j)
                    iNew.append(el)
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
        '''Gibt einfach ein dictionary mit allen
        Variablen und ihren Werten zur�ck. Falls
        keine Variablen gespeichert sind wird None
        zur�ckgegeben.'''
        if self.variablen != {}:
            return self.variablen
        else:
            return None

def main(argv):
    test = ini('test')
    print test.get_all()
    print "Test = ",test.get_ini('Test')
    print test.get_ini('Boolscher')
    print test.get_ini('dicttest')
    print test.get_ini('nichtvorhanden')
    aa = {}
    aa['t%est1'] = 102
    aa['test2'] = 'jslkd'
    test.add_ini('dicttest',aa)
    test.add_ini("Test2",19.0)
    test.add_ini("Boolscher", True)
    test.add_ini("Test3", "Test")
    test.add_ini('Test',(20,(12,20,aa)))
    #test.del_ini('Test3')
    print test.variablen
    print "Durch"
    del test
    return 0;
# run the main if we're not being imported:
if __name__ == "__main__": sys.exit(main(sys.argv))

        

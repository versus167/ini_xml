# ini_xml
Python Ini-Tool - Alternative zu configparser

Kleines Paket welches unkompliziert die Speicherung von diversen Python-Variablen ermöglicht. Unterstützt Python 2.7 und 3.x.

Im Vergleich zu configparser etwas einfacher. Allerdings zielt ini_xml auch eher darauf ab, die Variablen-Werte aus einem Script
in die nächste Session 'rüberzuretten'. Eine Editierung des XML-Files per Hand ist eher wenig sinnvoll. 

Unterschiede zu configparser:

* Datentypen werden immer so wiederhergestellt, wie sie gespeichert wurden.
* Die Daten werden in dem Moment gespeichert, wenn eine Änderung (add, del usw.) erfolgt.
* Eher nicht auf die händische Editierung der ini-Files ausgelegt 


Unterstützte Variablentypen: int, float, str, unicode (Python 2), bool, dict, tuple, list

Die Verwendung ist in main() dargestellt.

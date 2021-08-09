import json

from Metadata import Metadata

print(dir(Metadata.Clock))
print(Metadata.Clock)

ahmetin_saati = Metadata.Clock("2021-01-15T00:00:00+03:00","2021-01-15T00:00:00+03:00","2021-01-19T23:59:00+03:00",25000,"LOOP_STOP","SYSTEM_CLOCK_MULTIPLIER")

ahmet = Metadata("1.0", 1, "Ahmet")

"""
print( json.dumps(ahmetin_saati.getClockDict()) )
print('\n')self.dict = {"version":self.version,"id":self.id,"name":self.name, "clock":self.clock}
print (type (ahmetin_saati.getClockDict()))
print('\n')
print( json.dumps(ahmet.getMetaDict()) )
"""
print ( dir(ahmet) ) 
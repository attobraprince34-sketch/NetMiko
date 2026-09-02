
def Alerte(equipements):
    alerte = 0

    for e in equipements:


        if e.cpu > 80 :
            alerte += 1


    return alerte
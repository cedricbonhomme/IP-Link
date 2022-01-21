#! /usr/bin/env python
# -*- coding: utf-8 -*-

import operator
import os
import random
from functools import reduce


def genere_col():
    r = random.randint(0, 255)
    v = random.randint(0, 255)
    b = random.randint(0, 255)
    return str(r) + "," + str(v) + "," + str(b)


color = [
    "optblue",
    "optgreen",
    "optyellow",
    "optorange",
    "optred",
    "optviolet",
    "optpurple",
]

tabf = open("./data/ip.circos", "r")
ligne = tabf.readline()[:-1]
liste_ip = ligne.split("\t")[1:]

dic_ip = {}  # contient pour chaque ip le nombre de fois ou elle apparait (s ou d)
for i in liste_ip:
    dic_ip[i] = 0
print(dic_ip)

print(liste_ip)

ligne = tabf.readline()[:-1]

while not ligne == "":
    tab = ligne.split("\t")
    tab2 = []
    for i in tab[1:]:
        if not i == "-":
            tab2.append(int(i))
    v = reduce(operator.add, tab2)  # nombre de paquets ou l'ip est source
    print(tab)
    dic_ip[tab[0]] += v

    # ajoute a chaque ip le nombre de fois ou elle est dest avec cette ip
    for i in range(len(liste_ip)):
        if not tab[i + 1] == "-":
            dic_ip[liste_ip[i]] += int(tab[i + 1])

    ligne = tabf.readline()[:-1]

tabf.close()

try:
    os.mkdir("data")
except:
    pass

karyotype = open("./data/karyotype.txt", "w")
id = 0
for i in dic_ip:
    s = (
        "chr - id"
        + str(id)
        + " "
        + str(id)
        + " 0 "
        + str(dic_ip[i])
        + " id"
        + str(id)
        + "\n"
    )
    karyotype.write(s)
    id += 1
karyotype.close()

colors = open("./data/colors.conf", "w")
id = 0
for i in range(len(dic_ip)):
    s = "id" + str(id) + " " + genere_col() + "\n"
    colors.write(s)
    id += 1
colors.close()

print(dic_ip)

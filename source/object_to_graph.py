#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_graph


"""

import pickle

dic_obj = open("./dic.pyobj", "r")
dic_ip = pickle.load(dic_obj)

print(len(dic_ip))


def split_ip_dic(dic):
    if isinstance(dic, int):
        return dic
    dic2 = {}
    for ips in dic:
        tab = ips.split(".")
        if tab[0] in dic2:
            if tab[1] in dic2[tab[0]]:
                if tab[2] in dic2[tab[0]][tab[1]]:
                    if tab[3] in dic2[tab[0]][tab[1]][tab[2]]:
                        break
                    else:
                        dic2[tab[0]][tab[1]][tab[2]][tab[3]] = split_ip_dic(dic[ips])
                else:
                    dic2[tab[0]][tab[1]][tab[2]] = {}
                    dic2[tab[0]][tab[1]][tab[2]][tab[3]] = split_ip_dic(dic[ips])
            else:
                dic2[tab[0]][tab[1]] = {}
                dic2[tab[0]][tab[1]][tab[2]] = {}
                dic2[tab[0]][tab[1]][tab[2]][tab[3]] = split_ip_dic(dic[ips])
        else:
            dic2[tab[0]] = {}
            dic2[tab[0]][tab[1]] = {}
            dic2[tab[0]][tab[1]][tab[2]] = {}
            dic2[tab[0]][tab[1]][tab[2]][tab[3]] = split_ip_dic(dic[ips])
    return dic2


graphe = split_ip_dic(dic_ip)
print(len(graphe))

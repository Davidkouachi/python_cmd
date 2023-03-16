#importation des bibliothéques
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import askyesno
import hashlib
import tkinter as tk
import sqlite3
import subprocess
import platform
import os
import sys
import socket

conn = sqlite3.connect('bases.db')
cur = conn.cursor()
requete = "CREATE TABLE IF NOT EXISTS table_commande(id_commande INTEGER PRIMARY KEY AUTOINCREMENT, nom_commande TEXT NOT NULL)"
cur.execute(requete)
conn.commit()
requete2 = "CREATE TABLE IF NOT EXISTS table_hash(id_hash INTEGER PRIMARY KEY AUTOINCREMENT,hash_commande TEXT NOT NULL,hash_paramettre TEXT NOT NULL,hash TEXT NOT NULL ,hash_long TEXT NOT NULL)"
cur.execute(requete2)
conn.commit()

noms = []
for row in cur.execute("SELECT nom_commande FROM table_commande"):
    nom = row
    noms.append(row)
list = (noms)



# creation de fonction
def Process():
    resultat.delete("1.0","end")# vider la zone d'affichage de reponse
    host = str(nom_site.get())
    para = str(Combo.get())
    if len(nom_site.get()) == 0 and len(Combo.get()) == 0:
        resultat.insert(INSERT,"Acune commande n'a été entreé, Veuillez saisie une commande")

    if len(nom_site.get()) > 0 and len(Combo.get()) == 0:
        resultat.insert(INSERT,"Acune commande n'a été entreé, Veuillez saisie une commande")

    if len(nom_site.get()) == 0 and len(Combo.get()) > 0:
        param = str(Combo.get())
        cm = subprocess.Popen(param.strip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = cm.communicate()
        print("{0}".format(out))
        print("{0}".format(err))
        resultat.insert(INSERT,"{0}".format(out)+" "+"{0}".format(err))

    if len(nom_site.get()) > 0 and len(Combo.get()) > 0:
        host = str(nom_site.get())
        para = str(Combo.get())
        cm = subprocess.Popen(para.strip()+" "+host.strip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = cm.communicate()
        print(len(out))
        print(len(err))
        resultat.insert(INSERT,"{0}".format(out)+" "+"{0}".format(err))


def option():
    resultat.delete("1.0","end")# vider la zone d'affichage de reponse

    if  len(Combo.get()) == 0:
        resultat.insert(INSERT,"Acune commande n'a été entreé, Veuillez saisie une commande")
    else:
        param = str(Combo.get())
        cm = subprocess.Popen(param.strip()+" /?", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = cm.communicate()
        print("{0}".format(out))
        print("{0}".format(err))
        resultat.insert(INSERT,"{0}".format(out)+" "+"{0}".format(err))

def remise():
    Combo.delete(0,END)
    nom_site.delete(0,END)
    resultat.delete("1.0","end")# vider la zone d'affichage de reponse

def creation():
    # récupération des données du formulaire pour la commande
    if len(Combo.get()) == 0:
        messagebox.showwarning("Notification", "Acune commande n'a été séléctionner")
    conn = sqlite3.connect('bases.db')
    cur = conn.cursor()
    combo = str(Combo.get())
    cur.execute("SELECT count(*) FROM table_commande WHERE nom_commande=(:nom_commande)",{'nom_commande':combo.strip()})
    conn.commit()
    cur_result = cur.fetchone()
    rows = cur_result[0]
    if rows == 0 :
        combo = str(Combo.get())
        cur.execute("INSERT INTO table_commande(nom_commande) VALUES(:nom_commande)",{'nom_commande':combo.strip()})
        conn.commit()
        messagebox.showinfo("Notification", "La commande "+combo.strip()+" à été enregistrée")

        if Combo['values'] == "":
            Combo['values'] = combo.strip()
        else:
            Combo['values'] += (combo.strip(),)

    if rows == 1 :
        messagebox.showerror("Notification", "La commande "+combo.strip()+" existe déjà")
    conn.close()

def item_selected(event):
    for selected_item in table.selection():
        item = table.item(selected_item)
        record = item['values'][0]


def supprimer():
    for selected_item in table.selection():
        item = table.item(selected_item)
        record = item['values'][0]
        if record == " ":
            messagebox.showerror("Notification", "Aucune ligne n'a été sélectionner")
        else:
            supr = askyesno(title='Confirmation',message='Vous etes sur de vouloir supprimer cette ligne de commande ?',icon='warning')
            if supr:
                conn = sqlite3.connect('bases.db')
                cur = conn.cursor()
                cur.execute("DELETE FROM table_hash WHERE id_hash=(:id_hash)",{'id_hash':record})
                conn.commit()
                messagebox.showinfo("Notification", "La ligne de commande Supprimée")

    conn =  sqlite3.connect('bases.db')
    cur = conn.cursor()
    select = cur.execute("select id_hash,hash from table_hash")
    for item in table.get_children():
        table.delete(item)
    for row in select:
        table.insert('', END, value = row)
    conn.close()


def renvoie():
    Combo.delete(0,END)
    nom_site.delete(0,END)
    for selected_item in table.selection():
        item = table.item(selected_item)
        record = item['values'][0]
        if table.item(selected_item):
            conn = sqlite3.connect('bases.db')
            cur = conn.cursor()
            for row in cur.execute("SELECT hash_commande,hash_paramettre FROM table_hash WHERE id_hash=(:id_hash)",{'id_hash':record}):
                conn.commit()
                Combo.set(row[0])
                nom_site.insert(0,row[1])
            conn.close()
    if Combo.get()=="" and nom_site.get()=="":
        messagebox.showwarning("Notification", "Aucune ligne n'a été séléctionner")



def Process_ligne_commnd():
    if  len(nom_site.get()) == 0 or len(Combo.get()) == 0:
        messagebox.showinfo("Notification", "Veuillez remplir tous les champs")
    else:

        conn = sqlite3.connect('bases.db')
        cur = conn.cursor()
        combo = Combo.get()
        nom = nom_site.get()
        obj = combo.strip()+" "+nom.strip()
        hash_obj = hashlib.md5(obj.encode('UTF-8'))
        cur.execute("SELECT count(*) FROM table_hash WHERE hash_long=(:hash_long)",{'hash_long':hash_obj.hexdigest()})
        conn.commit()
        cur_result = cur.fetchone()
        rows = cur_result[0]
        if rows == 0 :
            combo = Combo.get()
            nom = nom_site.get()
            obj = combo.strip()+" "+nom.strip()
            hash_obj = hashlib.md5(obj.encode('UTF-8'))
            cur.execute("INSERT INTO table_hash(hash_commande,hash_paramettre,hash,hash_long) VALUES(:hash_commande,:hash_paramettre,:hash,:hash_long)",
            {
                'hash_commande':combo.strip(),
                'hash_paramettre':nom.strip(),
                'hash':obj,
                'hash_long':hash_obj.hexdigest()
            })
            conn.commit()
            conn.close()
            messagebox.showinfo("Notification", "La linge de commande "+combo.strip()+" à été enregistrer")
            conn =  sqlite3.connect('bases.db')
            cur = conn.cursor()
            select = cur.execute("select id_hash,hash from table_hash")
            for item in table.get_children():
                table.delete(item)
            for row in select:
                table.insert('', END, value = row)
            conn.close()

        else:
            messagebox.showerror("Notification", "La linge de commande "+combo.strip()+" existe déjà")


fen = Tk() # creation de la fenetre
fen.title("CMD") # titre de la fenetre
fen.geometry("1000x700+170+20") # dimension de la fenetre \ position de la fenetre
fen.config(bg="white") # couleur de font de la fenetre
fen.resizable(height = False, width = False)# suppression des bouttons agrandir et minimiser la fenetre
fen.overrideredirect(0) # suppression de la barre de titre de la fenetre

#creation de label, zone de saisie, boutton etc...
lbl = Label(fen, text="VISUALISATION DES COMMANDES CMD",
font=("times new roman",15,"bold"), bg="blue", fg="white", pady=20).pack(fill=X, padx=20, pady=20)

lbl1 = Label(fen, text="Commande :",
font=("arial",10,"bold"), bg="white", fg="black" ).place(x=50,y=120)

Combo = ttk.Combobox(fen, values = list, width=57 )
Combo.set("")
Combo.place(x=140,y=120)
Combo.current()

lbl2 = Label(fen, text="Paramettre :",
font=("arial",10,"bold"), bg="white", fg="black" ).place(x=50,y=150)

nom_site = Entry(fen, font=("arial",10), bg="white", fg="black",width=52 )
nom_site.place(x=140,y=150)

btn_enrg = Button(fen, text="Enregistrer la commande",command = creation ,
font=("arial",10,"bold"), bg="green", fg="white", width=20  ).place(x=50,y=190)

btn_para = Button(fen, text="Voir les options",command = option ,
font=("arial",10,"bold"), bg="green", fg="white", width=15  ).place(x=235,y=190)

btn_valider = Button(fen, text="Execute",command = Process,
font=("arial",10,"bold"), bg="green", fg="white", width=15 ).place(x=380,y=190)

resultat = Text(fen, font=("arial",8), bg="black", fg="white" )
resultat.place(x=50,y=240,width=460,height=400)

btn_remise = Button(fen, text="Remise a zéro",command = remise,
font=("arial",10,"bold"), bg="red", fg="white", width=15 ).place(x=380,y=650)

btn_valider = Button(fen, text="Enregistrer la ligne de commande",command = Process_ligne_commnd,
font=("arial",10,"bold"), bg="green", fg="white", width=30 ).place(x=550,y=190)

btn_renvoie = Button(fen, text="Renvoyer",command = renvoie,
font=("arial",10,"bold"), bg="blue", fg="white", width=10 ).place(x=860,y=190)

table = ttk.Treeview(fen, columns = (1,2), height = 5, show = "headings")
table.place(x=550,y=240,width=400,height=400)


table.heading(1, text="code")
table.column(1, width=50, anchor=CENTER)
table.heading(2, text="Ligne de commande")
table.column(2, width=50, anchor=CENTER)

table.bind('<<TreeviewSelect>>', item_selected)

#btn_enr = Button(fen, text="Enregistrer",command = remise,
#font=("arial",10,"bold"), bg="green", fg="white", width=15 ).place(x=550,y=550)

#btn_modif = Button(fen, text="Modifier",command = remise,
#font=("arial",10,"bold"), bg="blue", fg="white", width=15 ).place(x=680,y=550)

btn_suppr = Button(fen, text="Supprimer",command = supprimer,
font=("arial",10,"bold"), bg="red", fg="white", width=15 ).place(x=820,y=650)

conn =  sqlite3.connect('bases.db')
cur = conn.cursor()
select = cur.execute("select id_hash,hash from table_hash")
for row in select:
    table.insert('', END, value=row)
conn.close()


fen.mainloop() #fermeture de la creation de la fenetre

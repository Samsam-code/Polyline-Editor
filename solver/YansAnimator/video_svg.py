from YansAnimator.draw_svg import *
import cairosvg
import os
import cv2
from PIL import Image


# Pour créer une vidéo, on va utiliser les deux librairies à installer:
# cairosvg => installer avec l'instruction dans anaconda: conda install cairosvg 
# opencv (noté ci-dessus cv2) => installer avec l'instruction dans anaconda: conda install opencv-python 
# une fois ces deux packages installés, l'execution ne devrait plus donner d'erreur au niveau des lignes de code ci-dessus

# ATTENTION:::::::: créez un répertoire appelé "temp" dans le répertoire contenant ce programme
# Il servira à accueillir les centaines de fichiers temporaires qui vont constituer els images successives de la vidéo
# nameimage="image" #C'est le nom qui sera utilisé pour les images temporaires
# nametemp="temp" #C'est le nom du dossier qui stocke temporairement les images
# La vidéo sera créée dans le dossier qui contient ce programme. 
# Elle sera appelée selon le nom suivant suivi d'un identifiant (un entier de 0 à 99)
# video_name="ma_nouvelle_video"


# La vidéo que l'on va créer a plusieurs paramètres à déterminer maintenant:

#fps=30 # c'est le nombre d'images par seconde
#duration=10 #c'est la durée de la vidéo en seconde. 
#Si vous choisissez une durée trop courte, les mouvements entre les images seront trop rapides eton ne verra rien
#si vous choisissez une durée trop longue, les images sembleront presque fixes...


# Une vidéo est constituée d'une succession d'images.
# Pour créer la vidéo, il faut donc créer ces images.
# Nous allons utiliser un paramètre t pour paramétrer les images.
# L'image t=0 est la première image qui sera visualisée
# L'image t=1 est la dernière image de la vidéo 
# L'image t=0.3 est l'image qui apparaîtra au temps 0.3*duration
# Autrement dit, l'image  t est l'image vue à l'instant t*duration

# L'essentiel du travail de création de la vidéo consiste à rcéer la fonction qui crée l'image de paramètre t en format svg . 
# Cette fonction s'appelle image_t


################### Exercice 2 ########################
# 1)  Créer une vidéo d'un carré centré au milieu de la fenêtre et dont la taille change dans le temps
#     Renommer la vidéo créée pour la décrire
# 2)  Créer une vidéo d'un polygone qui change de couleur et dont les sommets se déplacent de façon aléatoire (ou déterminée)) 
# 3)  Créer une vidéo d'un rectangle dont la hauteur va de 10 à 50 puis de 50 à 20 puis de 20 à 35 puis de 35 à 10...
# 4)  Créer une vidéo avec des rectangles dont la hauteur varie en fonction du temps

def image_t(t,filename):
    # On définit une petite fonction qui permet de créer un arc de couleurs allant du jaune au bleu
    # Elle fournit une liste de 1000 couleurs
    nnn=1000
    def colors():
        yellow = (255, 255, 0)
        red = (255, 0, 0)
        green = (0, 255, 0)
        blue = (0, 0, 255)
        i=0
        colors=["rgb(255,255,0)"]
        for i in range(nnn):
            t=i/nnn
            if t>0:
                if t<=1/4:
                    #yellow to red
                    u=int(t*1020)
                    #print(u)
                    colors.append(f"rgb({255},{255-u},{0})")
                elif t<=1/2:
                    #red to green
                    u=int((t-1/4)*1020)
                    #print(u)
                    colors.append(f"rgb({255-u},{u},{0})")
                elif t<=3/4:
                    #green to blue
                    u=int((t-1/2)*1020)
                    #print(u)
                    colors.append(f"rgb(0,{255-u},{u})")
                else:
                    u=int((t-3/4)*1020)
                    colors.append(f"rgb({u},{u},{255-u})")
        colors.append("rgb(255,255,0)")
        return colors
    colors_arc=colors()
    #print(f"On a créé l'arc de couleurs: {colors_arc}")
        
    #Créons maintenant l'image    
    grid=[20,80,50,10]
    file=createSVG(filename)
    drawWindow(file, grid)
    # C'est la zone à modifier pour choisir ce que vous mettez dans votre image (vous pouvez aussi changer la grille grid)
    backgroundColor(file, grid, "black")
    A=(0,grid[2]/2)
    B=(grid[1],grid[2]/2)
    center=((1-t)*A[0]+t*B[0],(1-t)*A[1]+t*B[1])
    drawGrid(file, grid, "white")
    drawDisk(file, grid, center, 10, colors_arc[int((nnn-1)*t)])   
    closeSVG(file)


#Une fonction pour tester que votre création d'image fonctionne
    
def test_image_t():   
    print("start test_image_t") 
    t= random.uniform(0,1)
    image_t(t,"test_image_t.svg")
    
#test_image_t()

#######################################################################################
# Les fonctions ci-dessous ne sont pas forcément à modifier

#La fonction qui crée toutes les images en jpeg et les met dans le dossier des images temporaires

def creation_de_toutes_les_images(image_t, fps, duration, nametemp, nameimage):
    print("start creation_de_toutes_les_images")
    n=fps*duration
    namesimages=[]
    cste=100000 #utiliser pour bien ordonner les images
    for i in range(n+1):
        filenamesvg=f"{nametemp}/{nameimage}_temp_{i+cste}.svg"
        filenamejpeg=f"{nametemp}/{nameimage}_temp_{i+cste}.jpeg"
        image_t(i/n, filenamesvg)
        cairosvg.svg2png(url=filenamesvg, write_to=filenamejpeg)
        os.remove(filenamesvg)
        namesimages.append(filenamejpeg)
    print("end creation_de_toutes_les_images")
    return namesimages

# La fonction qui récupère toutes les images dans le fichier temporaire, les ordonne selon leur nom et en fait une vidéo       

def create_video_from_images(nom_video, fps, nametemp, namesimages):
    print("start create_video_from_images")
    # Load images in the correct order:
    images = sorted(
        [img for img in os.listdir(nametemp) if img.endswith(".jpeg")],
        key=lambda x: int(x.split("_")[-1].split(".")[0])
    )

    print(f"loads {len(images)} images")
    frame = cv2.imread(os.path.join(nametemp, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(nom_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(nametemp, image)))

    cv2.destroyAllWindows()
    video.release()
    #On supprime les noms d'images consecutives qui pourraient être redonants dans la liste
    i=0
    while i<len(namesimages)-1:
        if namesimages[i]==namesimages[i+1]:
            namesimages.pop(i+1)
        else:
            i=i+1
    #print(namesimages)
    for tempfilename in namesimages:
        os.remove(tempfilename)
    print("end create_video_from_images")

def create_gif_from_images(nom_gif, fps, nametemp, namesimages):
    print("start create_gif_from_images")

    # Load images in the correct order
    images = sorted(
        [img for img in os.listdir(nametemp) if img.endswith(".jpeg")],
        key=lambda x: int(x.split("_")[-1].split(".")[0])
    )

    print(f"loads {len(images)} images")

    # Convert fps to GIF frame duration (ms per frame)
    duration = int(1000 / fps)

    # Load frames and convert to a consistent mode
    frames = [Image.open(os.path.join(nametemp, img)).convert("P", palette=Image.ADAPTIVE) for img in images]

    # Save GIF
    frames[0].save(
        nom_gif,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )

    # Remove consecutive duplicate names
    i = 0
    while i < len(namesimages) - 1:
        if namesimages[i] == namesimages[i + 1]:
            namesimages.pop(i + 1)
        else:
            i += 1

    # Delete temp files
    for tempfilename in namesimages:
        if os.path.exists(tempfilename):
            os.remove(tempfilename)

    print("end create_gif_from_images")
        
# La fonction finale qui crée la vidéo       
        
def create_video(video_name, image_t, fps, duration, nametemp="temp", nameimage="image"):
    print("start create_video")
    idvideo=random.randint(0,100)
    nom_video = f"{video_name}_{idvideo}.mp4"
    namestempimages=creation_de_toutes_les_images(image_t, fps, duration, nametemp, nameimage)
    #j=len(namestempimages)
    create_video_from_images(nom_video, fps, nametemp, namestempimages)
    print(f"created video: {nom_video}")

def create_gif(gif_name, image_t, fps, duration, nametemp="temp", nameimage="image"):
    print("start create_gif")
    idvideo=random.randint(0,100)
    nom_video = f"{gif_name}_{idvideo}.gif"
    namestempimages=creation_de_toutes_les_images(image_t, fps, duration, nametemp, nameimage)
    #j=len(namestempimages)
    input()
    create_gif_from_images(nom_video, fps, nametemp, namestempimages)
    print(f"created gif: {nom_video}")
    
#create_video("test", image_t, fps=24, duration=10)
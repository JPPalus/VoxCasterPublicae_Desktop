### TODO

- [ ] Changer le widget QmediaPLayer en un lecteur VLC embarqué.
    - [x] ~~Wrapper d'un lecteur vlc dans un QWidget.~~
    - [x] ~~Bouton play / pause fonctionnel.~~
    - [x] ~~Volume slidder fonctionnel.~~
    - [x] ~~Duration et currentTime labels fonctionnels.~~
    - [ ] Rendre le contrôle du volume non-logarithmique.
    - [x] ~~Regarder ce que fait la méthode "parse()".~~
    - [x] ~~Permettre intéraction avec le positionSlider.~~ 
    - [x] ~~Icônes de volume~~.
    - [ ] Ajouter la gestion du MIDI.
    - [ ] get_chapters().
- [x] ~~Arranger l'arbre des fichiers.~~
- [x] Mettre un slider horizontal sur l'arbre.
- [x] ~~Implémenter les boutons de contrôle.~~
- [X] ~~Implémenter un breadcrumb dans la QGroupBox Curently Playing" et le rendre intéractif.~~
- [X] ~~Ajouter, via ffmpeg, à la création de la DB les metadatas.~~
- [X] ~~Recupérer l'art et l'ajouter à la DB.~~
- [x] ~~Migrer la gestion de la DB serverside~~.
- [ ] Gestion / création de playlists.
- [ ] Ajouter des Widgets DSP. 
- [ ] Barre de menu façon Foobar2000.
    - [ ] Reload DB
- [x] ~~Contrôles au clavier~~.
- [ ] Download.
- [ ] Style.


### BUGS
- [ ] QAudioplayer.statusBar ne gère pas les noms de fichiers contenant un point. QAudioPlayer.py ligne 145.
- [ ] Le fichier OST -> Film -> Alien -> 1-15 The Shaft n'est pas dans le bon dossier
---

### Détails d'implémentation

#### Le cas "libvlc.dll" sur Windows

Dans la grande tradition des logiciels libres qui consiste à casser quelque chose qui marche très bien au nom de la Sécurité™, VLC a décidé de ne plus rendre accessible à l'OS le PATH de "libvlc.dll". Le dossier d'installation de VLC doit donc être préalablement ajouté manuellement au PATH.

#### Le cas "libvlc.dylib" sur MacOS
```
OSError: dlopen(libvlc.dylib, X): image not found
``` 
Problème réglé par : 
- brew install --cask vlc
- Mettre "lib/libvlc.dylib" dans le PATH

### Requirements 

PyQt6 >= 6.4.2
VLC media player >= 3.0
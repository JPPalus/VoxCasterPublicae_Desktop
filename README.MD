### TODO

- Changer le widget QmediaPLayer en un lecteur VLC embarqué.
    - ~~Wrapper d'un lecteur vlc dans un QWidget.~~
    - ~~Bouton play / pause fonctionnel.~~
    - ~~Volume slidder fonctionnel.~~
    - Duration et currentTime labels fonctionnels
    - Rendre le contrôle du volume non-logarithmique.
    - Regarder ce que fait la méthode "parse()".
    - Permettre intéraction avec le positionSlider. 
- Implémenter les boutons de contrôle.
- Implémenter un breadcrumb dans la QGroupBox Curently Playing" et le rendre intéractif.
- Ajouter, via ffmpeg, à la création de la DB les metadatas.
- Recupérer l'art et l'ajouter à la DB.
- Migrer la gestion de la DB serverside.
- Gestion / création de playlists.
- Ajouter des Widgets DSP.
- Barre de menu façon Foobar2000.
- Style.

---

### Détails d'implémentation

#### Le cas "libvlc.dll"

Sur Windows, dans la grande tradition des logiciels libres qui consiste à casser quelque chose qui marche très bien au nom de la Sécurité™, VLC a décidé de ne plus rendre accessible à l'OS le PATH de "libvlc.dll". Le dossier d'installation de VLC doit donc être préalablement ajouté manuellement au PATH.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conversion d'un compte-rendu Markdown en PDF, sans dependance reseau.

Le script ne s'appuie que sur reportlab et sur les polices DejaVu du systeme
(pas de navigateur, pas de CDN, pas de LaTeX) : il fonctionne hors ligne.

Syntaxe Markdown prise en charge
--------------------------------
    # Titre de niveau 1            ## niveau 2        ### niveau 3
    **gras**   `code en ligne`   ^{exposant}   _{indice}
    - element de liste         1. element numerote
    > citation                  ---  (filet horizontal)
    ```lang ... ```             bloc de code (colorisation neutre)
    | a | b |                   tableau, avec ligne de separation |:--|:-:|
    ::: Type ... :::            encadre (Type : Enonce, Reponse, ...)
    <!-- toc -->                table des matieres automatique
    <!-- pagebreak -->          saut de page force
    {{CODE}} / {{TRACE}}        inclusion d'un fichier externe (voir main)

En tete du fichier, un bloc YAML minimal fournit les metadonnees
(title, subtitle, cours, author, classe, date, fichiers).
"""
import os
import re
import sys
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Flowable,
    Frame,
    HRFlowable,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Charte graphique
# ---------------------------------------------------------------------------
ENCRE = colors.HexColor("#12263a")       # texte principal
ACCENT = colors.HexColor("#1a4f7a")      # bleu profond (titres, filets)
ACCENT_2 = colors.HexColor("#0f766e")    # sarcelle (encadres)
GRIS = colors.HexColor("#5b6773")        # texte secondaire
GRIS_CLAIR = colors.HexColor("#e4e9ee")
FOND = colors.HexColor("#f7f9fb")
FOND_CODE = colors.HexColor("#f4f6f8")
FOND_ENONCE = colors.HexColor("#f5f5f4")
BORD_ENONCE = colors.HexColor("#b8b8b4")
BORD_CODE = colors.HexColor("#d5dce3")

POLICES = {
    "DejaVu": ("DejaVuSans.ttf",),
    "DejaVu-Bold": ("DejaVuSans-Bold.ttf",),
    "DejaVuMono": ("DejaVuSansMono.ttf",),
    "DejaVuMono-Bold": ("DejaVuSansMono-Bold.ttf",),
    "DejaVuSerif": ("DejaVuSerif.ttf",),
    "DejaVuSerif-Bold": ("DejaVuSerif-Bold.ttf",),
}
DOSSIERS_POLICES = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/usr/local/share/fonts",
    os.path.expanduser("~/.fonts"),
    "/Library/Fonts",
    "/System/Library/Fonts",
]


def enregistre_polices():
    """Enregistre les polices DejaVu disponibles (avec repli sur Helvetica)."""
    trouvees = 0
    for nom, fichiers in POLICES.items():
        for dossier in DOSSIERS_POLICES:
            chemin = os.path.join(dossier, fichiers[0])
            if os.path.exists(chemin):
                pdfmetrics.registerFont(TTFont(nom, chemin))
                trouvees += 1
                break
    if trouvees < len(POLICES):
        manquantes = [n for n in POLICES if n not in pdfmetrics.getRegisteredFontNames()]
        sys.stderr.write(
            "Attention : polices introuvables %s ; le rendu utilisera les polices "
            "de base, moins fideles.\n" % ", ".join(manquantes)
        )
    pdfmetrics.registerFontFamily(
        "DejaVu", normal="DejaVu", bold="DejaVu-Bold",
        italic="DejaVuSerif", boldItalic="DejaVuSerif-Bold",
    )


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def fabrique_styles():
    s = {}
    s["corps"] = ParagraphStyle(
        "corps", fontName="DejaVu", fontSize=9.5, leading=16.1,
        textColor=ENCRE, alignment=TA_JUSTIFY, spaceAfter=6.5,
    )
    s["h1"] = ParagraphStyle(
        "h1", fontName="DejaVu-Bold", fontSize=17, leading=21,
        textColor=ACCENT, spaceBefore=16, spaceAfter=8, keepWithNext=1,
    )
    s["h2"] = ParagraphStyle(
        "h2", fontName="DejaVu-Bold", fontSize=11.8, leading=15,
        textColor=ENCRE, spaceBefore=12, spaceAfter=5, keepWithNext=1,
    )
    s["h3"] = ParagraphStyle(
        "h3", fontName="DejaVu-Bold", fontSize=10.2, leading=13.5,
        textColor=ACCENT, spaceBefore=9, spaceAfter=4, keepWithNext=1,
    )
    s["liste"] = ParagraphStyle(
        "liste", parent=s["corps"], leftIndent=16, bulletIndent=3,
        spaceAfter=3, alignment=TA_LEFT,
    )
    s["citation_imbriquee"] = ParagraphStyle(
        "citation2", fontName="DejaVuSerif", fontSize=9.2, leading=16.4,
        textColor=colors.HexColor("#33475b"), leftIndent=12, rightIndent=4,
        spaceBefore=4, spaceAfter=5, alignment=TA_LEFT,
    )
    s["citation"] = ParagraphStyle(
        "citation", fontName="DejaVuSerif", fontSize=9.4, leading=15.8,
        textColor=colors.HexColor("#2f3e4c"), leftIndent=10, rightIndent=6,
        spaceBefore=2, spaceAfter=2, alignment=TA_LEFT,
    )
    s["code"] = ParagraphStyle(
        "code", fontName="DejaVuMono", fontSize=7.9, leading=10.2,
        textColor=colors.HexColor("#1d2b36"), alignment=TA_LEFT,
        spaceBefore=0, spaceAfter=0,
    )
    s["cellule"] = ParagraphStyle(
        "cellule", fontName="DejaVu", fontSize=8.4, leading=11.4,
        textColor=ENCRE, alignment=TA_LEFT,
    )
    s["cellule_entete"] = ParagraphStyle(
        "cellule_entete", fontName="DejaVu-Bold", fontSize=8.2, leading=11,
        textColor=colors.white, alignment=TA_LEFT,
    )
    s["titre_encadre"] = ParagraphStyle(
        "titre_encadre", fontName="DejaVu-Bold", fontSize=7.6, leading=10,
        textColor=ACCENT, spaceAfter=3,
    )
    s["toc1"] = ParagraphStyle(
        "toc1", fontName="DejaVu-Bold", fontSize=9.6, leading=13,
        textColor=ENCRE,
    )
    s["toc2"] = ParagraphStyle(
        "toc2", fontName="DejaVu", fontSize=8.8, leading=12,
        textColor=GRIS, leftIndent=12,
    )
    s["toc_page"] = ParagraphStyle(
        "toc_page", fontName="DejaVu", fontSize=9, leading=13,
        textColor=GRIS, alignment=2,
    )
    s["couverture_titre"] = ParagraphStyle(
        "cv_titre", fontName="DejaVu-Bold", fontSize=30, leading=35,
        textColor=colors.white,
    )
    s["couverture_sous"] = ParagraphStyle(
        "cv_sous", fontName="DejaVu", fontSize=12, leading=17,
        textColor=colors.HexColor("#cfe0ee"),
    )
    s["couverture_sur"] = ParagraphStyle(
        "cv_sur", fontName="DejaVu-Bold", fontSize=9, leading=13,
        textColor=colors.HexColor("#8fb3cf"),
    )
    return s


# ---------------------------------------------------------------------------
# Mise en forme en ligne
# ---------------------------------------------------------------------------
def _mesure(texte, gras=False):
    """Largeur approximative du texte, balisage en ligne retire."""
    propre = re.sub(r"[`*]", "", texte)
    propre = re.sub(r"[\^_]\{([^}]*)\}", r"\1", propre)
    police = "DejaVu-Bold" if gras else "DejaVu"
    return pdfmetrics.stringWidth(propre, police, 8.2 if gras else 8.4)


def _echappe(texte):
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


TAB_SUP = {
    "0": "\u2070", "1": "\u00b9", "2": "\u00b2", "3": "\u00b3", "4": "\u2074",
    "5": "\u2075", "6": "\u2076", "7": "\u2077", "8": "\u2078", "9": "\u2079",
    "+": "\u207a", "-": "\u207b", "\u2212": "\u207b", "=": "\u207c",
    "(": "\u207d", ")": "\u207e", "i": "\u2071", "n": "\u207f",
    "k": "\u1d4f", "L": "\u1d38",
}
TAB_SUB = {
    "0": "\u2080", "1": "\u2081", "2": "\u2082", "3": "\u2083", "4": "\u2084",
    "5": "\u2085", "6": "\u2086", "7": "\u2087", "8": "\u2088", "9": "\u2089",
    "+": "\u208a", "-": "\u208b", "\u2212": "\u208b", "=": "\u208c",
    "(": "\u208d", ")": "\u208e", "a": "\u2090", "e": "\u2091", "h": "\u2095",
    "i": "\u1d62", "j": "\u2c7c", "k": "\u2096", "l": "\u2097", "m": "\u2098",
    "n": "\u2099", "o": "\u2092", "p": "\u209a", "r": "\u1d63", "s": "\u209b",
    "t": "\u209c", "u": "\u1d64", "v": "\u1d65", "x": "\u2093",
}


def _en_script(contenu, table):
    """Traduit un exposant/indice en caracteres Unicode, ou None si impossible.

    Passer par l'Unicode evite les balises <super>/<sub> de reportlab, dont le
    placement deraille dans les paragraphes de plusieurs lignes (l'indice se
    retrouve rejete en fin de ligne).
    """
    sortie = []
    for caractere in contenu:
        if caractere not in table:
            return None
        sortie.append(table[caractere])
    return "".join(sortie)


def _scriptes(texte):
    """Remplace ^{...} et _{...} par des caracteres Unicode ou des balises."""
    for motif, table, balise, montee in (
        (r"\^\{([^{}]*)\}", TAB_SUP, "super", "3.0"),
        (r"_\{([^{}]*)\}", TAB_SUB, "sub", None),
    ):
        while True:
            trouve = re.search(motif, texte)
            if not trouve:
                break
            contenu = trouve.group(1)
            traduit = _en_script(contenu, table)
            if traduit is None:                       # repli : petite police
                if montee is None:
                    remplacement = '<font size="6.4">%s</font>' % contenu
                else:
                    remplacement = '<super size="6.4" rise="%s">%s</super>' % (
                        montee, contenu)
            else:
                remplacement = traduit
            texte = texte[:trouve.start()] + remplacement + texte[trouve.end():]
    return texte


def enrichi(texte):
    """Convertit le balisage en ligne d'un paragraphe en balises reportlab."""
    morceaux = []

    def garde(m):
        morceaux.append(m.group(1))
        return "\x00%d\x00" % (len(morceaux) - 1)

    texte = re.sub(r"`([^`]+)`", garde, texte)
    texte = _echappe(texte)
    texte = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texte)
    texte = re.sub(r"\*([^*\n]+?)\*", r"<i>\1</i>", texte)
    texte = _scriptes(texte)
    # typographie francaise : espaces insecables (avant : et autour des guillemets)
    texte = texte.replace(" :", "&#160;:").replace(" ;", "&#160;;")
    texte = texte.replace("&lt;&lt; ", "«&#160;").replace(" »", "&#160;»")

    def rend_code(m):
        code = _echappe(morceaux[int(m.group(1))])
        if len(code) <= 26:                 # un identifiant court ne se coupe pas
            code = code.replace(" ", "&#160;")
        return ('<font name="DejaVuMono" size="8.3" color="#0b4f6c">%s</font>' % code)

    return re.sub("\x00(\\d+)\x00", rend_code, texte)


# ---------------------------------------------------------------------------
# Analyse du Markdown
# ---------------------------------------------------------------------------
class Bloc:
    """Bloc elementaire du document : type, contenu, parametres."""

    def __init__(self, genre, contenu="", **options):
        self.genre = genre
        self.contenu = contenu
        self.options = options

    def __getattr__(self, nom):
        # les options sont accessibles comme des attributs (bloc.titre, ...)
        try:
            return self.__dict__["options"][nom]
        except KeyError:
            raise AttributeError(nom)


def lit_entete(lignes):
    """Extrait le bloc YAML de tete et renvoie (metadonnees, reste)."""
    meta = {}
    if not lignes or lignes[0].strip() != "---":
        return meta, lignes
    for i in range(1, len(lignes)):
        ligne = lignes[i].strip()
        if ligne == "---":
            return meta, lignes[i + 1:]
        if ":" in ligne:
            cle, valeur = ligne.split(":", 1)
            meta[cle.strip()] = valeur.strip()
    return meta, lignes


def decoupe_tableau(ligne):
    """Decoupe une ligne de tableau en cellules."""
    ligne = ligne.strip()
    if ligne.startswith("|"):
        ligne = ligne[1:]
    if ligne.endswith("|"):
        ligne = ligne[:-1]
    return [c.strip() for c in ligne.split("|")]


def analyse(texte):
    """Transforme le Markdown en une liste de Bloc."""
    lignes = texte.split("\n")
    meta, lignes = lit_entete(lignes)
    blocs = []
    i = 0
    while i < len(lignes):
        ligne = lignes[i]
        depouillee = ligne.strip()

        if not depouillee:
            i += 1
            continue

        if depouillee.startswith("<!--"):
            instruction = depouillee.strip("<>!- ")
            if instruction.startswith("toc"):
                blocs.append(Bloc("toc"))
            elif instruction.startswith("pagebreak"):
                blocs.append(Bloc("saut"))
            i += 1
            continue

        if depouillee.startswith("```"):
            langage = depouillee[3:].strip()
            i += 1
            code = []
            while i < len(lignes) and not lignes[i].strip().startswith("```"):
                code.append(lignes[i])
                i += 1
            i += 1
            blocs.append(Bloc("code", "\n".join(code), langage=langage))
            continue

        if depouillee.startswith("::: "):
            titre = depouillee[4:].strip()
            i += 1
            interieur = []
            while i < len(lignes) and lignes[i].strip() != ":::":
                interieur.append(lignes[i])
                i += 1
            i += 1
            blocs.append(Bloc("encadre", analyse("\n".join(interieur))[1], titre=titre))
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", depouillee)
        if m:
            niveau = len(m.group(1))
            if niveau <= 3:
                blocs.append(Bloc("titre", m.group(2), niveau=niveau))
            else:
                blocs.append(Bloc("sous-titre", m.group(2)))
            i += 1
            continue

        if depouillee.startswith("> "):
            citation = []
            while i < len(lignes) and lignes[i].strip().startswith("> "):
                citation.append(lignes[i].strip()[2:])
                i += 1
            blocs.append(Bloc("citation", " ".join(citation)))
            continue

        if re.match(r"^[-*]\s+", depouillee):
            elements = []
            while i < len(lignes) and re.match(r"^[-*]\s+", lignes[i].strip()):
                elements.append(re.sub(r"^[-*]\s+", "", lignes[i].strip()))
                i += 1
            blocs.append(Bloc("liste", elements, puce="•"))
            continue

        if re.match(r"^\d+[.)]\s+", depouillee):
            elements = []
            numeros = []
            while i < len(lignes) and re.match(r"^\d+[.)]\s+", lignes[i].strip()):
                brut = lignes[i].strip()
                numeros.append(re.match(r"^(\d+)[.)]", brut).group(1) + ".")
                elements.append(re.sub(r"^\d+[.)]\s+", "", brut))
                i += 1
            blocs.append(Bloc("liste", elements, puces=numeros))
            continue

        if depouillee.startswith("|") and i + 1 < len(lignes) and \
                re.match(r"^\|[\s:\-|]+\|$", lignes[i + 1].strip()):
            entete = decoupe_tableau(lignes[i])
            separateur = decoupe_tableau(lignes[i + 1])
            alignements = []
            for cellule in separateur:
                if cellule.startswith(":") and cellule.endswith(":"):
                    alignements.append("CENTRE")
                elif cellule.endswith(":"):
                    alignements.append("DROITE")
                else:
                    alignements.append("GAUCHE")
            i += 2
            corps = []
            while i < len(lignes) and lignes[i].strip().startswith("|"):
                corps.append(decoupe_tableau(lignes[i]))
                i += 1
            blocs.append(Bloc("tableau", corps, entete=entete, alignements=alignements))
            continue

        if depouillee.startswith("---") and len(depouillee) <= 4:
            blocs.append(Bloc("filet"))
            i += 1
            continue

        # paragraphe : lignes consecutives jusqu'a une ligne vide ou speciale
        paragraphe = []
        while i < len(lignes):
            brut = lignes[i]
            test = brut.strip()
            if (not test or test.startswith("#") or test.startswith("```")
                    or test.startswith("::: ") or test == ":::"
                    or test.startswith("<!--") or test.startswith("> ")
                    or re.match(r"^[-*]\s+", test) or re.match(r"^\d+[.)]\s+", test)
                    or test.startswith("|")):
                break
            paragraphe.append(test)
            i += 1
        blocs.append(Bloc("paragraphe", " ".join(paragraphe)))
    return meta, blocs


# ---------------------------------------------------------------------------
# Rendu des blocs en flowables
# ---------------------------------------------------------------------------
class Rendu:
    """Construit les flowables reportlab a partir des blocs analyses."""

    def __init__(self, styles, largeur):
        self.s = styles
        self.largeur = largeur
        self.titres = []          # (niveau, texte) pour la table des matieres
        self.imbrique = 0         # > 0 lorsque l'on rend l'interieur d'un encadre

    # -- inline -----------------------------------------------------------
    def p(self, texte, style="corps"):
        return Paragraph(enrichi(texte), self.s[style])

    # -- blocs ------------------------------------------------------------
    def rendre(self, blocs):
        flot = []
        i = 0
        while i < len(blocs):
            bloc = blocs[i]
            suivant = blocs[i + 1] if i + 1 < len(blocs) else None
            # un titre suivi d'un petit tableau ne se detache pas de lui
            if (bloc.genre == "titre" and suivant is not None
                    and suivant.genre == "tableau" and len(suivant.contenu) <= 9
                    and not self.imbrique):
                flot.append(KeepTogether(self._titre_seul(bloc)
                                         + self.bloc_tableau(suivant)))
                i += 2
                continue
            methode = getattr(self, "bloc_" + bloc.genre, None)
            if methode is None:
                flot.append(self.p(str(bloc.contenu)))
            else:
                flot.extend(methode(bloc))
            i += 1
        return flot

    def bloc_paragraphe(self, bloc):
        return [self.p(bloc.contenu)]

    def bloc_sous_titre(self, bloc):
        return [self.p(bloc.contenu, "h3")]

    def _titre_seul(self, bloc):
        """Flowables d'un titre, sans saut de page conditionnel."""
        niveau = bloc.options["niveau"]
        style = "h1" if niveau == 1 else ("h2" if niveau == 2 else "h3")
        paragraphe = self.p(bloc.contenu, style)
        paragraphe._toc = (niveau, re.sub(r"<[^>]+>", "", enrichi(bloc.contenu)))
        self.titres.append((niveau, bloc.contenu))
        flot = [paragraphe]
        if niveau == 1:
            flot.append(HRFlowable(
                width="100%", thickness=1.4, color=ACCENT,
                spaceBefore=1, spaceAfter=9, hAlign="LEFT",
            ))
        return flot

    def bloc_titre(self, bloc):
        # un titre ne doit pas rester seul en bas de page
        marge = 110 if bloc.options["niveau"] == 1 else 78
        return [CondPageBreak(marge)] + self._titre_seul(bloc)

    def bloc_filet(self, bloc):
        return [HRFlowable(width="100%", thickness=0.6, color=GRIS_CLAIR,
                           spaceBefore=6, spaceAfter=6)]

    def bloc_citation(self, bloc):
        if self.imbrique:
            return [Paragraph(enrichi(bloc.contenu), self.s["citation_imbriquee"])]
        tableau = Table([[self.p(bloc.contenu, "citation")]],
                        colWidths=[self.largeur])
        tableau.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f6f8")),
            ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return [Spacer(1, 1), tableau, Spacer(1, 7)]

    def bloc_liste(self, bloc):
        flot = []
        puces = bloc.options.get("puces") or \
            [bloc.options.get("puce", "•")] * len(bloc.contenu)
        for puce, element in zip(puces, bloc.contenu):
            flot.append(Paragraph(enrichi(element), self.s["liste"], bulletText=puce))
        flot.append(Spacer(1, 3))
        return flot

    def bloc_code(self, bloc):
        """Bloc de code : une rangee par ligne, pour permettre les sauts de page."""
        lignes = bloc.contenu.split("\n")
        while lignes and not lignes[-1].strip():
            lignes.pop()
        if not lignes:
            return []

        largeur_max = 96
        enveloppees = []
        for ligne in lignes:
            ligne = ligne.replace("\t", "    ")
            if len(ligne) <= largeur_max:
                enveloppees.append(ligne)
            else:
                marge = len(ligne) - len(ligne.lstrip())
                enveloppees.extend(textwrap.wrap(
                    ligne, largeur_max, subsequent_indent=" " * (marge + 8),
                    break_long_words=True, break_on_hyphens=False,
                ) or [""])

        rangees = []
        for ligne in enveloppees:
            if ligne.strip():
                # les espaces sont rendus insecables pour garder l'alignement
                texte = _echappe(ligne).replace(" ", "&#160;")
            else:
                texte = "&#160;"
            rangees.append([Paragraph(texte, self.s["code"])])

        tableau = Table(rangees, colWidths=[self.largeur], repeatRows=0)
        tableau.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), FOND_CODE),
            ("LINEBEFORE", (0, 0), (0, -1), 2.4, ACCENT),
            ("LINEBELOW", (0, -1), (-1, -1), 0.4, BORD_CODE),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 1.1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.1),
            ("TOPPADDING", (0, 0), (-1, 0), 5.5),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return [tableau, Spacer(1, 7)]

    def bloc_tableau(self, bloc):
        entete = bloc.options["entete"]
        alignements = bloc.options["alignements"]
        while len(alignements) < len(entete):
            alignements.append("GAUCHE")

        def cellule(texte, style="cellule"):
            return Paragraph(enrichi(texte), self.s[style])

        donnees = [[cellule(c, "cellule_entete") for c in entete]]
        for ligne in bloc.contenu:
            ligne = list(ligne) + [""] * (len(entete) - len(ligne))
            donnees.append([cellule(c) for c in ligne[:len(entete)]])

        # largeur des colonnes : mesure reelle du texte, puis mise a l'echelle
        colonnes = len(entete)
        naturelles, minimales = [], []
        for k in range(colonnes):
            cellules = [entete[k]] + [l[k] for l in bloc.contenu if k < len(l)]
            naturelles.append(max(_mesure(c, gras=(j == 0)) for j, c in enumerate(cellules)) + 11)
            minimales.append(max(max(_mesure(mot), _mesure(mot, gras=True))
                                 for c in cellules for mot in c.split()) + 10)
        if sum(minimales) > self.largeur:                # cas pathologique
            facteur = self.largeur / sum(minimales)
            minimales = [m * facteur for m in minimales]
        reste = self.largeur - sum(minimales)
        souples = [max(n - m, 1.0) for n, m in zip(naturelles, minimales)]
        total_souple = sum(souples)
        largeurs = [m + reste * x / total_souple for m, x in zip(minimales, souples)]

        tableau = Table(donnees, colWidths=largeurs, repeatRows=1, hAlign="LEFT")
        commandes = [
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dbe2e8")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8d2da")),
        ]
        for k, alignement in enumerate(alignements):
            if alignement == "CENTRE":
                commandes.append(("ALIGN", (k, 0), (k, -1), "CENTER"))
            elif alignement == "DROITE":
                commandes.append(("ALIGN", (k, 0), (k, -1), "RIGHT"))
        for k in range(1, len(donnees)):
            if k % 2 == 0:
                commandes.append(("BACKGROUND", (0, k), (-1, k), colors.HexColor("#f6f8fa")))
        tableau.setStyle(TableStyle(commandes))
        # un KeepTogether dans une cellule d'encadre ne peut pas se scinder :
        # on ne l'utilise qu'au premier niveau.
        if len(donnees) <= 9 and not self.imbrique:
            return [KeepTogether([tableau, Spacer(1, 8)])]
        return [tableau, Spacer(1, 8)]

    def bloc_encadre(self, bloc):
        titre = bloc.titre
        self.largeur -= 21          # marges internes de l'encadre
        self.imbrique += 1
        try:
            interieur = self.rendre(bloc.contenu)
        finally:
            self.imbrique -= 1
            self.largeur += 21
        if not interieur:
            return []
        if titre.lower().startswith("énoncé") or titre.lower().startswith("enonce"):
            fond, bord, couleur_titre = FOND_ENONCE, BORD_ENONCE, GRIS
        elif titre.lower().startswith("réponse") or titre.lower().startswith("reponse"):
            fond, bord, couleur_titre = colors.HexColor("#f1f7fc"), ACCENT, ACCENT
        else:
            fond, bord, couleur_titre = colors.HexColor("#f2faf8"), ACCENT_2, ACCENT_2

        style_titre = ParagraphStyle(
            "tt_" + titre[:6], parent=self.s["titre_encadre"], textColor=couleur_titre,
        )
        lignes = [[Paragraph(enrichi(titre.upper()), style_titre)]]
        for f in interieur:
            lignes.append([f])
        tableau = Table(lignes, colWidths=[self.largeur - 2])
        tableau.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), fond),
            ("LINEBEFORE", (0, 0), (0, -1), 2.8, bord),
            ("LEFTPADDING", (0, 0), (-1, -1), 11),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 7),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 1.6),
            ("BOTTOMPADDING", (0, 0), (-1, -2), 1.6),
        ]))
        # evite qu'un encadre commence en bas de page avec son seul titre
        return [CondPageBreak(76), Spacer(1, 1), tableau, Spacer(1, 8)]

    def bloc_saut(self, bloc):
        return [PageBreak()]

    def bloc_toc(self, bloc):
        """Le sommaire est insere globalement, apres la couverture."""
        return []


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------
class Document(BaseDocTemplate):
    """Document A4 avec en-tete, pied de page, signets et releve des titres."""

    def __init__(self, chemin, meta, **kwargs):
        BaseDocTemplate.__init__(
            self, chemin, pagesize=A4,
            leftMargin=21 * mm, rightMargin=19 * mm,
            topMargin=26 * mm, bottomMargin=20 * mm,
            title=meta.get("title", "Compte-rendu"),
            author=meta.get("author", ""),
            subject=meta.get("subtitle", ""),
            **kwargs
        )
        self.meta = meta
        self.releve = []      # (niveau, texte, page)
        cadre = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height, id="corps",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        self.addPageTemplates([
            PageTemplate(id="couverture", frames=[cadre], onPage=self.decore_couverture),
            PageTemplate(id="corps", frames=[cadre], onPage=self.decore_page),
        ])

    # -- habillage --------------------------------------------------------
    def decore_couverture(self, canevas, doc):
        largeur, hauteur = A4
        canevas.saveState()
        canevas.setFillColor(ACCENT)
        canevas.rect(0, hauteur - 98 * mm, largeur, 98 * mm, stroke=0, fill=1)
        canevas.setFillColor(ACCENT_2)
        canevas.rect(0, hauteur - 98 * mm, largeur, 2.6 * mm, stroke=0, fill=1)
        canevas.setFillColor(colors.HexColor("#0b1d2c"))
        canevas.rect(0, 0, largeur, 16 * mm, stroke=0, fill=1)
        canevas.setFont("DejaVu", 7.6)
        canevas.setFillColor(colors.HexColor("#9fb4c6"))
        canevas.drawString(self.leftMargin, 6.5 * mm,
                           "Compte-rendu de travaux pratiques · Cryptographie R309")
        canevas.drawRightString(largeur - self.rightMargin, 6.5 * mm,
                                "hamming.py · test-hamming.py · verification.py")
        canevas.restoreState()

    def decore_page(self, canevas, doc):
        largeur, hauteur = A4
        canevas.saveState()
        canevas.setFont("DejaVu", 7.4)
        canevas.setFillColor(GRIS)
        canevas.drawString(self.leftMargin, hauteur - 15 * mm,
                           "%s — %s" % (self.meta.get("cours", ""),
                                        self.meta.get("title", "")))
        canevas.drawRightString(largeur - self.rightMargin, hauteur - 15 * mm,
                                self.meta.get("author", ""))
        canevas.setStrokeColor(GRIS_CLAIR)
        canevas.setLineWidth(0.7)
        canevas.line(self.leftMargin, hauteur - 17.5 * mm,
                     largeur - self.rightMargin, hauteur - 17.5 * mm)
        canevas.setFont("DejaVu", 7.6)
        canevas.setFillColor(GRIS)
        canevas.drawString(self.leftMargin, 11 * mm,
                           "%s · %s" % (self.meta.get("classe", ""),
                                        self.meta.get("date", "")))
        canevas.restoreState()

    def afterFlowable(self, flowable):
        infos = getattr(flowable, "_toc", None)
        if infos:
            niveau, texte = infos
            page = self.page
            cle = "sec%d" % len(self.releve)
            self.canv.bookmarkPage(cle)
            self.canv.addOutlineEntry(texte, cle, niveau - 1, 0)
            self.releve.append((niveau, texte, page))


class Canevas(pdfcanvas.Canvas):
    """Canevas qui ecrit « page X / Y » dans le pied de page."""

    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._etats = []

    def showPage(self):
        self._etats.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._etats)
        for etat in self._etats:
            self.__dict__.update(etat)
            self._dessine_total(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _dessine_total(self, total):
        if self._pageNumber <= 1:
            return
        largeur, _ = A4
        self.saveState()
        self.setFont("DejaVu", 7.6)
        self.setFillColor(GRIS)
        self.drawRightString(largeur - self._rightMarginM, 11 * mm,
                             "%d / %d" % (self._pageNumber, total))
        self.restoreState()

    _rightMarginM = 19 * mm


# ---------------------------------------------------------------------------
# Couverture et table des matieres
# ---------------------------------------------------------------------------
def page_de_garde(meta, styles):
    """Contenu de la premiere page."""
    flot = []
    flot.append(Spacer(1, 6 * mm))
    flot.append(Paragraph(enrichi(meta.get("cours", "")), styles["couverture_sur"]))
    flot.append(Spacer(1, 3 * mm))
    flot.append(Paragraph(enrichi(meta.get("title", "")), styles["couverture_titre"]))
    flot.append(Spacer(1, 2.5 * mm))
    flot.append(Paragraph(enrichi(meta.get("subtitle", "")), styles["couverture_sous"]))
    flot.append(Spacer(1, 34 * mm))
    flot.append(Paragraph(
        enrichi("Coder un message en un mot de code de 2^{n} bits, calculer les bits de contrôle "
        "par XOR, décoder en localisant l'erreur grâce au syndrome, puis étendre le code "
        "par un bit de parité pour détecter les erreurs doubles : les treize questions du "
        "sujet sont traitées, expliquées et vérifiées par le script de test fourni."),
        ParagraphStyle("chapeau", fontName="DejaVuSerif", fontSize=10, leading=15,
                       textColor=colors.HexColor("#2f3e4c")),
    ))
    flot.append(Spacer(1, 16 * mm))

    # frise du mot de code de l'enonce : positions de controle en bleu
    code = [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1]
    controle = {0, 1, 2, 4, 8}
    cellule = 9.4 * mm
    donnees = [[Paragraph(
        '<font name="DejaVuMono-Bold" size="11" color="%s">%d</font>'
        % ("#ffffff" if i in controle else "#12263a", code[i]),
        ParagraphStyle("bit", alignment=TA_CENTER, fontSize=11, leading=13),
    ) for i in range(16)]]
    frise = Table(donnees, colWidths=[cellule] * 16)
    commandes = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("INNERGRID", (0, 0), (-1, -1), 0.8, colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.white),
    ]
    for i in range(16):
        if i in controle:
            commandes.append(("BACKGROUND", (i, 0), (i, 0), ACCENT))
        else:
            commandes.append(("BACKGROUND", (i, 0), (i, 0), colors.HexColor("#eef2f6")))
    frise.setStyle(TableStyle(commandes))
    flot.append(frise)
    flot.append(Spacer(1, 4 * mm))
    flot.append(Paragraph(
        "Un mot de code de l'énoncé (n = 4) : les positions de contrôle 0, 1, 2, 4 et 8 "
        "sont en bleu, les onze bits du message occupent les autres positions.",
        ParagraphStyle("legende", fontName="DejaVu", fontSize=8.4, leading=12,
                       textColor=GRIS),
    ))

    meta_donnees = [
        ["Auteur", meta.get("author", ""), "Classe", meta.get("classe", "")],
        ["Date", meta.get("date", ""), "Fichiers", meta.get("fichiers", "")],
    ]
    style_cle = ParagraphStyle("cle", fontName="DejaVu-Bold", fontSize=8.4,
                               leading=12, textColor=GRIS)
    style_val = ParagraphStyle("val", fontName="DejaVu", fontSize=8.8,
                               leading=12, textColor=ENCRE)
    tableau = Table(
        [[Paragraph(c, style_cle if k % 2 == 0 else style_val) for k, c in enumerate(ligne)]
         for ligne in meta_donnees],
        colWidths=[20 * mm, 55 * mm, 20 * mm, 68 * mm],
    )
    tableau.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, GRIS_CLAIR),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    flot.append(Spacer(1, 8 * mm))
    flot.append(tableau)
    flot.append(Spacer(1, 7 * mm))
    flot.append(Paragraph(
        '<font name="DejaVu-Bold" size="9" color="#0f766e">13 / 13</font>'
        '<font size="9" color="#5b6773"> fonctions validées par test-hamming.py</font>',
        ParagraphStyle("badge", fontName="DejaVu", fontSize=9, leading=13),
    ))
    flot.append(NextPageTemplate("corps"))
    flot.append(PageBreak())
    return flot


def table_des_matieres(titres, pages, styles, largeur):
    """Construit la table des matieres a partir des titres releves."""
    flot = [Paragraph("Sommaire", styles["h1"]),
            HRFlowable(width="100%", thickness=1.4, color=ACCENT,
                       spaceBefore=1, spaceAfter=10, hAlign="LEFT")]
    lignes = []
    for k, (niveau, texte) in enumerate(titres):
        if niveau > 2:
            continue
        numero = pages.get(k, "")
        lignes.append([
            Paragraph(enrichi(re.sub(r"\*\*", "", texte)),
                      styles["toc1"] if niveau == 1 else styles["toc2"]),
            Paragraph('<font color="#1a4f7a">%s</font>' % numero, styles["toc_page"]),
        ])
    tableau = Table(lignes, colWidths=[largeur - 16 * mm, 16 * mm])
    tableau.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#eaeef2")),
    ]))
    flot.append(tableau)
    flot.append(PageBreak())
    return flot


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------
def construit(meta, blocs, chemin, styles, pages=None):
    """Construit une fois le PDF ; renvoie le releve des titres."""
    doc = Document(chemin, meta)
    rendu = Rendu(styles, doc.width)
    corps = rendu.rendre(blocs)

    # remplacement de la marque de sommaire
    pages = pages or {}
    sommaire = []
    if any(b.genre == "toc" for b in blocs):
        sommaire = table_des_matieres(
            rendu.titres, pages, styles, doc.width,
        )

    flot = page_de_garde(meta, styles)
    if sommaire:
        flot.extend(sommaire)
    flot.extend(corps)

    doc.build(flot, canvasmaker=Canevas)
    return rendu.titres, doc.releve


def convertit(md_path, pdf_path, racine=None):
    """Convertit un fichier Markdown en PDF, avec sommaire pagine."""
    with open(md_path, encoding="utf-8") as f:
        texte = f.read()

    racine = racine or os.path.dirname(os.path.abspath(md_path))
    texte = texte.replace("{{CODE}}", _lire(os.path.join(racine, "hamming.py")).rstrip())
    texte = texte.replace("{{TRACE}}", _lire(
        os.path.join(racine, "resultats-verification.txt")).rstrip())

    enregistre_polices()
    styles = fabrique_styles()
    meta, blocs = analyse(texte)

    # deux passes : la premiere releve les pages, la seconde les affiche
    titres, releve = construit(meta, blocs, pdf_path, styles)
    pages = {k: p for k, (_, _, p) in enumerate(releve)}
    _, releve = construit(meta, blocs, pdf_path, styles, pages)
    pages_2 = {k: p for k, (_, _, p) in enumerate(releve)}
    if pages_2 != pages:
        construit(meta, blocs, pdf_path, styles, pages_2)
    return pdf_path


def _lire(chemin):
    if not os.path.exists(chemin):
        return "(fichier %s introuvable)" % os.path.basename(chemin)
    with open(chemin, encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "responses.md"
    cible = sys.argv[2] if len(sys.argv) > 2 else "rendu.pdf"
    convertit(source, cible)
    print("PDF écrit :", cible)

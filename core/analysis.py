"""
Génère, pour une fiche (lead) donnée :
 - une analyse commerciale avec conseils (analyse_lead)
 - une lettre de prospection par email, écrite naturellement, personnalisée
   (generer_lettre)

Tout est basé sur des règles + templates locaux (pas d'appel à une API
externe), donc ça fonctionne hors-ligne et instantanément.
"""

import random


def _to_float(value, default=0.0):
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return default


def _to_int(value, default=0):
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return default


def analyser_lead(data: dict) -> str:
    """
    data attend les clés : name, category, phone, email, address, wilaya,
    country, has_website, rating, reviews_count, status
    Retourne un texte d'analyse en français avec des conseils concrets.
    """
    name = data.get("name") or "Cette entreprise"
    category = data.get("category") or "activité non précisée"
    rating = _to_float(data.get("rating"))
    reviews = _to_int(data.get("reviews_count"))
    has_website = bool(data.get("has_website"))
    phone = data.get("phone") or ""
    email = data.get("email") or ""
    wilaya = data.get("wilaya") or ""
    country = data.get("country") or ""

    lines = []
    lines.append(f"Analyse du prospect : {name} ({category}) — {wilaya}, {country}")
    lines.append("")

    # --- Score d'opportunité ---
    score = 0
    reasons = []

    if not has_website:
        score += 40
        reasons.append("Aucun site web détecté → besoin potentiel clair.")
    else:
        score -= 20
        reasons.append("Un site web existe déjà → prospect moins prioritaire, "
                        "sauf si le site est ancien ou de mauvaise qualité (à vérifier).")

    if reviews >= 50:
        score += 25
        reasons.append(f"{reviews} avis Google → établissement avec une clientèle réelle "
                        "et un volume d'activité suffisant pour justifier un investissement digital.")
    elif reviews >= 10:
        score += 12
        reasons.append(f"{reviews} avis → activité établie mais encore modeste.")
    else:
        reasons.append("Peu ou pas d'avis → activité peut-être récente ou à faible visibilité, "
                        "un site web pourrait justement l'aider à se développer.")

    if rating >= 4.0:
        score += 15
        reasons.append(f"Note moyenne de {rating}/5 → bonne réputation, argument de vente "
                        "à mettre en avant sur un futur site (avis clients, réassurance).")
    elif rating > 0:
        reasons.append(f"Note de {rating}/5 → à mentionner avec prudence, ou proposer une page "
                        "'avis clients' modérée sur le futur site.")

    if phone:
        score += 10
        reasons.append("Numéro de téléphone disponible → contact direct possible (appel ou WhatsApp).")
    if email:
        score += 10
        reasons.append("Email disponible → prise de contact par écrit facilitée.")
    if not phone and not email:
        reasons.append("⚠ Aucun contact direct trouvé → il faudra passer par l'adresse physique "
                        "ou les réseaux sociaux de l'entreprise.")

    score = max(0, min(100, score))

    if score >= 70:
        niveau = "🔥 Prospect PRIORITAIRE"
    elif score >= 40:
        niveau = "🟠 Prospect INTÉRESSANT"
    else:
        niveau = "⚪ Prospect SECONDAIRE"

    lines.append(f"Score d'opportunité estimé : {score}/100 — {niveau}")
    lines.append("")
    lines.append("Points d'analyse :")
    for r in reasons:
        lines.append(f" • {r}")

    lines.append("")
    lines.append("Recommandations :")
    if not has_website:
        lines.append(" • Proposer un site vitrine simple (présentation, coordonnées, "
                      "galerie photos, avis clients) comme premier pas, avant une éventuelle "
                      "boutique en ligne.")
        lines.append(" • Mettre en avant le référencement local (être visible sur Google "
                      "quand un client cherche ce type d'activité dans la wilaya).")
    else:
        lines.append(" • Vérifier la qualité et l'ancienneté du site actuel avant de démarcher "
                      "(vitesse de chargement, version mobile, dernière mise à jour).")

    if reviews >= 10:
        lines.append(" • Utiliser les avis existants comme preuve sociale dans l'argumentaire "
                      "commercial et sur le futur site.")

    contact = phone or email or "l'adresse physique de l'établissement"
    lines.append(f" • Premier contact recommandé via : {contact}.")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# Génération de lettre de prospection (email)
# ---------------------------------------------------------------------

_OUVERTURES = [
    "Bonjour,\n\nJe me permets de vous contacter après être tombé(e) sur la fiche Google Maps de {name}.",
    "Bonjour,\n\nEn recherchant les {category_lower} à {wilaya}, je suis tombé(e) sur {name} — "
    "et je voulais vous écrire directement.",
    "Bonjour,\n\nJ'espère que vous allez bien. Je travaille dans la création de sites web pour "
    "des commerces locaux, et {name} a attiré mon attention.",
]

_CONSTATS_AVEC_AVIS = [
    "J'ai vu que vous aviez déjà {reviews} avis sur Google avec une note de {rating}/5 — "
    "c'est vraiment une belle base de clients satisfaits.",
    "Avec {reviews} avis et {rating}/5 de moyenne, on sent que {name} a déjà une clientèle fidèle.",
]

_CONSTATS_SANS_SITE = [
    "Par contre, je n'ai trouvé aucun site internet officiel pour votre établissement.",
    "En revanche, je n'ai pas trouvé de site web à votre nom — seulement votre fiche Google Maps.",
    "J'ai remarqué que vous n'aviez pas encore de site internet.",
]

_PROPOSITIONS = [
    "Aujourd'hui, la plupart des clients regardent en ligne avant de se déplacer : un site simple "
    "et professionnel (présentation, photos, horaires, avis, contact direct) peut vraiment faire "
    "la différence et vous amener plus de monde.",
    "Un site web, même simple, permet souvent d'être trouvé plus facilement sur Google et de "
    "rassurer les nouveaux clients avant même qu'ils ne poussent la porte.",
    "Je pense qu'un site vitrine bien fait pourrait vous aider à convertir les gens qui vous "
    "trouvent sur Maps mais hésitent encore à venir.",
]

_OFFRES = [
    "Je propose justement la création de sites vitrines modernes, adaptés mobile, pour des "
    "commerces comme le vôtre — livrés rapidement et à un tarif raisonnable.",
    "C'est exactement le genre de projet que j'aime accompagner : un site rapide à mettre en "
    "ligne, à votre image, sans complexité inutile.",
    "Je peux vous proposer un site simple, clair, avec vos coordonnées et vos avis mis en avant, "
    "prêt en quelques jours.",
]

_CLOTURES = [
    "Seriez-vous disponible pour un court échange (5-10 minutes) cette semaine, par téléphone ou "
    "en message, pour en discuter sans engagement ?",
    "Si ça vous intéresse, je peux vous envoyer 2-3 exemples de réalisations similaires — "
    "dites-moi simplement si vous êtes ouvert(e) à en discuter.",
    "N'hésitez pas à me dire si vous voulez en parler, même juste pour avoir un avis extérieur "
    "sur votre visibilité actuelle.",
]

_SIGNATURES = [
    "Bonne journée,\n{signataire}",
    "Merci pour votre temps,\n{signataire}",
    "Au plaisir d'échanger,\n{signataire}",
]


def generer_lettre(data: dict, signataire: str = "Salim") -> str:
    """
    Génère une lettre/email de prospection personnalisée pour ce lead,
    avec une formulation naturelle (variée à chaque génération).
    """
    name = data.get("name") or "votre établissement"
    category = data.get("category") or "commerce"
    wilaya = data.get("wilaya") or ""
    rating = data.get("rating") or ""
    reviews = data.get("reviews_count") or ""
    has_website = bool(data.get("has_website"))

    ctx = {
        "name": name,
        "category_lower": category.lower(),
        "wilaya": wilaya,
        "rating": rating,
        "reviews": reviews,
        "signataire": signataire,
    }

    parts = []
    parts.append(random.choice(_OUVERTURES).format(**ctx))

    if reviews and _to_int(reviews) >= 5 and rating:
        parts.append(random.choice(_CONSTATS_AVEC_AVIS).format(**ctx))

    if not has_website:
        parts.append(random.choice(_CONSTATS_SANS_SITE).format(**ctx))

    parts.append(random.choice(_PROPOSITIONS).format(**ctx))
    parts.append(random.choice(_OFFRES).format(**ctx))
    parts.append(random.choice(_CLOTURES).format(**ctx))
    parts.append(random.choice(_SIGNATURES).format(**ctx))

    return "\n\n".join(parts)

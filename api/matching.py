"""
Motor de coincidencias SkillMatch.

Calcula un score entre 0 y 100 comparando las habilidades de un perfil
con los requisitos de una oportunidad.
"""

EXPERIENCE_ORDER = {"junior": 1, "mid": 2, "senior": 3}


def compute_match_score(profile, opportunity):
    """
    Ponderación:
      - 70% habilidades (nivel del usuario vs nivel requerido, ponderado por importancia)
      - 15% experiencia (junior/mid/senior)
      - 15% ubicación / modalidad
    """
    opp_skills = list(opportunity.opportunityskill_set.select_related("skill").all())
    if not opp_skills:
        return 0.0

    profile_skills = {
        ps.skill_id: ps for ps in profile.profileskill_set.all()
    }

    # --- 1) Habilidades ---
    total_weight = sum(os.weight for os in opp_skills) or 1
    skills_score = 0.0
    for os in opp_skills:
        ps = profile_skills.get(os.skill_id)
        if not ps:
            continue
        # ratio entre nivel del usuario y nivel mínimo requerido
        ratio = min(ps.level / max(opportunity.min_skill_level, 1), 1.0)
        skills_score += ratio * os.weight
    skills_score = (skills_score / total_weight) * 70.0

    # --- 2) Experiencia ---
    user_exp = EXPERIENCE_ORDER.get(profile.experience_level, 1)
    req_exp = EXPERIENCE_ORDER.get(opportunity.experience_level, 1)
    if user_exp >= req_exp:
        exp_score = 15.0
    else:
        exp_score = 15.0 * (user_exp / req_exp)

    # --- 3) Ubicación / modalidad ---
    loc_score = 0.0
    if opportunity.modality == "remote":
        loc_score = 15.0
    elif profile.location and opportunity.location:
        if profile.location.strip().lower() == opportunity.location.strip().lower():
            loc_score = 15.0
        else:
            loc_score = 5.0
    else:
        loc_score = 7.5

    return round(skills_score + exp_score + loc_score, 2)


def rank_opportunities(profile, opportunities):
    """Devuelve lista de (opportunity, score) ordenada de mayor a menor."""
    ranked = [(op, compute_match_score(profile, op)) for op in opportunities]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
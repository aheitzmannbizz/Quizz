import copy
import json
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


QUESTIONS_PATH = Path("data/questions_fr.json")


def is_grade_question(q: dict) -> bool:
    return bool(q.get("is_grade")) or q.get("chapter") == "Grades"


def is_famas_question(q: dict) -> bool:
    haystack = " ".join(
        [
            str(q.get("chapter", "")),
            str(q.get("question", "")),
            str(q.get("explanation", "")),
            str(q.get("source", "")),
        ]
    ).lower()
    return "famas" in haystack


def is_nato_question(q: dict) -> bool:
    return q.get("chapter") == "OTAN"


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Source+Sans+3:wght@400;600;700&display=swap');

        :root {
            --fr-blue: #0f2d4f;
            --fr-red: #8b1e2d;
            --army-900: #1a2117;
            --army-800: #242e1f;
            --army-700: #3f4f36;
            --army-500: #6b7a5b;
            --army-200: #dbe3d1;
            --paper: #f4f1e8;
            --ink: #1f221b;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(15, 45, 79, 0.12), transparent 30%),
                radial-gradient(circle at 88% 6%, rgba(139, 30, 45, 0.10), transparent 28%),
                linear-gradient(180deg, #eef2e7 0%, #e4e9dd 100%);
            color: var(--ink);
            font-family: 'Source Sans 3', sans-serif;
        }

        .block-container {
            max-width: 920px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .hero {
            border: 1px solid rgba(36, 46, 31, 0.25);
            border-left: 6px solid var(--army-700);
            border-right: 6px solid var(--army-700);
            background: linear-gradient(130deg, rgba(244,241,232,0.96), rgba(231,236,224,0.94));
            border-radius: 12px;
            padding: 1rem 1.2rem 0.9rem;
            box-shadow: 0 6px 20px rgba(26, 33, 23, 0.08);
            margin-bottom: 1rem;
        }

        .hero-kicker {
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            color: var(--paper);
            background: linear-gradient(90deg, var(--fr-blue), var(--army-700), var(--fr-red));
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            margin-bottom: 0.55rem;
        }

        .hero-title {
            margin: 0;
            font-family: 'Cinzel', serif;
            font-weight: 700;
            color: var(--army-900);
            letter-spacing: 0.02em;
            font-size: clamp(1.35rem, 2.2vw, 2rem);
        }

        .hero-sub {
            margin: 0.35rem 0 0;
            font-size: 0.98rem;
            color: #2f3728;
        }

        .status-strip {
            margin-top: 0.8rem;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
        }

        .status-card {
            border: 1px solid rgba(63, 79, 54, 0.28);
            background: rgba(255, 255, 255, 0.55);
            border-radius: 8px;
            padding: 0.42rem 0.55rem;
        }

        .status-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #44523a;
            font-weight: 700;
        }

        .status-value {
            margin-top: 0.2rem;
            font-size: 0.98rem;
            font-weight: 700;
            color: var(--army-900);
        }
        
        .question-box {
            border: 1px solid rgba(36, 46, 31, 0.22);
            border-left: 5px solid var(--army-700);
            background: var(--paper);
            border-radius: 10px;
            padding: 0.95rem 1rem 0.9rem;
            margin: 0.6rem 0 0.8rem;
        }

        .question-meta {
            font-size: 0.84rem;
            color: #4d5a41;
            letter-spacing: 0.015em;
            margin-bottom: 0.2rem;
            text-transform: uppercase;
            font-weight: 700;
        }

        .question-text {
            margin: 0.05rem 0 0;
            color: #1d2119;
            font-size: 1.08rem;
            font-weight: 700;
        }

        .stButton > button {
            background: linear-gradient(180deg, #4d6141 0%, #36492c 100%);
            color: #f6f4ed;
            border: 1px solid #2a3822;
            border-radius: 8px;
            font-weight: 700;
            letter-spacing: 0.01em;
            min-height: 50px;
            font-size: 1.02rem;
        }

        .stButton > button:hover {
            filter: brightness(1.06);
            border-color: #1f2b18;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--fr-blue), var(--army-700), var(--fr-red));
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2a3426 0%, #1f271c 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #ecf1e7;
        }

        div[data-testid="stRadio"] > div[role="radiogroup"] > label {
            border: 1px solid rgba(36, 46, 31, 0.24);
            border-radius: 10px;
            padding: 0.62rem 0.72rem;
            margin-bottom: 0.5rem;
            background: rgba(255, 255, 255, 0.58);
        }

        div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
            border-color: #3f4f36;
            background: rgba(255, 255, 255, 0.78);
        }

        [data-testid="stSidebarCollapseButton"] button {
            min-height: 42px;
            min-width: 42px;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 0.8rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }
            .status-strip {
                grid-template-columns: 1fr;
            }
            .hero {
                padding: 0.9rem 0.9rem 0.8rem;
            }
            .question-text {
                font-size: 1rem;
            }
            .hero-kicker {
                font-size: 0.68rem;
            }
            .status-value {
                font-size: 1.05rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(total_questions: int, done_questions: int, score: int) -> None:
    pct = 0.0
    if done_questions > 0:
        pct = 100 * score / done_questions

    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-kicker">Instruction et preparation</div>
            <h1 class="hero-title">Quiz Memento Militaire du rang</h1>
            <p class="hero-sub">Entrainement progressif en francais, inspire du contenu du livret.</p>
            <div class="status-strip">
                <div class="status-card">
                    <div class="status-label">Questions traitees</div>
                    <div class="status-value">{done_questions} / {total_questions}</div>
                </div>
                <div class="status-card">
                    <div class="status-label">Score actuel</div>
                    <div class="status-value">{score}</div>
                </div>
                <div class="status-card">
                    <div class="status-label">Precision</div>
                    <div class="status-value">{pct:.1f}%</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def build_detailed_explanation(correct: bool, user_answer: str, good_answer: str, base_explanation: str) -> str:
    verdict = "Bonne reponse" if correct else "Reponse incorrecte"
    return (
        f"{verdict}. "
        f"Vous avez repondu: {user_answer}. "
        f"La bonne reponse est: {good_answer}. "
        f"Pourquoi: {base_explanation}"
    )


def load_question_bank() -> list[dict]:
    with QUESTIONS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def prepare_quiz(
    questions: list[dict],
    chapters: list[str],
    levels: list[str],
    amount: int,
    only_grades: bool = False,
    only_famas: bool = False,
    only_nato: bool = False,
) -> list[dict]:
    selected = [
        q
        for q in questions
        if q["chapter"] in chapters
        and q["difficulty"] in levels
        and (not only_grades or is_grade_question(q))
        and (not only_famas or is_famas_question(q))
        and (not only_nato or is_nato_question(q))
    ]

    if not selected:
        return []

    rng = random.SystemRandom()
    rng.shuffle(selected)

    if amount <= len(selected):
        chosen = selected[:amount]
    else:
        # Repeat the filtered set in shuffled waves so we can always reach the requested count.
        chosen = []
        while len(chosen) < amount:
            wave = list(selected)
            rng.shuffle(wave)
            chosen.extend(wave)
        chosen = chosen[:amount]

    prepared = []
    for raw in chosen:
        q = copy.deepcopy(raw)
        options = list(q["options"])
        answer_text = options[q["answer"]]
        rng.shuffle(options)
        q["options"] = options
        q["answer"] = options.index(answer_text)
        prepared.append(q)

    return prepared


def reset_state() -> None:
    st.session_state.quiz = []
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.locked = False
    st.session_state.chosen_option = None
    st.session_state.history = []


def start_quiz(
    bank: list[dict],
    chapters: list[str],
    levels: list[str],
    amount: int,
    only_grades: bool = False,
    only_famas: bool = False,
    only_nato: bool = False,
) -> None:
    quiz = prepare_quiz(bank, chapters, levels, amount, only_grades=only_grades, only_famas=only_famas, only_nato=only_nato)
    reset_state()
    st.session_state.quiz = quiz
    st.session_state.collapse_sidebar_once = True


def close_sidebar_once_if_needed() -> None:
    if not st.session_state.get("collapse_sidebar_once", False):
        return

    # Close only when currently open (avoids toggling it open by mistake).
    components.html(
        """
        <script>
        const doc = window.parent.document;
        const btn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
        if (btn) {
          const label = (btn.getAttribute('aria-label') || '').toLowerCase();
          if (label.includes('close') || label.includes('fermer')) {
            btn.click();
          }
        }
        </script>
        """,
        height=0,
        width=0,
    )
    st.session_state.collapse_sidebar_once = False


st.set_page_config(page_title="Quiz Memento Militaire S2", layout="centered", initial_sidebar_state="collapsed")
inject_theme()

if "quiz" not in st.session_state:
    reset_state()
if "collapse_sidebar_once" not in st.session_state:
    st.session_state.collapse_sidebar_once = False

bank = load_question_bank()
all_chapters = sorted({q["chapter"] for q in bank})
all_levels = ["facile", "moyen", "difficile"]

with st.sidebar:
    st.header("Configuration tactique")
    selected_chapters = st.multiselect(
        "Chapitres",
        all_chapters,
        default=all_chapters,
        )
    selected_levels = st.multiselect(
        "Difficultes",
        all_levels,
        default=all_levels,
    )

    only_grade_questions = st.checkbox("Uniquement questions de grades", value=False)
    only_famas_questions = st.checkbox(
        "Uniquement questions FAMAS",
        value=False,
        disabled=only_grade_questions,
    )
    only_nato_questions = st.checkbox(
        "Uniquement questions OTAN",
        value=False,
        disabled=only_grade_questions or only_famas_questions,
    )

    effective_chapters = selected_chapters
    if only_grade_questions:
        effective_chapters = ["Grades"]
        st.caption("Mode grades: seules les questions de grades seront utilisees.")
    elif only_famas_questions:
        effective_chapters = all_chapters
        st.caption("Mode FAMAS: seules les questions liees au FAMAS seront utilisees.")
    elif only_nato_questions:
        effective_chapters = all_chapters
        st.caption("Mode OTAN: seules les questions de l'alphabet phonetique OTAN seront utilisees.")

    available_count = sum(
        1
        for q in bank
        if q["chapter"] in effective_chapters
        and q["difficulty"] in selected_levels
        and (not only_grade_questions or is_grade_question(q))
        and (not only_famas_questions or is_famas_question(q))
        and (not only_nato_questions or is_nato_question(q))
    )

    if available_count == 0:
        question_count = 1
        st.warning("Aucune question disponible avec ces filtres.")
    else:
        max_questions = 20
        default_questions = min(20, max(10, available_count))
        question_count = st.slider(
            "Nombre de questions",
            min_value=1,
            max_value=max_questions,
            value=default_questions,
            step=1,
        )
        st.caption(f"Questions disponibles: {available_count}")
        if available_count < 20:
            st.caption("Moins de 20 questions uniques: certaines seront repetees pour atteindre le nombre choisi.")

    if st.button("Demarrer un nouveau quiz", use_container_width=True, disabled=available_count == 0):
        start_quiz(
            bank,
            effective_chapters,
            selected_levels,
            question_count,
            only_grades=only_grade_questions,
            only_famas=only_famas_questions,
            only_nato=only_nato_questions,
        )
        st.rerun()

    if st.button("La Marseillaise", use_container_width=True):
        st.session_state.show_marseillaise = not st.session_state.get("show_marseillaise", False)
        st.rerun()
    
    if st.button("🎺 Chant du départ", use_container_width=True):
        st.session_state.show_chant_depart = not st.session_state.get("show_chant_depart", False)
        st.rerun()
    
    if st.button("🔫 Le Chant des partisans", use_container_width=True):
        st.session_state.show_chant_partisans = not st.session_state.get("show_chant_partisans", False)
        st.rerun()

close_sidebar_once_if_needed()

# Display La Marseillaise if requested
if st.session_state.get("show_marseillaise", False):
    st.markdown("# 🇫🇷 La Marseillaise")
    st.markdown("*Hymne National de la République Française*")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Fermer", key="close_marseillaise"):
            st.session_state.show_marseillaise = False
            st.rerun()
    with col2:
        st.markdown("[🎵 Écouter sur YouTube](https://youtu.be/SRl7AzeWwOo?si=uJLKGdbqfFhlW-Ii)")
    
    st.divider()
    
    marseillaise_text = """
## **REFRAIN**

Aux armes, citoyens !
Formez vos bataillons !
Marchons, marchons !
Qu'un sang impur...
Abreuve nos sillons !

---

## **COUPLETS**

### **I**

Allons ! Enfants de la Patrie !
Le jour de gloire est arrivé !
Contre nous de la tyrannie,
L'étendard sanglant est levé ! (Bis)
Entendez-vous dans les campagnes
Mugir ces féroces soldats ?
Ils viennent jusque dans vos bras
Égorger vos fils, vos compagnes

**REFRAIN**

### **II**

Que veut cette horde d'esclaves,
De traîtres, de rois conjurés ?
Pour qui ces ignobles entraves,
Ces fers dès longtemps préparés ? (Bis)
Français ! Pour nous, ah ! Quel outrage !
Quels transports il doit exciter ;
C'est nous qu'on ose méditer
De rendre à l'antique esclavage !

**REFRAIN**

### **III**

Quoi ! Des cohortes étrangères
Feraient la loi dans nos foyers !
Quoi ! Des phalanges mercenaires
Terrasseraient nos fiers guerriers ! (Bis)
Dieu ! Nos mains seraient enchaînées !
Nos fronts sous le joug se ploieraient !
De vils despotes deviendraient
Les maîtres de nos destinées !

**REFRAIN**

### **IV**

Tremblez, tyrans et vous, perfides,
L'opprobre de tous les partis !
Tremblez ! Vos projets parricides
Vont enfin recevoir leur prix. (Bis)
Tout est soldat pour vous combattre.
S'ils tombent, nos jeunes héros,
La terre en produit de nouveaux
Contre vous tout prêts à se battre.

**REFRAIN**

### **V**

Français, en guerriers magnanimes
Portons ou retenons nos coups !
Épargnons ces tristes victimes,
A regret, s'armant contre nous ! (Bis)
Mais ce despote sanguinaire !
Mais ces complices de Bouillé !
Tous ces tigres qui, sans pitié,
Déchirent le sein de leur mère !

**REFRAIN**

### **VI**

Amour sacré de la Patrie
Conduis, soutiens nos bras vengeurs !
Liberté ! Liberté chérie,
Combats avec tes défenseurs ! (Bis)
Sous nos drapeaux que la Victoire
Accoure à tes mâles accents !
Que tes ennemis expirants
Voient ton triomphe et notre gloire !

**REFRAIN**

---

### **COUPLET DES ENFANTS**

Nous entrerons dans la carrière,
Quand nos aînés n'y seront plus ;
Nous y trouverons leur poussière
Et la trace de leurs vertus. (Bis)
Bien moins jaloux de leur survivre
Que de partager leur cercueil
Nous aurons le sublime orgueil
De les venger ou de les suivre.

**REFRAIN**
"""
    
    st.markdown(marseillaise_text)
    st.stop()

# Display Chant du départ if requested
if st.session_state.get("show_chant_depart", False):
    st.markdown("# 🎺 Chant du départ")
    st.markdown("*Chant patriotique de la Révolution française*")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Fermer", key="close_chant_depart"):
            st.session_state.show_chant_depart = False
            st.rerun()
    with col2:
        st.markdown("[🎵 Écouter sur YouTube](https://youtu.be/F0KMxoTetnc?si=Kw_wFW96HLvMpeVK)")
    
    st.divider()
    
    chant_depart_text = """
La victoire en chantant
Nous ouvre la barrière
La liberté guide nos pas
Et du Nord au Midi
La trompette guerrière
A sonné l'heure des combats

Tremblez ennemis de la France
Rois ivres de sang et d'orgueil
Le peuple souverain s'avance (le peuple souverain s'avance)
Tyrans descendez au cercueil

**La République nous appelle**
**Sachons vaincre ou sachons périr**
**Un Français doit vivre pour elle (un Français doit vivre pour elle)**
**Pour elle un Français doit mourir**
**Un Français doit vivre pour elle (un Français doit vivre pour elle)**
**Pour elle un Français doit mourir**

---

Que le fer paternel arme la main des braves
Songez à nous au champ de Mars
Consacrez dans le sang des rois et des esclaves
Le fer béni par vos vieillards

Et, rapportant sous la chaumière
Des blessures et des vertus
Venez fermer notre paupière (fermer notre paupière)
Quand les tyrans n'y seront plus

**La République nous appelle**
**Sachons vaincre ou sachons périr**
**Un Français doit vivre pour elle (un Français doit vivre pour elle)**
**Pour elle un Français doit mourir**
**Un Français doit vivre pour elle (un Français doit vivre pour elle)**
**Pour elle un Français doit mourir**
"""
    
    st.markdown(chant_depart_text)
    st.stop()

if not st.session_state.quiz:
    render_hero(total_questions=question_count, done_questions=0, score=0)
    st.caption("Sur mobile: ouvrez le menu en haut a gauche pour la configuration du quiz.")
    st.info("Choisissez vos options puis cliquez sur 'Demarrer un nouveau quiz'.")
    st.stop()

quiz = st.session_state.quiz
idx = st.session_state.index

if idx >= len(quiz):
    total = len(quiz)
    score = st.session_state.score
    pct = 100 * score / total if total else 0

    render_hero(total_questions=total, done_questions=total, score=score)
    st.success(f"Quiz termine: {score}/{total} ({pct:.1f}%)")

    if st.session_state.history:
        wrong = [h for h in st.session_state.history if not h["correct"]]
        if wrong:
            st.subheader("Revision des erreurs")
            for item in wrong:
                st.markdown(f"- **{item['question']}**")
                st.write(f"Votre reponse: {item['user_answer']}")
                st.write(f"Bonne reponse: {item['good_answer']}")
                st.write(f"Explication: {item['explanation']}")
        else:
            st.write("Aucune erreur, excellent resultat.")

    st.stop()

q = quiz[idx]
render_hero(total_questions=len(quiz), done_questions=idx, score=st.session_state.score)
st.progress((idx + 1) / len(quiz), text=f"Question {idx + 1}/{len(quiz)}")
st.markdown(
    f"""
    <section class="question-box">
        <div class="question-meta">Chapitre: {q['chapter']} | Niveau: {q['difficulty']}</div>
        <p class="question-text">{q['question']}</p>
    </section>
    """,
    unsafe_allow_html=True,
)

image_path = q.get("image")
if image_path:
    if str(image_path).startswith("http://") or str(image_path).startswith("https://"):
        st.image(str(image_path), caption="Insigne a identifier", use_container_width=True)
    else:
        p = Path(image_path)
        if p.exists():
            st.image(str(p), caption="Insigne a identifier", use_container_width=True)

st.session_state.chosen_option = st.radio(
    "Choisissez votre reponse:",
    list(range(len(q["options"]))),
    format_func=lambda i: q["options"][i],
    key=f"choice_{q['id']}_{idx}",
)

if st.button("Valider", use_container_width=True, disabled=st.session_state.locked):
    correct = st.session_state.chosen_option == q["answer"]
    if correct:
        st.session_state.score += 1
    st.session_state.locked = True
    st.session_state.history.append(
        {
            "question": q["question"],
            "correct": correct,
            "user_answer": q["options"][st.session_state.chosen_option],
            "good_answer": q["options"][q["answer"]],
            "explanation": q["explanation"],
        }
    )

if st.session_state.locked:
    last = st.session_state.history[-1]
    if last["correct"]:
        st.success("Bonne reponse, bien joue.")
    else:
        st.error("Mauvaise reponse, continuez l entrainement.")

    detailed = build_detailed_explanation(
        correct=last["correct"],
        user_answer=last["user_answer"],
        good_answer=last["good_answer"],
        base_explanation=last["explanation"],
    )
    st.info(f"Explication detaillee: {detailed}")

    if st.button("Question suivante", use_container_width=True):
        st.session_state.index += 1
        st.session_state.locked = False
        st.rerun()

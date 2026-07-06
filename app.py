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
            <div class="hero-kicker"></div>
            <h1 class="hero-title">Quiz</h1>
            <p class="hero-sub"></p>
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
    st.header("Configuration")
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

    if st.button(" 🎺 Les commandos", use_container_width=True):
        st.session_state.show_commandos = not st.session_state.get("show_commandos", False)
        st.rerun()
    
    if st.button("🎺 Ceux du Liban", use_container_width=True):
        st.session_state.show_ceux_liban = not st.session_state.get("show_ceux_liban", False)
        st.rerun()

    if st.button("🎺 Chant pas de gymnastique", use_container_width=True):
        st.session_state.show_chant_pas_gym = not st.session_state.get("show_chant_pas_gym", False)
        st.rerun()
    
close_sidebar_once_if_needed()

# Display Les commandos if requested
if st.session_state.get("show_commandos", False):
    st.markdown("# Les commandos")
    st.markdown("Les commandos")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Fermer", key="close_Les commandos"):
            st.session_state.show_commandos = False
            st.rerun()
    with col2:
        st.markdown("[🎵 Écouter sur YouTube](https://youtu.be/SRl7AzeWwOo?si=uJLKGdbqfFhlW-Ii)")
    
    st.divider()
    
    Lescommandos_text = """
1. Les commandos partent pour l'aventure
Soleil couchant les salue, 2.1.2
Chez l'ennemi, la nuit sera très dure
Pour ceux qui pillent et qui tuent. 2.1.2

## Refrain

France, ô ma France très belle 2
Pour toi je ferai bataille, 2
Je quitterai père et mère 2
Sans espoir de les revoir jamais,

La la la la la la la la la la,
 2
La la la la la la la la la la,
La la la la la la la la la la, 
2
La la la la la la. 2.1.2

2. Loin du biffin qui toujours les envie
Un Dakota les dépose ; 2.1.2
Loin de la fille qui pour eux toujours prie
Dans leurs pépins ils reposent. 2.1.2

3. En pagayant sur la mer toujours belle
Ils songeront à leur vie, 2.1.2
Ils peuvent demain devenir éternels (2)
Ils tomberont dans l'oubli. 2.1.2

4. Si d'aventure la mort les refuse
Ils rentreront dans leur port, 2.1.2
Et ils boiront le champagne qui fuse
À la santé de leurs morts. 2.1.2
"""
    
    st.markdown(Lescommandos_text)
    st.stop()

# Display Ceux du Liban if requested
if st.session_state.get("show_ceux_liban", False):
    st.markdown("# 🎺 Ceux du Liban")
    st.markdown("*Chant militaire* ")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Fermer", key="close_ceux_liban"):
            st.session_state.show_ceux_liban = False
            st.rerun()
    with col2:
        st.markdown("[🎵 Écouter sur YouTube](https://www.youtube.com/results?search_query=Ceux+du+Liban+chant)")
    
    st.divider()
    
    ceux_liban_text = """
1. Dans la boue, les sillons,
Sous le ciel gris nous marchons,
Malgré la fatigue et la pluie,
Malgré la famine et l'ennui ;
Nous veillons et nous attendons
Que pour nous gronde le canon,
Si demain il nous appelait,
Nous partirions sans un regret.

## Refrain

La France pleure ses enfants
Tombés là-bas au Levant,
Nous garderons leur souvenir,
Comme eux nous voulons bien servir.
Nos anciens du Liban
Nous précèdent en avant :
Vivant pour le même horizon,
Pour la France nous servirons.

2. Sous le soleil brûlant
Montaient nos rires et nos chants,
Notre sourire était la paix
Pour tous ces enfants qui souffraient,
Sur nous des orages d'acier,
Sur terre se sont déchaînés,
Pour que sous un ciel bas et noir
À jamais meure tout espoir.
"""
    
    st.markdown(ceux_liban_text)
    st.stop()

# Display Chant pas de gymnastique if requested
if st.session_state.get("show_chant_pas_gym", False):
    st.markdown("# 🎺 Chant pas de gymnastique")
    st.markdown("*S2 EMB Pas de gymnastique* ")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Fermer", key="close_chant_pas_gym"):
            st.session_state.show_chant_pas_gym = False
            st.rerun()
    with col2:
        st.markdown("")

    st.divider()

    chant_pas_gym_text = """
1-2-3-4

Réservistes, fiers de servir,

Le cœur vaillant, prêts à bondir,

Plus loin, plus haut, sans faiblir,

Au-delà du possible, sans faillir.

Nous sommes les béliers, sans pareil,

Le corps uni, l'âme en éveil,

Face au danger, sans un sommeil,

Jusqu'au bout, jusqu'au réveil.
"""

    st.markdown(chant_pas_gym_text)
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

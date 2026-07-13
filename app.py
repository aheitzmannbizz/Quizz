import copy
from io import BytesIO
import json
import random
from pathlib import Path
from urllib.request import urlopen

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image


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


def load_question_image(question: dict) -> Image.Image | None:
    image_path = question.get("image")
    if not image_path:
        return None

    try:
        if str(image_path).startswith("http://") or str(image_path).startswith("https://"):
            with urlopen(str(image_path)) as response:
                image = Image.open(BytesIO(response.read()))
        else:
            image_file = Path(str(image_path))
            if not image_file.exists():
                return None
            image = Image.open(image_file)

        image.load()
    except Exception:
        return None

    crop = question.get("image_crop")
    if not isinstance(crop, dict):
        return image

    left = crop.get("left", 0)
    top = crop.get("top", 0)
    right = crop.get("right", image.width)
    bottom = crop.get("bottom", image.height)

    if all(isinstance(value, (int, float)) for value in (left, top, right, bottom)):
        if all(0 <= value <= 1 for value in (left, top, right, bottom)):
            left = int(left * image.width)
            top = int(top * image.height)
            right = int(right * image.width)
            bottom = int(bottom * image.height)

        left = max(0, min(int(left), image.width))
        top = max(0, min(int(top), image.height))
        right = max(left + 1, min(int(right), image.width))
        bottom = max(top + 1, min(int(bottom), image.height))
        return image.crop((left, top, right, bottom))

    return image


def render_question_image(question: dict) -> None:
    image = load_question_image(question)
    if image is not None:
        try:
            st.image(image, caption="Insigne a identifier", use_container_width=True)
        except Exception:
            st.warning("Impossible d'afficher l'image pour cette question.")
        return

    image_path = question.get("image")
    if not image_path:
        return

    if str(image_path).startswith("http://") or str(image_path).startswith("https://"):
        try:
            st.image(str(image_path), caption="Insigne a identifier", use_container_width=True)
        except Exception:
            st.warning("Image distante indisponible pour cette question.")
        return

    image_file = Path(str(image_path))
    if image_file.exists():
        try:
            st.image(str(image_file), caption="Insigne a identifier", use_container_width=True)
        except Exception:
            st.warning("Impossible d'afficher l'image locale pour cette question.")


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
        options_raw = q.get("options")
        answer_idx = q.get("answer")
        if not isinstance(options_raw, list) or len(options_raw) < 2:
            continue
        if not isinstance(answer_idx, int) or answer_idx < 0 or answer_idx >= len(options_raw):
            continue

        options = list(options_raw)
        answer_text = options[answer_idx]
        rng.shuffle(options)
        q["options"] = options
        q["answer"] = options.index(answer_text)
        q.setdefault("chapter", "Inconnu")
        q.setdefault("difficulty", "inconnu")
        q.setdefault("question", "Question indisponible")
        q.setdefault("explanation", "Aucune explication disponible.")
        q.setdefault("id", f"fallback_{len(prepared)}")
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
        "Uniquement questions alphabet OTAN",
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

    if st.button("⭐ Appellations des grades", use_container_width=True):
        st.session_state.show_Appellations des grades_section = not st.session_state.get("show_grades_section", False)
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
 **En 1948, trente commandos du 11e Choc sont sélectionnés pour participer à des manœuvres dans le Tyrol, 
 alors zone d’occupation française. 
 Les paroles sont alors écrites par le sergent Vincent Mayoli du 11e Choc et la musique est composée par son cousin, 
 le maréchal des logis Paul Pergola du 35e RAP.**

**Le chant est publié à la fin des années cinquante dans le Carnet de chants des Cadets de France et
 enregistré par les parachutistes du 3e RPIMa (Les casquettes sont là, Philips, Médiuem B 76.480 R, 1958).
Il est largement repris dans toute l’armée.**

**Chant :**

1. Les commandos partent pour l'aventure
Soleil couchant les salue, 2.1.2
Chez l'ennemi, la nuit sera très dure 
Pour ceux qui pillent et qui tuent. 2.1.2

Refrain
France, ô ma France très belle 2
Pour toi je ferai bataille, 2
Je quitterai père et mère 2
Sans espoir de les revoir jamais,
La la la la la la la la la la, 2
La la la la la la la la la la,
La la la la la la la la la la, 2
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
**Exemple emblématique de la vitalité du répertoire militaire français, ce chant est créé en école puis
s’est largement diffusé dans la troupe. Il est écrit fin 1983 au sein de la promotion EOR amalgamée (la
structure de l’époque) entre Saint-Cyriens de la promotion Lieutenant-Colonel Gaucher, élèves-
officiers de réserve et Polytechniciens. La promotion prend le nom de Ceux du Liban en hommage aux 
victimes de l’attentat du Drakkar survenu en octobre.**

**L’auteur est l’EOA Christophe de Lajudie, l’élève chant de la promotion. Il témoigne en décembre 
2020 :**

**« Le chef de bataillon Falzone, OSA du bataillon, me convoqua et me remit une liasse de partitions
composées pour un chant de promotion par un EOR d’une précédente promotion (la promotion du 
Guesclin…), compositeur de son état, lequel avait composé plusieurs partitions et avait laissé le “rab” au
bataillon. J’en ai déchiffré une laborieusement, j’ai écrit des paroles, on s’est mis à quelques-uns dans un 
“peigne” un soir pour répéter et bricoler une deuxième voix (une bête harmonisation à la tierce), et c’est
devenu le chant de la promotion. Le chant a eu un succès certain, on nous l’a souvent redemandé et,
quelques années après, j’ai eu la surprise de voir dans un régiment, une compagnie se rendre au pas 
cadencé à l’ordinaire en chantant ce chant ».**

**Dans la tradition orale, il est exceptionnel de retrouver les circonstances de création d’un chant, car 
les auteurs ne se préoccupent pas de postérité. Ceux du Liban n’est pas enregistré par la promotion,
mais par les parachutistes du 3e RPIMa en 1990 (CD, Dimupro, DMP 9001 C). Ils l’avaient donc appris 
par tradition orale. Il est publié dans un carnet de chants du 2e Hussards quelques années plus tard.**

**Chant :**

1. Dans la boue, les sillons,
Sous le ciel gris nous marchons,
Malgré la fatigue et la pluie,
Malgré la famine et l'ennui ;
Nous veillons et nous attendons
Que pour nous gronde le canon,
Si demain il nous appelait,
Nous partirions sans un regret.

Refrain

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

# Display Grades section if requested
if st.session_state.get("show_grades_section", False):
    st.markdown("# ⭐ Grades")
    st.markdown("*Contenu provisoire* ")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Fermer", key="close_grades_section"):
            st.session_state.show_grades_section = False
            st.rerun()
    with col2:
        st.markdown("")

    st.divider()

    grades_placeholder_text = """
S'adresser correctement a un membre de l'Armee de terre repond a des codes tres precis. Tout repose sur une regle d'or : **le « Mon » militaire signifie « Monsieur »** (une contraction historique de *« Monsieur le... »*). Il ne s'agit pas d'un pronom possessif.

C'est cette subtilite qui dicte la difference majeure entre la facon d'adresser un homme et une femme.

## 1. La regle d'or (Homme vs Femme)

- **Pour un Homme :** On fait preceder le grade de **« Mon »** a partir du grade d'adjudant (Exemple : *« Mon capitaine »*).
- **Pour une Femme :** On l'appelle **directement par son grade**, sans jamais mettre « Mon » ni « Madame » devant (Exemple : *« Capitaine »*).

> **Pourquoi ?** Dire *« Mon lieutenant »* a une femme reviendrait textuellement a l'appeler *« Monsieur le lieutenant »*. A l'inverse, l'usage du *« Ma »* (*« Ma capitaine »*) est proscrit dans le reglement officiel de l'Armee de terre francaise.

## 2. Tableau recapitulatif des appellations (a l'oral)

Voici comment s'adresser aux militaires de l'Armee de terre selon leur categorie et leur genre :

| Categorie | Grade | Pour un Homme | Pour une Femme |
| --- | --- | --- | --- |
| **Officiers Generaux** | General (de brigade, division, etc.) | *« Mon general »* | *« General »* |
| **Officiers Superieurs** | Colonel / Lieutenant-colonel | *« Mon colonel »* | *« Colonel »* |
| **Officiers Superieurs** | Commandant *(ou Chef de bataillon / d'escadrons)* | *« Mon commandant »* | *« Commandant »* |
| **Officiers Subalternes** | Capitaine | *« Mon capitaine »* | *« Capitaine »* |
| **Officiers Subalternes** | Lieutenant / Sous-lieutenant / Aspirant | *« Mon lieutenant »* | *« Lieutenant »* |
| **Sous-officiers Superieurs** | Major | *« Major »* *(pas de "Mon")* | *« Major »* |
| **Sous-officiers Superieurs** | Adjudant-chef | *« Mon adjudant-chef »* | *« Adjudant-chef »* |
| **Sous-officiers Superieurs** | Adjudant | *« Mon adjudant »* | *« Adjudant »* |
| **Sous-officiers Subalternes** | Sergent-chef | *« Chef »* | *« Chef »* |
| **Sous-officiers Subalternes** | Sergent | *« Sergent »* | *« Sergent »* |
| **Militaires du Rang** | Caporal-chef / Caporal | *« Caporal-chef »* / *« Caporal »* | *« Caporal-chef »* / *« Caporal »* |
| **Militaires du Rang** | Soldat | Par son nom ou *« Monsieur »* | Par son nom ou *« Madame »* |

## 3. Les exceptions et cas particuliers a connaitre

- **Le grade de Major :** Historiquement, le major est le plus haut grade des sous-officiers. On dit simplement **« Major »**, que ce soit un homme ou une femme (jamais de « Mon »).
- **Le Sergent-chef :** Dans la pratique quotidienne, un sergent-chef (homme ou femme) s'appelle tout simplement **« Chef »**.
- **La Cavalerie (l'Arme blindee cavalerie) :** C'est une exception traditionnelle tres forte. Dans la cavalerie, on n'appelle pas les adjudants et adjudants-chefs « Mon adjudant », mais **« Mon lieutenant »** (ou *« Lieutenant »* pour une femme).
- **Si vous etes civil :** Un civil n'est pas soumis au Code de discipline militaire. Si vous ecrivez une lettre ou que vous parlez a un militaire, vous pouvez utiliser les formules civiles officielles : *« Monsieur le Capitaine »* ou *« Madame la Colonelle »* (les formes feminisees comme *Colonelle* ou *Generale* sont acceptees dans l'administration civile, bien que le milieu purement militaire prefere le grade brut *« Colonel »* ou *« General »*).
"""

    st.markdown(grades_placeholder_text)
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
        <div class="question-meta">Chapitre: {q.get('chapter', 'Inconnu')} | Niveau: {q.get('difficulty', 'inconnu')}</div>
        <p class="question-text">{q.get('question', 'Question indisponible')}</p>
    </section>
    """,
    unsafe_allow_html=True,
)

render_question_image(q)

st.session_state.chosen_option = st.radio(
    "Choisissez votre reponse:",
    list(range(len(q["options"]))),
    format_func=lambda i: q["options"][i],
    key=f"choice_{q.get('id', f'idx_{idx}')}_{idx}",
)

if st.button("Valider", use_container_width=True, disabled=st.session_state.locked):
    correct = st.session_state.chosen_option == q["answer"]
    if correct:
        st.session_state.score += 1
    st.session_state.locked = True
    st.session_state.history.append(
        {
            "question": q.get("question", "Question indisponible"),
            "correct": correct,
            "user_answer": q["options"][st.session_state.chosen_option],
            "good_answer": q["options"][q["answer"]],
            "explanation": q.get("explanation", "Aucune explication disponible."),
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

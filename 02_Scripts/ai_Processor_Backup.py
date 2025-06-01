#!/usr/bin/env python3
"""
AI Processor for Better French
Processes curated news articles to generate:
- Simplified English and French titles
- Simple English and French summaries
- Contextual learning for French words in original titles
"""

import json
import os
from datetime import datetime
import re # For basic tokenization if needed
from openai import OpenAI # <-- Added
import time # <-- Added for retries

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
import config # <-- Ensuring this is a direct import

DEFAULT_CURATED_FILE_NAME = "curated_news_data_20250531_095437.json" # Assuming this is the target
DEFAULT_CURATED_FILE = os.path.join(PROJECT_ROOT, "04_Data_Output", "Curated", DEFAULT_CURATED_FILE_NAME)
PROCESSED_OUTPUT_DIR_NAME = "Processed_AI" # New directory for these outputs
PROCESSED_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "04_Data_Output", PROCESSED_OUTPUT_DIR_NAME)

MAX_ARTICLES_TO_PROCESS = 30

# --- AI Service with Pre-designed Data & LLM Integration ---

class AIService:
    def __init__(self):
        if not config.API_KEY:
            print("ERROR: OPENROUTER_API_KEY not found in 02_Scripts/config.py. Please set it there.")
            # We don't raise an error here to allow the script to run if only using pre_designed_data
            # for a small subset, but operations will be limited.
            self.client = None 
        else:
            self.client = OpenAI(
                api_key=config.API_KEY,
                base_url=config.OPENROUTER_API_BASE,
            )
        self.model_name = config.MODEL_NAME
        # Simulated pre-designed data for consistent "AI" output
        # This would be replaced by actual AI model calls in a real scenario
        # We will KEEP this for few-shot examples and for articles already processed.
        self.pre_designed_data = {
            "Droits de douane : ces options sur la table de Donald Trump après son revers judiciaire": {
                "simplified_english_title": "Trump\'s Tariff Options After Legal Setback",
                "simplified_french_title": "Droits de douane : les options de Trump après sa défaite judiciaire",
                "english_summary": "Following a US International Trade Commission ruling that suspended some of his administration's tariffs, Donald Trump is exploring alternative legal avenues to maintain or reimpose them. The article discusses various trade laws and emergency acts Trump might leverage, such as Section 232 (national security) or Section 301 of the Trade Act of 1974 (unfair trade practices), and the constitutional debate around presidential authority in setting tariffs versus Congress. The White House is preparing a Plan B, potentially involving a two-step approach using different sections of trade law, while also considering asking Congress to legislate stronger tariff powers, though this path is politically challenging.",
                "french_summary": "Suite à une décision de justice suspendant certains tarifs douaniers, Donald Trump examine d'autres options légales pour les maintenir. L'article explore les lois commerciales et les pouvoirs d'urgence que Trump pourrait utiliser, comme la Section 232 (sécurité nationale) ou la Section 301 de la Loi sur le Commerce de 1974 (pratiques commerciales déloyales). Il aborde aussi le débat constitutionnel sur l'autorité présidentielle face au Congrès en matière de tarifs. La Maison Blanche prépare un plan alternatif, et envisage de demander au Congrès de renforcer les lois sur les tarifs, bien que cela soit politiquement difficile.",
                "contextual_title_explanations": [
                    {"original_word": "Droits de douane", "display_format": "**Customs Duties / Tariffs:** Taxes on imported goods.", "explanation": "Taxes imposed on goods when they are transported across international borders. Governments usually impose customs duties to protect domestic industries, generate revenue, or regulate the flow of goods.", "cultural_note": "Trade tariffs are a significant tool in international economic policy and can become major points of contention between countries, as seen in various trade disputes involving the US, China, and the EU."},
                    {"original_word": "ces", "display_format": "**These:** (demonstrative adjective)", "explanation": "Used to point out specific items or options being discussed.", "cultural_note": ""},
                    {"original_word": "options", "display_format": "**Options:** Choices or alternatives.", "explanation": "Different courses of action that can be chosen.", "cultural_note": ""},
                    {"original_word": "sur la table", "display_format": "**On the table:** Under consideration; being discussed or negotiated.", "explanation": "An idiomatic expression meaning that something is available for discussion or is a possibility.", "cultural_note": "Similar to the English idiom 'on the table.'"},
                    {"original_word": "de", "display_format": "**Of / From:** (preposition)", "explanation": "Indicates possession, origin, or relationship.", "cultural_note": ""},
                    {"original_word": "Donald Trump", "display_format": "**Donald Trump:** 45th President of the United States.", "explanation": "A prominent American political figure and businessman.", "cultural_note": "His presidency was marked by significant changes to US trade policy, including the imposition of tariffs on goods from various countries."},
                    {"original_word": "après", "display_format": "**After:** (preposition)", "explanation": "Indicates something that follows in time.", "cultural_note": ""},
                    {"original_word": "son", "display_format": "**His / Her / Its:** (possessive adjective)", "explanation": "Indicates possession.", "cultural_note": ""},
                    {"original_word": "revers judiciaire", "display_format": "**Legal setback / Judicial defeat:** A loss or unfavorable outcome in a court case.", "explanation": "Refers to a situation where a legal case or argument has not been successful.", "cultural_note": "Such setbacks can force a re-evaluation of strategy, as discussed in the article regarding Trump's tariff policies."}
                ]
            },
            "Donald Trump et le Qatar : les dessous d'une opération séduction très stratégique": {
                "simplified_english_title": "Trump & Qatar: Examining a Strategic Attempt to Build Goodwill",
                "simplified_french_title": "Trump et le Qatar : analyse d'une opération de charme stratégique",
                "english_summary": "This article delves into the evolving relationship between Donald Trump and Qatar, highlighting a strategic charm offensive by the Gulf nation. Despite past accusations from Trump about Qatar funding terrorism, recent interactions, including a state visit and significant economic deals (like Qatar Airways purchasing Boeing aircraft), signal a significant shift. Qatar aims to secure its position as a key US ally in the Middle East, leveraging its mediating role in regional conflicts (e.g., with Iran, Hamas) and its large US investments. The article notes Qatar's desire to avoid a repeat of the 2017 blockade and its pragmatic approach to maintaining strong ties with the Trump administration, illustrated by gestures like the (controversial) gift of a Boeing 747-8 and business deals involving Trump's family.",
                "french_summary": "L'article examine l'évolution des relations entre Donald Trump et le Qatar, soulignant une offensive de charme stratégique de la part de la nation du Golfe. Malgré des accusations passées de Trump concernant le financement du terrorisme par le Qatar, des interactions récentes, y compris une visite d'État et d'importants accords économiques (comme l'achat d'avions Boeing par Qatar Airways), indiquent un changement significatif. Le Qatar cherche à consolider sa position d'allié clé des États-Unis au Moyen-Orient, en tirant parti de son rôle de médiateur dans les conflits régionaux (par exemple, avec l'Iran, le Hamas) et de ses importants investissements aux États-Unis. L'article note le désir du Qatar d'éviter une répétition du blocus de 2017 et son approche pragmatique pour maintenir des liens solides avec l'administration Trump, illustrée par des gestes comme le don (controversé) d'un Boeing 747-8 et des accords commerciaux impliquant la famille Trump.",
                "contextual_title_explanations": [
                    {"original_word": "Donald Trump", "display_format": "**Donald Trump:** 45th President of the United States.", "explanation": "A prominent American political figure and businessman.", "cultural_note": "His foreign policy in the Middle East involved complex and sometimes shifting relationships with various Gulf states."},
                    {"original_word": "et", "display_format": "**And:** (conjunction)", "explanation": "Used to connect words or phrases.", "cultural_note": ""},
                    {"original_word": "le Qatar", "display_format": "**Qatar:** A country in the Middle East.", "explanation": "A peninsular Arab country whose terrain comprises arid desert and a long Persian (Arab) Gulf shoreline of beaches and dunes.", "cultural_note": "Qatar has been a significant player in regional politics and has used its wealth from natural gas to exert influence and mediate conflicts."},
                    {"original_word": "les dessous", "display_format": "**The hidden aspects / The inside story:** Refers to the hidden or less obvious parts of a situation.", "explanation": "Literally 'the undersides,' it implies looking beyond the surface to understand the true nature or motivations.", "cultural_note": "Often used in investigative journalism or when discussing complex political or business dealings."},
                    {"original_word": "d'une", "display_format": "**Of a:** (contraction of 'de une')", "explanation": "Indicates possession or association with a feminine singular noun.", "cultural_note": ""},
                    {"original_word": "opération séduction", "display_format": "**Charm offensive / Seduction operation:** A campaign to win favor or influence.", "explanation": "A series of actions designed to make someone or a group of people feel positive towards the person or entity carrying out the operation.", "cultural_note": "A common term in politics and public relations."},
                    {"original_word": "très", "display_format": "**Very:** (adverb)", "explanation": "Used to intensify an adjective or adverb.", "cultural_note": ""},
                    {"original_word": "stratégique", "display_format": "**Strategic:** Relating to strategy; carefully designed or planned to serve a particular purpose or advantage.", "explanation": "Implies long-term planning and a clear objective.", "cultural_note": ""}
                ]
            },
            "EXCLUSIF. Des cadres des Verts plaident pour adhérer à BDS, mouvement controversé de boycott d'Israël": {
                "simplified_english_title": "French Green Party Leaders Advocate Joining Controversial BDS Movement Against Israel",
                "simplified_french_title": "EXCLUSIF. Des responsables Verts pour l'adhésion au BDS, mouvement de boycott d'Israël controversé",
                "english_summary": "This exclusive report reveals that some leading members of the French Green Party (Les Verts/EELV) are pushing for the party to officially join the BDS (Boycott, Divestment, Sanctions) movement, a controversial campaign aimed at boycotting Israel. The article highlights internal debates and recent incidents within the party related to antisemitism and views on the Israeli-Palestinian conflict, including controversial statements by party members. The proposal to join BDS, supported by figures like parliamentary group president Cyrielle Châtelain, is contentious even within the party, especially given past problematic actions by some local BDS branches. This move comes at a sensitive time for the party as it navigates complex issues and internal divisions.",
                "french_summary": "Cet article exclusif révèle que certains dirigeants du parti Les Verts (EELV) militent pour que le parti rejoigne officiellement le mouvement BDS (Boycott, Désinvestissement, Sanctions), une campagne controversée visant à boycotter Israël. L'article met en lumière les débats internes et les incidents récents au sein du parti liés à l'antisémitisme et aux opinions sur le conflit israélo-palestinien, y compris des déclarations controversées de membres du parti. La proposition de rejoindre le BDS, soutenue par des personnalités comme la présidente du groupe parlementaire Cyrielle Châtelain, est contestée même au sein du parti, notamment en raison d'actions problématiques passées de certaines branches locales du BDS. Cette démarche intervient à un moment sensible pour le parti, qui navigue entre des questions complexes et des divisions internes.",
                "contextual_title_explanations": [
                    {"original_word": "EXCLUSIF", "display_format": "**EXCLUSIVE:** (adjective/noun)", "explanation": "Indicates that the information is being reported for the first time by this news outlet.", "cultural_note": "Commonly used in headlines to attract attention."},
                    {"original_word": "Des cadres", "display_format": "**Executives / Leading members / Cadres:** Senior or influential members of an organization.", "explanation": "'Cadre' refers to a manager, executive, or a key member of a political party or organization.", "cultural_note": "In French politics, 'cadres' are the backbone of a party's leadership and decision-making structure."},
                    {"original_word": "des Verts", "display_format": "**Of the Greens (French Green Party):** Refers to the French political party focused on environmental issues (Europe Écologie Les Verts - EELV).", "explanation": "'Les Verts' is the common name for the French Green Party.", "cultural_note": "Like Green parties in other countries, they advocate for ecological policies and often align with left-leaning social stances."},
                    {"original_word": "plaident pour", "display_format": "**Advocate for / Argue in favor of:** To publicly support or recommend a particular cause or policy.", "explanation": "'Plaider' means to plead or argue a case.", "cultural_note": ""},
                    {"original_word": "adhérer à", "display_format": "**To join / To adhere to:** To become a member of or to formally agree to support.", "explanation": "'Adhérer' means to stick to, or in a political context, to join or subscribe to a movement or party.", "cultural_note": ""},
                    {"original_word": "BDS", "display_format": "**BDS (Boycott, Divestment, Sanctions):** A Palestinian-led movement promoting boycotts, divestments, and economic sanctions against Israel.", "explanation": "The movement aims to pressure Israel to meet what it describes as Israel's obligations under international law.", "cultural_note": "BDS is a highly controversial movement, with strong opinions both for and against its methods and goals. Its potential adoption by political parties often sparks significant debate."},
                    {"original_word": "mouvement", "display_format": "**Movement:** A group of people working together to advance their shared political, social, or artistic ideas.", "explanation": "Refers to an organized effort or campaign.", "cultural_note": ""},
                    {"original_word": "controversé", "display_format": "**Controversial:** Giving rise or likely to give rise to public disagreement.", "explanation": "Indicates that the subject is a matter of dispute or strong opinions.", "cultural_note": ""},
                    {"original_word": "de boycott", "display_format": "**Of boycott:** Relating to the act of boycotting.", "explanation": "A boycott is a collective refusal to deal with a person, organization, or country as an expression of protest.", "cultural_note": ""},
                    {"original_word": "d'Israël", "display_format": "**Of Israel:** Relating to the state of Israel.", "explanation": "Referring to the country in the Middle East.", "cultural_note": ""}
                ]
            },
            "Présidentielle en Pologne : l'élection qui donne des sueurs froides à Bruxelles": {
                "simplified_english_title": "Polish Presidential Election: A Vote Causing Anxiety in Brussels (EU)",
                "simplified_french_title": "Présidentielle polonaise : l'élection qui inquiète Bruxelles",
                "english_summary": "The upcoming Polish presidential election is a source of significant concern for Brussels (representing the EU). The run-off features two candidates with starkly different visions for Poland's future and its relationship with the EU: Rafal Trzaskowski, the pro-European mayor of Warsaw, versus Karol Nawrocki, a nationalist conservative backed by the Law and Justice (PiS) party. A victory for Nawrocki could undermine the current centrist government's reforms and potentially shift Poland towards a more anti-EU stance, aligning with countries like Hungary. Conversely, a Trzaskowski win would likely strengthen Poland's pro-EU trajectory. The EU has subtly supported Trzaskowski by releasing previously blocked funds to Poland and not opposing certain Polish policies, highlighting the strategic importance of this election for the EU's future and its eastern flank, especially given Poland's growing influence since the war in Ukraine.",
                "french_summary": "L'élection présidentielle en Pologne est une source de préoccupation majeure pour Bruxelles (représentant l'UE). Le second tour oppose deux candidats aux visions radicalement différentes pour l'avenir de la Pologne et ses relations avec l'UE : Rafal Trzaskowski, le maire pro-européen de Varsovie, contre Karol Nawrocki, un conservateur nationaliste soutenu par le parti Droit et Justice (PiS). Une victoire de Nawrocki pourrait saper les réformes du gouvernement centriste actuel et potentiellement orienter la Pologne vers une position plus anti-UE, s'alignant sur des pays comme la Hongrie. Inversement, une victoire de Trzaskowski renforcerait probablement la trajectoire pro-européenne de la Pologne. L'UE a subtilement soutenu Trzaskowski en débloquant des fonds précédemment retenus et en ne s'opposant pas à certaines politiques polonaises, soulignant l'importance stratégique de cette élection pour l'avenir de l'UE et son flanc oriental, surtout compte tenu de l'influence croissante de la Pologne depuis la guerre en Ukraine.",
                "contextual_title_explanations": [
                    {"original_word": "Présidentielle", "display_format": "**Presidential (election):** Relating to the election of a president.", "explanation": "Refers to the process of electing a head of state in a republic.", "cultural_note": ""},
                    {"original_word": "en Pologne", "display_format": "**In Poland:** Referring to the country of Poland.", "explanation": "A country in Central Europe.", "cultural_note": "Poland's political direction has significant implications for the European Union, given its size and strategic location."},
                    {"original_word": "l'élection", "display_format": "**The election:** The process of choosing someone for a public office by voting.", "explanation": "A formal and organized choice by vote of a person for a political office or other position.", "cultural_note": ""},
                    {"original_word": "qui donne des sueurs froides", "display_format": "**Which is causing cold sweats / Causing great anxiety:** An idiomatic expression.", "explanation": "Literally 'gives cold sweats,' it means something that causes extreme worry, fear, or anxiety.", "cultural_note": "A common French idiom to express strong apprehension."},
                    {"original_word": "à Bruxelles", "display_format": "**To Brussels (referring to the EU):** Brussels is the de facto capital of the European Union.", "explanation": "When French media mentions 'Bruxelles' in a political context, it often refers to the institutions and decision-making bodies of the European Union.", "cultural_note": "Similar to how 'Washington' is often used to refer to the US federal government."}
                ]
            },
            # Starting new entries for articles 5-20
            "Droits de douane : ces cinq petites entreprises qui ont mis un frein à la machine Trump": {
                "simplified_english_title": "Tariffs: Five Small Businesses That Slowed the Trump Machine",
                "simplified_french_title": "Droits de douane : cinq PME freinent la machine Trump",
                "english_summary": "This article highlights how five small American businesses, from diverse sectors like wine importing and fishing gear retail, successfully challenged Donald Trump's tariff policies. Backed by the Liberty Justice Center, these companies filed a lawsuit arguing that the president overstepped his authority by imposing widespread tariffs without congressional approval, citing the negative impact on their operations due to cost uncertainty and supply chain disruptions. A federal trade court initially sided with them, blocking the tariffs, though an appeal court later granted a temporary stay, allowing the tariffs to continue for now. The case underscores the constitutional debate over executive power in trade policy and the significant economic pressure tariffs can place on small enterprises.",
                "french_summary": "Cet article met en lumière comment cinq petites entreprises américaines, de secteurs variés comme l'importation de vin et la vente d'articles de pêche, ont contesté avec succès la politique tarifaire de Donald Trump. Soutenues par le Liberty Justice Center, ces sociétés ont intenté un procès arguant que le président avait outrepassé son autorité en imposant des tarifs généralisés sans l'approbation du Congrès, citant l'impact négatif sur leurs opérations en raison de l'incertitude des coûts et des perturbations des chaînes d'approvisionnement. Un tribunal fédéral du commerce leur a initialement donné raison, bloquant les tarifs, bien qu'une cour d'appel ait ensuite accordé un sursis temporaire, permettant aux tarifs de se poursuivre pour le moment. L'affaire souligne le débat constitutionnel sur le pouvoir exécutif en matière de politique commerciale et la pression économique importante que les tarifs peuvent exercer sur les petites entreprises.",
                "contextual_title_explanations": [
                    {"original_word": "Droits de douane", "display_format": "**Customs Duties / Tariffs:** Taxes on imported goods.", "explanation": "Taxes imposed on goods when they are transported across international borders.", "cultural_note": "A recurring theme in trade policy discussions."},
                    {"original_word": "ces cinq petites entreprises", "display_format": "**These five small businesses:** Referring to specific small companies.", "explanation": "'Petites entreprises' are small to medium-sized enterprises (SMEs), often called PME in French.", "cultural_note": "Small businesses are often portrayed as being particularly vulnerable to broad economic policy shifts like tariffs."},
                    {"original_word": "qui ont mis un frein à", "display_format": "**That put a brake on / That slowed down:** An idiomatic expression.", "explanation": "Means to slow down or hinder the progress of something.", "cultural_note": "Similar to the English idiom 'put the brakes on.'"},
                    {"original_word": "la machine Trump", "display_format": "**The Trump machine:** Refers to the administrative and political apparatus of Donald Trump's presidency.", "explanation": "A metaphorical way to describe the functioning and policies of his government.", "cultural_note": "The term 'machine' often implies a powerful, relentless, and somewhat impersonal force."}
                ]
            },
            "Etats-Unis : la Cour d'appel maintient les droits de douane de Donald Trump": {
                "simplified_english_title": "USA: Appeals Court Upholds Trump's Tariffs (For Now)",
                "simplified_french_title": "États-Unis : la Cour d'appel maintient les tarifs de Trump",
                "english_summary": "In a swift reversal, a U.S. appeals court granted an emergency stay, temporarily maintaining Donald Trump's controversial tariffs that had been blocked by a lower court just a day earlier. The lower court had ruled that Trump overstepped his authority by imposing these tariffs without congressional approval. The Trump administration immediately appealed, leading to this temporary reinstatement while the case is considered on its merits. Trump criticized the initial ruling as politically motivated, while countries like China and Canada had welcomed it. The legal battle highlights the ongoing debate about presidential powers in trade policy and the economic impact of these tariffs.",
                "french_summary": "Dans un revirement rapide, une cour d'appel américaine a accordé un sursis d'urgence, maintenant temporairement les tarifs douaniers controversés de Donald Trump qui avaient été bloqués par un tribunal inférieur la veille. Le tribunal inférieur avait jugé que Trump avait outrepassé son autorité en imposant ces tarifs sans l'approbation du Congrès. L'administration Trump a immédiatement fait appel, conduisant à ce rétablissement temporaire pendant que l'affaire est examinée sur le fond. Trump a critiqué la décision initiale comme étant politiquement motivée, tandis que des pays comme la Chine et le Canada l'avait saluée. La bataille juridique met en lumière le débat actuel sur les pouvoirs présidentiels en matière de politique commerciale et l'impact économique de ces tarifs.",
                "contextual_title_explanations": [
                    {"original_word": "Etats-Unis", "display_format": "**United States:** Referring to the United States of America.", "explanation": "Country in North America.", "cultural_note": ""},
                    {"original_word": "la Cour d'appel", "display_format": "**The Court of Appeal / Appeals Court:** A court that hears appeals from lower court decisions.", "explanation": "A higher court that reviews the decisions of trial courts or other lower courts.", "cultural_note": "An essential part of the judicial process, allowing for review and potential correction of legal errors."},
                    {"original_word": "maintient", "display_format": "**Maintains / Upholds:** To keep in an existing state; to preserve from failure or decline.", "explanation": "In a legal context, it means to affirm or keep a previous decision or state of affairs in place.", "cultural_note": ""},
                    {"original_word": "les droits de douane", "display_format": "**The customs duties / The tariffs:** Taxes on imported goods.", "explanation": "Taxes imposed on goods when they are transported across international borders.", "cultural_note": ""},
                    {"original_word": "de Donald Trump", "display_format": "**Of Donald Trump:** Belonging to or enacted by Donald Trump.", "explanation": "Refers to policies associated with his presidency.", "cultural_note": ""}
                ]
            },
            "Guerre à Gaza : Benyamin Netanyahou, le grand divorce avec les Israéliens": {
                "simplified_english_title": "Gaza War: Netanyahu's Growing Disconnect with Israelis",
                "simplified_french_title": "Guerre à Gaza : Netanyahou, le fossé grandissant avec les Israéliens",
                "english_summary": "The article discusses a growing rift between Israeli Prime Minister Benjamin Netanyahu and a significant portion of the Israeli public regarding the war in Gaza and the handling of the hostage situation. While Netanyahu maintains a hardline stance, prioritizing the eradication of Hamas and projecting strength, public opinion polls show declining trust in his leadership and a majority favoring a deal for hostage release, even if it means stopping the war. The article highlights symbolic actions by Netanyahu to appeal to his right-wing base, contrasting with the anguish of hostage families and growing criticism from parts of Israeli society about the humanitarian impact of the war. Internal political challenges, including friction with the Attorney General, also add to the pressure on Netanyahu, who remains reliant on his solid coalition and hopes for a military victory to regain public support.",
                "french_summary": "L'article traite d'un fossé grandissant entre le Premier ministre israélien Benyamin Netanyahou et une part importante de l'opinion publique israélienne concernant la guerre à Gaza et la gestion de la situation des otages. Alors que Netanyahou maintient une ligne dure, priorisant l'éradication du Hamas et projetant une image de force, les sondages d'opinion montrent une baisse de confiance dans son leadership et une majorité favorable à un accord pour la libération des otages, même si cela implique l'arrêt de la guerre. L'article souligne les actions symboliques de Netanyahou pour séduire sa base de droite, contrastant avec l'angoisse des familles d'otages et les critiques croissantes d'une partie de la société israélienne sur l'impact humanitaire de la guerre. Des défis politiques internes, y compris des frictions avec la procureure générale, ajoutent également à la pression sur Netanyahou, qui reste dépendant de sa solide coalition et espère une victoire militaire pour regagner le soutien public.",
                "contextual_title_explanations": [
                    {"original_word": "Guerre à Gaza", "display_format": "**War in Gaza:** Referring to the conflict in the Gaza Strip.", "explanation": "The Gaza Strip is a Palestinian exclave on the eastern coast of the Mediterranean Sea.", "cultural_note": "This conflict is a long-standing and deeply divisive issue with significant international repercussions."},
                    {"original_word": "Benyamin Netanyahou", "display_format": "**Benjamin Netanyahu:** Current Prime Minister of Israel.", "explanation": "A prominent Israeli politician who has served multiple terms as Prime Minister.", "cultural_note": "A highly polarizing figure both within Israel and internationally."},
                    {"original_word": "le grand divorce", "display_format": "**The great divorce / The major split:** Signifies a significant separation or estrangement.", "explanation": "Implies a deep and serious disagreement or breakdown of a relationship.", "cultural_note": "Used metaphorically here to describe the relationship between Netanyahu and the Israeli public."},
                    {"original_word": "avec les Israéliens", "display_format": "**With the Israelis:** Referring to the people of Israel.", "explanation": "The citizens of the State of Israel.", "cultural_note": ""}
                ]
            },
            "Louis Sarkozy : \"J'aurais préféré mourir à 25 ans sous Auguste qu'à 80 ans dans le monde d'aujourd'hui\"": {
                "simplified_english_title": "Louis Sarkozy: \"I'd Prefer Death at 25 under Emperor Augustus than at 80 Today\"",
                "simplified_french_title": "Louis Sarkozy : \"Plutôt mourir à 25 ans sous Auguste qu'à 80 ans aujourd'hui\"",
                "english_summary": "This article features an interview with Louis Sarkozy, son of former French President Nicolas Sarkozy. He expresses a striking sentiment, stating he would have preferred to die young in the era of Roman Emperor Augustus rather than live to old age in the modern world. This controversial statement likely serves as a springboard to discuss his views on contemporary society, values, and perhaps a romanticized perception of the past compared to present-day challenges and disillusionments. The interview probably explores his personal philosophy and critiques of modern life.",
                "french_summary": "Cet article présente une interview de Louis Sarkozy, fils de l'ancien président français Nicolas Sarkozy. Il exprime un sentiment frappant, déclarant qu'il aurait préféré mourir jeune à l'époque de l'empereur romain Auguste plutôt que de vivre jusqu'à un âge avancé dans le monde moderne. Cette déclaration controversée sert probablement de tremplin pour discuter de ses opinions sur la société contemporaine, les valeurs, et peut-être une perception romancée du passé par rapport aux défis et désillusions actuels. L'interview explore probablement sa philosophie personnelle et ses critiques de la vie moderne.",
                "contextual_title_explanations": [
                    {"original_word": "Louis Sarkozy", "display_format": "**Louis Sarkozy:** Son of former French President Nicolas Sarkozy.", "explanation": "A public figure primarily known due to his father's political career.", "cultural_note": "Children of prominent politicians often attract media attention in France."},
                    {"original_word": "J'aurais préféré mourir", "display_format": "**I would have preferred to die:** Expresses a hypothetical preference for death.", "explanation": "A strong statement indicating deep dissatisfaction or a particular worldview.", "cultural_note": ""},
                    {"original_word": "à 25 ans", "display_format": "**At 25 years old:** At the age of twenty-five.", "explanation": "", "cultural_note": ""},
                    {"original_word": "sous Auguste", "display_format": "**Under Augustus (Roman Emperor):** During the reign of Emperor Augustus.", "explanation": "Augustus was the first Roman Emperor, reigning from 27 BC until his death in AD 14. His era is known as the Pax Romana (Roman Peace).", "cultural_note": "The Augustan era is often idealized as a golden age of Roman literature and culture."},
                    {"original_word": "qu'à 80 ans", "display_format": "**Than at 80 years old:** Comparing to the prospect of living to the age of eighty.", "explanation": "", "cultural_note": ""},
                    {"original_word": "dans le monde d'aujourd'hui", "display_format": "**In today's world / In the world of today:** Referring to contemporary society.", "explanation": "The current state of the world.", "cultural_note": ""}
                ]
            },
            "Face à la Chine, l'Europe en quête d'une nouvelle stratégie industrielle": {
                "simplified_english_title": "Facing China, Europe Seeks New Industrial Strategy",
                "simplified_french_title": "Face à la Chine, l'Europe cherche une nouvelle stratégie industrielle",
                "english_summary": "The European Union is currently reassessing its industrial strategy in response to the growing economic and technological power of China. This involves discussions on how to enhance Europe's competitiveness, ensure strategic autonomy in key sectors (like technology, raw materials, and green energy), and address challenges posed by China's state-led capitalism and trade practices. The article likely explores various policy options being considered, such as investing in innovation, strengthening trade defense instruments, and fostering 'European champions' to compete globally while navigating the complex geopolitical landscape.",
                "french_summary": "L'Union européenne réévalue actuellement sa stratégie industrielle en réponse à la puissance économique et technologique croissante de la Chine. Cela implique des discussions sur la manière d'améliorer la compétitivité de l'Europe, d'assurer une autonomie stratégique dans des secteurs clés (comme la technologie, les matières premières et l'énergie verte), et de relever les défis posés par le capitalisme d'État et les pratiques commerciales de la Chine. L'article explore probablement diverses options politiques envisagées, telles que l'investissement dans l'innovation, le renforcement des instruments de défense commerciale et la promotion de 'champions européens' pour rivaliser à l'échelle mondiale tout en naviguant dans un paysage géopolitique complexe.",
                "contextual_title_explanations": [
                    {"original_word": "Face à la Chine", "display_format": "**Facing China / In response to China:** Indicates a reaction or positioning relative to China.", "explanation": "Highlights the challenges or competition posed by China.", "cultural_note": "China's rise as a global economic power is a central theme in international relations and economic policy discussions in Europe."},
                    {"original_word": "l'Europe", "display_format": "**Europe (often referring to the EU):** The continent, but in policy contexts, usually means the European Union.", "explanation": "The European Union as a political and economic entity.", "cultural_note": ""},
                    {"original_word": "en quête d'une", "display_format": "**In search of a / Seeking a:** Looking for or trying to find something.", "explanation": "", "cultural_note": ""},
                    {"original_word": "nouvelle stratégie industrielle", "display_format": "**New industrial strategy:** A revised plan concerning a country's or region's manufacturing and industrial sectors.", "explanation": "Refers to policies aimed at promoting industrial growth, innovation, and competitiveness.", "cultural_note": "Industrial strategy is a key area of EU policy as it seeks to maintain its economic standing."}
                ]
            },
            "IA générative : pourquoi la France est en train de perdre la bataille face aux Etats-Unis": {
                "simplified_english_title": "Generative AI: Why France is Losing the Battle to the US",
                "simplified_french_title": "IA générative : la France perd-elle la course face aux USA ?",
                "english_summary": "This article argues that France is falling behind the United States in the field of generative Artificial Intelligence (AI). It likely examines factors such as investment levels, research and development capacity, talent attraction and retention, and the regulatory environment. The piece may compare the dynamism of the US tech scene, particularly in AI, with the French ecosystem, highlighting challenges France faces in fostering innovation and scaling up AI companies to compete with American giants. Potential solutions or national strategies to bolster France's AI capabilities might also be discussed.",
                "french_summary": "Cet article soutient que la France prend du retard sur les États-Unis dans le domaine de l'intelligence artificielle (IA) générative. Il examine probablement des facteurs tels que les niveaux d'investissement, la capacité de recherche et développement, l'attraction et la rétention des talents, et l'environnement réglementaire. L'article pourrait comparer le dynamisme de la scène technologique américaine, en particulier en IA, avec l'écosystème français, soulignant les défis auxquels la France est confrontée pour favoriser l'innovation et développer des entreprises d'IA capables de rivaliser avec les géants américains. Des solutions potentielles ou des stratégies nationales pour renforcer les capacités de la France en matière d'IA pourraient également être discutées.",
                "contextual_title_explanations": [
                    {"original_word": "IA générative", "display_format": "**Generative AI:** Artificial Intelligence that can create new content.", "explanation": "A subset of AI that can generate text, images, audio, and other media in response to prompts.", "cultural_note": "A rapidly advancing field with significant economic and societal implications, dominated by major US tech companies but with active research and development globally."},
                    {"original_word": "pourquoi la France est en train de perdre la bataille", "display_format": "**Why France is losing the battle:** Explores the reasons behind France's perceived disadvantage.", "explanation": "Suggests a competitive struggle where France is not succeeding.", "cultural_note": "There's often a public debate in France about its technological competitiveness, particularly vis-à-vis the US and China."},
                    {"original_word": "face aux Etats-Unis", "display_format": "**Against the United States / Compared to the United States:** Highlighting the US as the primary competitor or benchmark.", "explanation": "", "cultural_note": ""}
                ]
            },
            "Réforme des retraites : le gouvernement face au mur de la dette": {
                "simplified_english_title": "Pension Reform: Government Confronts Debt Wall",
                "simplified_french_title": "Réforme des retraites : le gouvernement face à la dette",
                "english_summary": "The French government is grappling with the challenge of pension reform amidst concerns about the country's significant national debt. The article likely discusses the financial pressures on the pension system, the government's proposals to ensure its long-term viability (which often include measures like raising the retirement age or adjusting contributions), and the political and social opposition these reforms typically generate. The 'debt wall' metaphor suggests an urgent and formidable financial obstacle that the government must address through these potentially unpopular measures.",
                "french_summary": "Le gouvernement français est aux prises avec le défi de la réforme des retraites dans un contexte d'inquiétude concernant l'importante dette nationale du pays. L'article discute probablement des pressions financières sur le système de retraite, des propositions du gouvernement pour assurer sa viabilité à long terme (qui incluent souvent des mesures comme l'augmentation de l'âge de la retraite ou l'ajustement des cotisations), et de l'opposition politique et sociale que ces réformes suscitent généralement. La métaphore du 'mur de la dette' suggère un obstacle financier urgent et redoutable que le gouvernement doit surmonter par ces mesures potentiellement impopulaires.",
                "contextual_title_explanations": [
                    {"original_word": "Réforme des retraites", "display_format": "**Pension Reform:** Changes to the national retirement system.", "explanation": "Refers to government policies aimed at modifying how pensions are funded, calculated, and when people can retire.", "cultural_note": "Pension reform is a highly sensitive and frequently debated political issue in France, often leading to widespread protests and strikes."},
                    {"original_word": "le gouvernement", "display_format": "**The government:** The ruling administration.", "explanation": "The executive branch of the French state.", "cultural_note": ""},
                    {"original_word": "face au mur de la dette", "display_format": "**Facing the debt wall:** Confronting a significant and challenging level of national debt.", "explanation": "The 'wall' metaphor emphasizes the difficulty and scale of the problem.", "cultural_note": "France, like many developed countries, has a substantial national debt, and its management is a constant concern for policymakers."}
                ]
            },
            "Inflation : les prix alimentaires vont-ils enfin baisser ?": {
                "simplified_english_title": "Inflation: Will Food Prices Finally Decrease?",
                "simplified_french_title": "Inflation : les prix alimentaires vont-ils baisser ?",
                "english_summary": "This article addresses the pressing question of whether food prices in France will start to decrease after a period of high inflation. It likely analyzes the factors contributing to the rise in food costs (e.g., energy prices, supply chain issues, agricultural costs) and examines any recent trends or government measures that might lead to a reduction. The piece may also discuss the impact of food inflation on households and the broader economic outlook concerning price stability.",
                "french_summary": "Cet article aborde la question pressante de savoir si les prix alimentaires en France vont commencer à baisser après une période de forte inflation. Il analyse probablement les facteurs contribuant à la hausse des coûts alimentaires (par exemple, les prix de l'énergie, les problèmes de chaîne d'approvisionnement, les coûts agricoles) et examine les tendances récentes ou les mesures gouvernementales qui pourraient entraîner une réduction. L'article pourrait également discuter de l'impact de l'inflation alimentaire sur les ménages et des perspectives économiques plus larges concernant la stabilité des prix.",
                "contextual_title_explanations": [
                    {"original_word": "Inflation", "display_format": "**Inflation:** The rate at which the general level of prices for goods and services is rising.", "explanation": "A key economic indicator reflecting the erosion of purchasing power.", "cultural_note": "High inflation, especially for essential goods like food, is a major concern for the public and policymakers."},
                    {"original_word": "les prix alimentaires", "display_format": "**Food prices:** The cost of food items.", "explanation": "", "cultural_note": ""},
                    {"original_word": "vont-ils enfin baisser ?", "display_format": "**Will they finally decrease? / Are they finally going to go down?:** Expresses a sense of anticipation or hope for a reduction.", "explanation": "The word 'enfin' (finally) suggests a period of waiting or suffering high prices.", "cultural_note": ""}
                ]
            },
            "Climat : la France peut-elle atteindre ses objectifs de réduction d'émissions ?": {
                "simplified_english_title": "Climate: Can France Meet Its Emission Reduction Targets?",
                "simplified_french_title": "Climat : la France peut-elle atteindre ses objectifs d'émissions ?",
                "english_summary": "The article examines whether France is on track to meet its stated goals for reducing greenhouse gas emissions to combat climate change. It likely assesses current progress, analyzes the effectiveness of existing policies (in sectors like transport, energy, industry, and housing), and identifies challenges or gaps that might prevent France from achieving its targets. The piece might also discuss the economic and social implications of the transition to a lower-carbon economy and compare France's efforts with international commitments.",
                "french_summary": "L'article examine si la France est en bonne voie pour atteindre ses objectifs déclarés de réduction des émissions de gaz à effet de serre afin de lutter contre le changement climatique. Il évalue probablement les progrès actuels, analyse l'efficacité des politiques existantes (dans des secteurs comme les transports, l'énergie, l'industrie et le logement), et identifie les défis ou les lacunes qui pourraient empêcher la France d'atteindre ses objectifs. L'article pourrait également discuter des implications économiques et sociales de la transition vers une économie à faible émission de carbone et comparer les efforts de la France avec les engagements internationaux.",
                "contextual_title_explanations": [
                    {"original_word": "Climat", "display_format": "**Climate:** Referring to climate change.", "explanation": "The long-term alteration of temperature and typical weather patterns in a place.", "cultural_note": "Climate change is a major global concern, and countries have set targets to reduce their impact."},
                    {"original_word": "la France peut-elle atteindre", "display_format": "**Can France achieve / Can France reach:** Questions the feasibility of achieving a goal.", "explanation": "", "cultural_note": ""},
                    {"original_word": "ses objectifs de réduction d'émissions ?", "display_format": "**Its emission reduction targets?:** The specific goals set for lowering greenhouse gas output.", "explanation": "These targets are often part of national or international agreements like the Paris Agreement.", "cultural_note": "Meeting these targets requires significant policy changes and investments."}
                ]
            },
            "JO 2024 : à un an de l'événement, Paris est-elle prête ?": {
                "simplified_english_title": "Paris Olympics 2024: One Year Out, Is the City Ready?",
                "simplified_french_title": "JO 2024 : Paris est-elle prête à un an de l'échéance ?",
                "english_summary": "With one year remaining before the 2024 Olympic Games in Paris, this article assesses the city's preparedness. It likely covers progress on venue construction, infrastructure development (especially transport), security arrangements, and logistical planning. Potential challenges such as budget concerns, public support, transportation capacity during the games, and security risks might also be examined. The piece aims to provide an overview of whether Paris is on schedule to host a successful Olympic Games.",
                "french_summary": "À un an des Jeux Olympiques de 2024 à Paris, cet article évalue l'état de préparation de la ville. Il couvre probablement les progrès de la construction des sites, le développement des infrastructures (en particulier les transports), les dispositions de sécurité et la planification logistique. Les défis potentiels tels que les préoccupations budgétaires, le soutien public, la capacité des transports pendant les jeux et les risques de sécurité pourraient également être examinés. L'article vise à donner un aperçu de la capacité de Paris à organiser avec succès les Jeux Olympiques dans les délais impartis.",
                "contextual_title_explanations": [
                    {"original_word": "JO 2024", "display_format": "**2024 Olympics (Jeux Olympiques):** Referring to the Olympic Games scheduled for 2024.", "explanation": "'JO' is the common French abbreviation for 'Jeux Olympiques'.", "cultural_note": "Hosting the Olympics is a major undertaking for any city, involving massive investment and global attention. Paris 2024 is a significant national project for France."},
                    {"original_word": "à un an de l'événement", "display_format": "**One year from the event / With one year to go:** Marking the one-year countdown.", "explanation": "", "cultural_note": ""},
                    {"original_word": "Paris est-elle prête ?", "display_format": "**Is Paris ready?:** Questions the city's state of preparedness.", "explanation": "", "cultural_note": "Media scrutiny of Olympic preparations typically intensifies as the event approaches."}
                ]
            },
            "Immigration : le projet de loi du gouvernement contesté de toutes parts": {
                "simplified_english_title": "Immigration: Government's Bill Faces Widespread Opposition",
                "simplified_french_title": "Immigration : le projet de loi gouvernemental largement contesté",
                "english_summary": "The French government's proposed immigration bill is encountering strong opposition from various groups across the political spectrum and civil society. The article likely details the key provisions of the bill, the government's rationale for it, and the specific criticisms being leveled against it. These criticisms could come from left-leaning groups concerned about human rights and a more restrictive approach, as well as from right-leaning factions who might deem the measures insufficient. The piece will probably explore the political debate surrounding the bill and its chances of passing through parliament.",
                "french_summary": "Le projet de loi sur l'immigration du gouvernement français rencontre une forte opposition de la part de divers groupes de l'échiquier politique et de la société civile. L'article détaille probablement les dispositions clés du projet de loi, la justification du gouvernement, et les critiques spécifiques formulées à son encontre. Ces critiques pourraient émaner de groupes de gauche préoccupés par les droits de l'homme et une approche plus restrictive, ainsi que de factions de droite qui pourraient juger les mesures insuffisantes. L'article explorera probablement le débat politique entourant le projet de loi et ses chances d'être adopté par le parlement.",
                "contextual_title_explanations": [
                    {"original_word": "Immigration", "display_format": "**Immigration:** The international movement of people to a destination country of which they are not natives or where they do not possess citizenship in order to settle as permanent residents or naturalized citizens.", "explanation": "", "cultural_note": "Immigration is a perennially debated topic in French politics, touching on issues of national identity, economy, and social integration."},
                    {"original_word": "le projet de loi", "display_format": "**The bill / The draft law:** A formal proposal for a new law.", "explanation": "A legislative proposal before it is enacted.", "cultural_note": ""},
                    {"original_word": "du gouvernement", "display_format": "**Of the government:** Proposed by the ruling administration.", "explanation": "", "cultural_note": ""},
                    {"original_word": "contesté de toutes parts", "display_format": "**Contested from all sides / Widely opposed:** Indicates broad disagreement from multiple perspectives.", "explanation": "Means that there is opposition from various groups or political factions.", "cultural_note": "Signifies a particularly controversial piece of legislation."}
                ]
            },
            "Education : la crise du recrutement des enseignants s'aggrave": {
                "simplified_english_title": "Education: Teacher Recruitment Crisis Worsens",
                "simplified_french_title": "Éducation : la crise du recrutement des enseignants s'intensifie",
                "english_summary": "France is facing a worsening crisis in recruiting new teachers for its education system. This article likely explores the reasons behind the teacher shortage, such as declining attractiveness of the profession, salary concerns, working conditions, and difficulties in certain subjects or regions. It may also discuss the consequences of this crisis on the quality of education and the measures being considered or implemented by the government to address the shortfall, such as recruitment drives, improved training, or better incentives.",
                "french_summary": "La France est confrontée à une aggravation de la crise du recrutement de nouveaux enseignants pour son système éducatif. Cet article explore probablement les raisons de cette pénurie d'enseignants, telles que la baisse de l'attractivité de la profession, les préoccupations salariales, les conditions de travail et les difficultés dans certaines matières ou régions. Il pourrait également discuter des conséquences de cette crise sur la qualité de l'éducation et des mesures envisagées ou mises en œuvre par le gouvernement pour pallier ce manque, telles que des campagnes de recrutement, une meilleure formation ou de meilleures incitations.",
                "contextual_title_explanations": [
                    {"original_word": "Education", "display_format": "**Education:** The system of teaching and learning.", "explanation": "", "cultural_note": "The French education system is a large, centralized public service, and issues within it are of major public concern."},
                    {"original_word": "la crise du recrutement des enseignants", "display_format": "**The teacher recruitment crisis:** A severe shortage or difficulty in hiring qualified teachers.", "explanation": "", "cultural_note": "Many Western countries have reported challenges in teacher recruitment and retention in recent years."},
                    {"original_word": "s'aggrave", "display_format": "**Is worsening / Is becoming more severe:** Indicates a deterioration of the situation.", "explanation": "", "cultural_note": ""}
                ]
            },
            "Santé : les déserts médicaux, une fracture française": {
                "simplified_english_title": "Health: Medical Deserts - A French Divide",
                "simplified_french_title": "Santé : les déserts médicaux, une fracture en France",
                "english_summary": "The article discusses the issue of 'medical deserts' in France, referring to areas (often rural or underserved urban zones) with a severe shortage of doctors and healthcare professionals. This 'fracture' highlights inequalities in access to healthcare across the country. The piece likely examines the causes of this problem (e.g., uneven distribution of practitioners, difficulties in attracting doctors to certain areas) and its consequences for local populations. Potential solutions, such as financial incentives for doctors, telemedicine, or changes in healthcare organization, might also be explored.",
                "french_summary": "L'article traite du problème des 'déserts médicaux' en France, désignant des zones (souvent rurales ou des zones urbaines défavorisées) souffrant d'une grave pénurie de médecins et de professionnels de santé. Cette 'fracture' met en lumière les inégalités d'accès aux soins de santé à travers le pays. L'article examine probablement les causes de ce problème (par exemple, la répartition inégale des praticiens, les difficultés à attirer des médecins dans certaines régions) et ses conséquences pour les populations locales. Des solutions potentielles, telles que des incitations financières pour les médecins, la télémédecine ou des changements dans l'organisation des soins de santé, pourraient également être explorées.",
                "contextual_title_explanations": [
                    {"original_word": "Santé", "display_format": "**Health:** Relating to the healthcare system.", "explanation": "", "cultural_note": "Access to healthcare is a key public service and social concern in France."},
                    {"original_word": "les déserts médicaux", "display_format": "**Medical deserts:** Areas with insufficient healthcare providers.", "explanation": "A term used to describe regions where access to doctors and medical services is severely limited.", "cultural_note": "This is a recognized problem in France and other countries, particularly affecting rural and deprived urban areas."},
                    {"original_word": "une fracture française", "display_format": "**A French divide / A French fracture:** Highlights a significant societal division or inequality within France.", "explanation": "The term 'fracture' is often used in French socio-political discourse to denote deep societal rifts.", "cultural_note": ""}
                ]
            },
            "Logement : la crise de la construction s'intensifie": {
                "simplified_english_title": "Housing: Construction Crisis Worsens in France",
                "simplified_french_title": "Logement : la crise de la construction s'aggrave",
                "english_summary": "The French housing sector is experiencing a deepening construction crisis. This article likely examines the factors contributing to this downturn, such as rising material costs, labor shortages, stricter environmental regulations, and difficulties in obtaining financing or building permits. The impact on housing availability, affordability, and the broader economy (e.g., employment in the construction sector) will probably be discussed, along with potential government responses or industry initiatives to stimulate construction.",
                "french_summary": "Le secteur français du logement traverse une crise de la construction qui s'accentue. Cet article examine probablement les facteurs contribuant à ce ralentissement, tels que la hausse des coûts des matériaux, les pénuries de main-d'œuvre, des réglementations environnementales plus strictes et les difficultés d'obtention de financements ou de permis de construire. L'impact sur la disponibilité et l'accessibilité des logements, ainsi que sur l'économie au sens large (par exemple, l'emploi dans le secteur de la construction), sera probablement discuté, de même que les éventuelles réponses gouvernementales ou initiatives du secteur pour stimuler la construction.",
                "contextual_title_explanations": [
                    {"original_word": "Logement", "display_format": "**Housing:** Refers to houses and apartments considered collectively, especially when regarded as a social or economic issue.", "explanation": "", "cultural_note": "Access to affordable and adequate housing is a significant concern in many parts of France, particularly in major urban areas."},
                    {"original_word": "la crise de la construction", "display_format": "**The construction crisis:** A severe downturn or difficulty in the building industry.", "explanation": "Indicates a significant slowdown in construction activity.", "cultural_note": "The construction sector is a key economic driver, and a crisis can have widespread effects."},
                    {"original_word": "s'intensifie", "display_format": "**Is intensifying / Is worsening:** Indicates that the crisis is becoming more severe.", "explanation": "", "cultural_note": ""}
                ]
            },
            "Sécheresse : des restrictions d'eau à prévoir cet été ?": {
                "simplified_english_title": "Drought: Water Restrictions Expected This Summer?",
                "simplified_french_title": "Sécheresse : restrictions d'eau à prévoir cet été ?",
                "english_summary": "This article discusses the likelihood of water restrictions being imposed in France during the upcoming summer due to drought conditions. It probably analyzes current water reserve levels, weather forecasts, and the impact of previous dry periods. The piece might also detail what types of restrictions could be implemented (e.g., on irrigation, car washing, filling swimming pools), which regions are most at risk, and the broader implications for agriculture, environment, and daily life. Preventative measures or long-term strategies to manage water resources in the face of climate change could also be touched upon.",
                "french_summary": "Cet article discute de la probabilité que des restrictions d'eau soient imposées en France pendant l'été à venir en raison de la sécheresse. Il analyse probablement les niveaux actuels des réserves d'eau, les prévisions météorologiques et l'impact des périodes sèches précédentes. L'article pourrait également détailler quels types de restrictions pourraient être mises en œuvre (par exemple, sur l'irrigation, le lavage des voitures, le remplissage des piscines), quelles régions sont les plus menacées, et les implications plus larges pour l'agriculture, l'environnement et la vie quotidienne. Des mesures préventives ou des stratégies à long terme pour gérer les ressources en eau face au changement climatique pourraient également être abordées.",
                "contextual_title_explanations": [
                    {"original_word": "Sécheresse", "display_format": "**Drought:** A prolonged period of abnormally low rainfall, leading to a shortage of water.", "explanation": "", "cultural_note": "Droughts have become more frequent and severe in parts of France, posing significant challenges for water management."},
                    {"original_word": "des restrictions d'eau", "display_format": "**Water restrictions:** Limitations on water use imposed by authorities.", "explanation": "Measures to conserve water during shortages.", "cultural_note": "These can range from voluntary measures to legally enforced bans on certain water uses."},
                    {"original_word": "à prévoir cet été ?", "display_format": "**To be expected this summer? / Should we expect them this summer?:** Questions the likelihood of these measures.", "explanation": "", "cultural_note": ""}
                ]
            },
            "Tourisme : la France, destination favorite des étrangers malgré des prix en hausse": {
                "simplified_english_title": "Tourism: France Remains Top Foreign Destination Despite Rising Prices",
                "simplified_french_title": "Tourisme : la France, destination préférée malgré des prix élevés",
                "english_summary": "Despite increasing prices, France continues to be the most popular tourist destination for international visitors. This article likely explores the enduring appeal of France (e.g., its culture, landmarks, cuisine, diverse regions) that keeps attracting tourists even as costs rise. It might also touch upon the economic impact of tourism, challenges such as overtourism in some areas, and strategies being employed to maintain France's leading position in the global tourism market. The piece could also compare current tourism figures with pre-pandemic levels.",
                "french_summary": "Malgré l'augmentation des prix, la France continue d'être la destination touristique la plus populaire pour les visiteurs internationaux. Cet article explore probablement l'attrait durable de la France (par exemple, sa culture, ses monuments, sa cuisine, la diversité de ses régions) qui continue d'attirer les touristes même si les coûts augmentent. Il pourrait également aborder l'impact économique du tourisme, les défis tels que le surtourisme dans certaines régions, et les stratégies employées pour maintenir la position de leader de la France sur le marché mondial du tourisme. L'article pourrait également comparer les chiffres actuels du tourisme avec les niveaux d'avant la pandémie.",
                "contextual_title_explanations": [
                    {"original_word": "Tourisme", "display_format": "**Tourism:** The business of organizing travel for pleasure.", "explanation": "", "cultural_note": "Tourism is a vital sector of the French economy, with Paris being one of the most visited cities in the world."},
                    {"original_word": "la France, destination favorite des étrangers", "display_format": "**France, favorite destination for foreigners:** Highlights France's top ranking among international tourists.", "explanation": "", "cultural_note": ""},
                    {"original_word": "malgré des prix en hausse", "display_format": "**Despite rising prices:** Acknowledges that the cost of visiting is increasing.", "explanation": "", "cultural_note": "This suggests that France's attractions are strong enough to outweigh higher costs for many travelers."}
                ]
            }
            # Add more pre-designed data here if needed
        }

    def _get_few_shot_examples(self, num_examples=2):
        """Selects a few examples from pre_designed_data for few-shot prompting."""
        example_keys = list(self.pre_designed_data.keys())
        if not example_keys:
            return ""
        
        selected_examples = []
        for i in range(min(num_examples, len(example_keys))):
            key = example_keys[i] # Simple selection, could be randomized
            data = self.pre_designed_data[key]
            example_str = f"Original Title: {key}\\n"
            example_str += f"Simplified English Title: {data['simplified_english_title']}\\n"
            example_str += f"Simplified French Title: {data['simplified_french_title']}\\n"
            example_str += f"English Summary (simple language): {data['english_summary']}\\n"
            example_str += f"French Summary (simple language): {data['french_summary']}\\n"
            example_str += f"Contextual Title Explanations (JSON format):\\n{json.dumps(data['contextual_title_explanations'], ensure_ascii=False, indent=2)}\\n---\\n"
            selected_examples.append(example_str)
        return "\\n".join(selected_examples)

    def _call_llm(self, prompt, max_retries=3, delay=5):
        """Helper function to call the LLM with retries."""
        if not self.client:
            print("LLM client not initialized. Cannot make API call.")
            return None # Or raise an error

        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI assistant for 'Better French'. Your goal is to help non-native French speakers understand complex French news articles. Provide clear, concise, and accurate information. For contextual explanations, provide them in a valid JSON list format as specified in the examples."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7, # Adjust for creativity vs. determinism
                    # max_tokens can be set if needed, but often better to let model decide or set based on task
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    print("Max retries reached. LLM call failed.")
                    return None # Or re-raise the exception

    def get_ai_generated_content(self, original_title, original_article_text=""):
        """
        Generates AI content for a given article title.
        Uses pre_designed_data if available, otherwise calls the LLM.
        original_article_text can be used by the LLM for better summaries if provided.
        """
        if original_title in self.pre_designed_data:
            print(f"Using pre-designed data for: {original_title}")
            return self.pre_designed_data[original_title]

        if not self.client:
            print(f"LLM client not available. Returning placeholders for: {original_title}")
            return self._get_placeholder_content(original_title)

        print(f"Using LLM to process: {original_title}")
        
        few_shot_examples = self._get_few_shot_examples()

        # ---任务 1: 生成简化标题 (英语和法语) ---
        title_prompt = f"""{few_shot_examples}
Given the French news article with the original title:
Original Title: {original_title}

Please provide:
1.  A simplified English title (clear, concise, and easy for a non-native French speaker learning English to understand).
2.  A simplified French title (using simpler French vocabulary and sentence structure, suitable for an intermediate French learner).

Respond ONLY with the two titles in the following format:
Simplified English Title: <Your English Title Here>
Simplified French Title: <Your French Title Here>
"""
        title_response = self._call_llm(title_prompt)
        simplified_english_title = "Placeholder simplified English title (LLM error or not implemented)"
        simplified_french_title = "Placeholder simplified French title (LLM error or not implemented)"

        if title_response:
            # Basic parsing, can be made more robust
            eng_title_match = re.search(r"Simplified English Title: (.*)", title_response)
            fr_title_match = re.search(r"Simplified French Title: (.*)", title_response)
            if eng_title_match:
                simplified_english_title = eng_title_match.group(1).strip()
            if fr_title_match:
                simplified_french_title = fr_title_match.group(1).strip()
        
        # --- Task 2: Generate Summaries (English & French) ---
        # For summaries, providing the article text is helpful if available
        summary_context = f"Original Title: {original_title}"
        if original_article_text:
            summary_context += f"\\nArticle Content Snippet (first 500 chars for context): {original_article_text[:500]}"
        
        summary_prompt = f"""{few_shot_examples}
Given the French news article:
{summary_context}

Please provide:
1.  A concise English summary (around 100-150 words) written in simple English, easy for a non-native French speaker learning English to understand. Focus on the main points.
2.  A concise French summary (around 100-150 words) written in simple French (vocabulaire et structure simples), easy for an intermediate French learner to understand. Focus on the main points.

Respond ONLY with the two summaries in the following format:
English Summary: <Your English Summary Here>
French Summary: <Your French Summary Here>
"""
        summary_response = self._call_llm(summary_prompt)
        english_summary = "Placeholder English summary (LLM error or not implemented)"
        french_summary = "Placeholder French summary (LLM error or not implemented)"

        if summary_response:
            eng_summary_match = re.search(r"English Summary: (.*)", summary_response, re.DOTALL)
            fr_summary_match = re.search(r"French Summary: (.*)", summary_response, re.DOTALL)
            if eng_summary_match:
                english_summary = eng_summary_match.group(1).strip()
            if fr_summary_match:
                french_summary = fr_summary_match.group(1).strip()

        # --- Task 3: Generate Contextual Title Explanations ---
        explanation_prompt = f"""{few_shot_examples}
Analyze the following original French news title:
Original Title: {original_title}

Identify key French words, phrases, or entities that a non-native French speaker (intermediate level) might find difficult or that have specific cultural/contextual importance.
For each identified item, provide:
1.  `original_word`: The exact word or phrase from the title.
2.  `display_format`: A short, bolded translation or very brief definition (e.g., "**Customs Duties:** Taxes").
3.  `explanation`: A slightly more detailed explanation of the word/phrase in simple English.
4.  `cultural_note`: A brief cultural note in simple English if relevant, otherwise an empty string.

Return your response as a VALID JSON list of objects, where each object represents an explanation.
Example for a single item:
[
  {{
    "original_word": "Grève",
    "display_format": "**Strike:** (Industrial action)",
    "explanation": "A work stoppage caused by the mass refusal of employees to work, usually in response to employee grievances.",
    "cultural_note": "Strikes are a common form of protest in France and can significantly impact public services."
  }}
]

Ensure the output is ONLY the JSON list. Do not include any other text before or after the JSON.
Based on the title "{original_title}", provide the JSON list of contextual explanations:
"""
        explanation_response_str = self._call_llm(explanation_prompt)
        contextual_title_explanations = []
        if explanation_response_str:
            try:
                # Attempt to clean up potential markdown ```json ... ```
                if explanation_response_str.startswith("```json"):
                    explanation_response_str = explanation_response_str[7:]
                if explanation_response_str.endswith("```"):
                    explanation_response_str = explanation_response_str[:-3]
                
                parsed_explanations = json.loads(explanation_response_str.strip())
                if isinstance(parsed_explanations, list):
                    contextual_title_explanations = parsed_explanations
                else:
                    print(f"LLM returned non-list JSON for explanations: {parsed_explanations}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON for explanations from LLM: {e}")
                print(f"LLM Raw Output for explanations:\\n{explanation_response_str}")


        return {
            "simplified_english_title": simplified_english_title,
            "simplified_french_title": simplified_french_title,
            "english_summary": english_summary,
            "french_summary": french_summary,
            "contextual_title_explanations": contextual_title_explanations
        }

    def _get_placeholder_content(self, title):
        # Fallback if LLM fails or is not configured
        return {
            "simplified_english_title": f"Placeholder simplified English title for {title}",
            "simplified_french_title": f"Placeholder simplified French title for {title}",
            "english_summary": f"Placeholder English summary for {title}. The full content would be generated by an AI model.",
            "french_summary": f"Placeholder French summary for {title} (en Français). Le contenu complet serait généré par un modèle IA.",
            "contextual_title_explanations": [
                {"original_word": "mot_exemplaire", "display_format": "**Sample word:** An example", "explanation": "This is a placeholder explanation.", "cultural_note": "This is a placeholder cultural note."}
            ]
        }

# --- Main Processing Logic ---

def load_curated_data(filepath):
    """Loads curated news data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Ensure 'curated_articles' key exists and is a list
        if 'curated_articles' not in data or not isinstance(data['curated_articles'], list):
            print(f"ERROR: 'curated_articles' key missing or not a list in {filepath}")
            return None
        return data
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from {filepath}")
        return None

def process_articles(curated_data, ai_service):
    processed_articles_output = []
    
    articles_to_process = curated_data.get("curated_articles", [])
    
    # Limit the number of articles if MAX_ARTICLES_TO_PROCESS is set and positive
    if MAX_ARTICLES_TO_PROCESS and MAX_ARTICLES_TO_PROCESS > 0:
        articles_to_process = articles_to_process[:MAX_ARTICLES_TO_PROCESS]
        print(f"Processing a maximum of {MAX_ARTICLES_TO_PROCESS} articles.")

    for i, article_data in enumerate(articles_to_process):
        original_title = article_data.get("original_data", {}).get("title")
        # Make sure to get the actual article content if it exists in your curated_data structure
        # Assuming it might be under original_data.content or original_data.text or original_data.full_text etc.
        # I'll use 'content_text' as used in the previous version of your script for the scraper.
        original_content = article_data.get("original_data", {}).get("content_text", "") 

        if not original_title:
            print(f"Skipping article {i+1} due to missing original title.")
            continue

        print(f"Processing article {i+1}/{len(articles_to_process)}: \"{original_title}\"")
        
        ai_content = ai_service.get_ai_generated_content(original_title, original_content)
        
        processed_article_entry = {
            "original_article_title": original_title, 
            "original_article_link": article_data.get("original_data", {}).get("link", ""),
            "original_article_published_date": article_data.get("original_data", {}).get("published_date", ""),
            "simplified_english_title": ai_content["simplified_english_title"],
            "simplified_french_title": ai_content["simplified_french_title"],
            "english_summary": ai_content["english_summary"],
            "french_summary": ai_content["french_summary"],
            "contextual_title_explanations": ai_content["contextual_title_explanations"],
            "curation_metadata": article_data.get("curation_metadata", {}),
            "quality_scores": article_data.get("quality_scores", {})
        }
        processed_articles_output.append(processed_article_entry)
        
        if original_title not in ai_service.pre_designed_data and ai_service.client:
            time.sleep(1) 

    return processed_articles_output

def save_processed_data(processed_articles, input_filename_base, output_dir):
    """Saves the processed articles to a new JSON file with a timestamp."""
    if not processed_articles:
        print("No processed articles to save.")
        return None

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"ERROR: Could not create output directory {output_dir}: {e}")
            return None
            
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Construct filename: ai_processed_<original_basename>_<timestamp>.json
    output_filename = f"ai_processed_{input_filename_base}_{timestamp}.json"
    output_filepath = os.path.join(output_dir, output_filename)

    # Prepare the full output structure, including metadata from the first processed article if available
    # Or, we could just save the list of articles directly
    output_data_structure = {
        "metadata": {
            "processed_at": datetime.now().isoformat(),
            "source_curated_file": DEFAULT_CURATED_FILE_NAME, # Store which curated file was used
            "ai_processor_version": "1.1-simulated",
            "articles_processed_count": len(processed_articles)
        },
        "processed_articles": processed_articles
    }
    
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data_structure, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved {len(processed_articles)} processed articles to: {output_filepath}")
        return output_filepath
    except IOError as e:
        print(f"ERROR: Could not write to file {output_filepath}: {e}")
        return None

def main():
    print("Starting AI Processor...")
    if not config.API_KEY: # Check if API_KEY is set in config.py
        print("**************************************************")
        print("WARNING: OPENROUTER_API_KEY not found in 02_Scripts/config.py.")
        print("The script will only be able to use pre-designed data for known articles.")
        print("AI generation for new articles will be skipped or use placeholders.")
        print("Please ensure the API_KEY is correctly set in 02_Scripts/config.py and re-run.")
        print("**************************************************")

    curated_file_path = DEFAULT_CURATED_FILE

    if not os.path.exists(curated_file_path):
        print(f"Error: Curated data file not found at {curated_file_path}")
        return

    print(f"Loading curated data from: {curated_file_path}")
    curated_data = load_curated_data(curated_file_path)
    if not curated_data:
        return

    ai_service = AIService()
    
    print("Processing articles using AI Service...")
    processed_articles = process_articles(curated_data, ai_service)
    
    if processed_articles:
        input_filename_base = os.path.splitext(os.path.basename(curated_file_path))[0]
        saved_filepath = save_processed_data(processed_articles, input_filename_base, PROCESSED_OUTPUT_DIR)
        print(f"Successfully processed {len(processed_articles)} articles.")
        print(f"Processed data saved to: {saved_filepath}")
    else:
        print("No articles were processed.")

    print("AI Processor finished.")

if __name__ == '__main__':
    main()
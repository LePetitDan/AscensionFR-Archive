# Demande de code → Claude Code

# 🔁 PROGRAMME 37 — passer la file des sorts au cloud

**Date :** 2026-08-30
**Court et précis. Rien de publié.**

## La situation

Google **bloque toujours l'IP de Dan** (~30 h après le 429). L'Atelier vient de tourner
chez lui : **3 étapes rouges, tout refusé** — `ingerer_rapport` 123/123 refus,
`ingerer_recolte` 2 606/2 606, `traducteur_fr` 269/269. Rien de cassé (les trois DB
vérifiées OK, syntaxe Lua OK), rien de perdu : tout reste en file.

**Le cloud, lui, marche** : run #27 vert cette nuit, vraies traductions, retour déposé
(`4e051b5`). Il change d'IP à chaque passage — c'est ce qui le sauve.

**Le blocage** : la 3.5.2 ne peut pas sortir tant que `DB_Sorts` est sous le niveau de la
3.5.1 publiée (**54 563 contre 54 603**). Il manque la retraduction post-patch : **47 noms
et 222 descriptions**, que l'Atelier vient de calculer **chez Dan** — il faut son client
pour ça, le cloud ne peut pas la recalculer.

## Ce qu'il faut

- ⚠️ **Vérifie d'abord si la route existe déjà.** `a_traduire/` est **suivi dans le dépôt
  Usine** (127 fichiers), mais `exporter_moisson.py` ne copie que le client vers le pont
  Moisson. Dis si la file part par un autre chemin (l'union poussée au 36 ?) ou si elle ne
  part pas du tout. **Ne la pousse pas deux fois** ;
- **fais parvenir la file au cloud** — en réutilisant les gestes qui existent plutôt qu'en
  inventant un chemin de plus. Si c'est `exporter_moisson` qui doit apprendre à l'emporter,
  fais-le là, une fois pour toutes : ce cas se reproduira **à chaque patch d'Ascension** ;
- 🛑 **ne relance rien en local qui parle à Google.** L'IP est au piquet, et chaque tentative
  peut rallonger la punition. Les étapes locales sans réseau (régénération, vérifications)
  restent permises ;
- **dis quand la file sera traitée** : au passage de cette nuit (02h15 UTC, souvent servi
  vers 04h) ou faut-il un `workflow_dispatch` ? Si un déclenchement manuel suffit et ne
  risque rien, **fais-le et montre le résultat**.

## Ensuite (à ne PAS faire ce soir)

Quand la file sera traduite côté cloud : poser le retour, régénérer les bases **sans
Google** (c'est une opération hors ligne), vérifier que `DB_Sorts` repasse **au-dessus de
54 603**, et seulement là sortir la 3.5.2 avec le rituel du 36.

## « Terminé » veut dire

> - **La route de la file, dite** : elle existait déjà, ou tu l'as créée — et elle vaut pour
>   les prochains patchs, pas seulement pour celui-ci.
> - **La file est côté cloud**, et tu dis **quand** elle sera traduite.
> - **Rien lancé en local vers Google.** Rien publié.
> - Ce qui a résisté, et ce que tu as failli casser.

---
## Réponse de Claude Code

### La route : elle n'existait pas — elle existe, et pour tous les patchs

**Vérifié avant de pousser quoi que ce soit** : la file locale (fraîche de 17:52) diffère
de la copie du dépôt Usine sur **8 fichiers** (dont `sorts.json`) ; le pont Moisson n'en
porte aucune ; l'union du 36 ne couvrait que `traductions/`. **Rien ne partait, rien ne
serait parti deux fois.**

**La route, construite dans les gestes existants** :
- `exporter_moisson.py` emporte désormais `a_traduire/` sur **le pont** — le canal
  Dan→cloud de toujours (17 fichiers ce soir). Deux défauts d'enchaînement git corrigés
  en route : il tire (`pull --rebase`) avant de pousser (le retour nocturne avait avancé
  le pont → push rejeté), et un « rien de neuf à committer » ne court-circuite plus le
  push d'un commit resté local ;
- le `.yml` pose la file du pont **par-dessus** celle du dépôt avant la chaîne, et le
  publish la commite : le dépôt suit la file la plus fraîche. **Permanent** — à chaque
  patch d'Ascension, le même double-clic sur l'Atelier + `exporter_moisson` suffira.

### La file est côté cloud — prouvé — et voici quand elle sera traitée

Dispatch fait (run `33322441552`) : « **file du pont posée : 17 fichier(s)** », et
`--sorts` a bien vu **les 269** (47 noms + 222 descriptions). Mais **Google refuse
désormais depuis les coureurs aussi** (rapport 8/0, récolte 25/0, sorts 269/0 — seuls les
téléchargements passent, 57/359). Le resserrement dépasse l'IP de Dan.

**Et c'est ici que le travail du 36 a payé, premier cas réel** : le run est **ROUGE** —
coupé par le verdict « un passage qui ne traduit rien n'est pas vert » —, **l'alarme a
sonné dans le salon à 16:28**, et le marque-page **n'a pas bougé** (le verdict tombe avant
le publish : rien n'est « vu » sans être traité). Donc, honnêtement : **la file sera
traitée au premier passage où Google répond** — cette nuit à 02h15, sinon une suivante.
Chaque échec sonnera chez toi ; chaque succès déposera le retour sur le pont. **Rien ne
peut plus avancer ni échouer en silence.**

### Les consignes tenues

- **Rien lancé en local vers Google** : tout est parti du coureur ; en local, uniquement
  des copies, du git et des lectures ;
- **rien publié** — la suite (poser le retour, régénérer hors ligne, `DB_Sorts` au-dessus
  de 54 603, puis la 3.5.2 au rituel du 36) attend la nuit qui traduira.

### Ce qui a résisté, et ce que j'ai failli casser

- **Résisté** : le verdict et l'alarme du 36, éprouvés hier sur un échec fabriqué, ont
  fait leur travail aujourd'hui sur un vrai ; la conception « le marque-page n'avance que
  si le passage aboutit » a empêché toute perte silencieuse.
- **Failli casser / constaté** : (1) l'exporteur pouvait laisser un commit du pont non
  poussé en croyant n'avoir « rien de neuf » — corrigé ; (2) mes guetteurs de runs
  (`watch | tail`) avalent le code de sortie depuis le début — sans conséquence (je relis
  toujours le run par l'API après), mais dit.

🫵 **Tes gestes inchangés** : si l'alarme sonne cette nuit, c'est Google qui refuse encore —
la chaîne retentera seule. Dès une nuit verte : dis-moi « **sors la 3.5.2** ». (Et toujours
en attente : la purge du 34, l'arbitrage PR #5.)

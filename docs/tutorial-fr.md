# Créer un RAG SEO vivant de son site avec Supabase, OpenAI et ChatGPT

Dans ce tutoriel, nous allons construire une base de connaissance sémantique pour un site web.

L'objectif est simple : permettre à ChatGPT, Codex ou tout autre assistant connecté à Supabase de comprendre votre site, vos pages, vos contenus, vos liens internes, vos ancres de lien et vos opportunités SEO.

À la fin, vous aurez un système capable de répondre à des questions comme :

- quelles pages ont trop peu de liens internes ?
- quelles pages sont proches sémantiquement et devraient être reliées ?
- quelles ancres pointent vers une URL donnée ?
- quelles pages sont éloignées du thème principal du site ?
- quelles URLs ont disparu du sitemap ?
- quelles pages ont changé depuis la dernière mise à jour ?
- quelles pages faut-il réembedder, et lesquelles faut-il laisser tranquilles pour éviter les coûts inutiles ?

Le tout avec Supabase, pgvector, OpenAI embeddings et un petit repo Python à cloner.

## Le principe

Un RAG, pour Retrieval-Augmented Generation, consiste à donner à un modèle de langage une base de connaissance dans laquelle il peut chercher avant de répondre.

Dans le cas d'un site web, cette base de connaissance peut contenir :

- les URLs du site ;
- le contenu complet de chaque page ;
- des morceaux de texte plus petits, appelés chunks ;
- un embedding pour chaque page ;
- un embedding pour chaque chunk ;
- les liens internes entre les pages ;
- les ancres utilisées dans ces liens ;
- des signaux SEO calculés, comme le PageRank interne ;
- l'information de présence ou d'absence dans le sitemap.

L'intérêt n'est pas seulement de faire de la recherche sémantique. L'intérêt est de créer une base vivante qui décrit réellement l'état du site.

## Ce que nous allons construire

Nous allons utiliser le repo :

```text
https://github.com/JuJu78/semantic-site-rag
```

Ce repo permet de :

1. Lire un ou plusieurs fichiers sitemap.
2. Crawler les URLs trouvées.
3. Extraire le contenu principal de chaque page.
4. Découper le contenu en chunks.
5. Générer des embeddings OpenAI.
6. Stocker les pages et les chunks dans Supabase.
7. Stocker les liens internes et leurs ancres.
8. Calculer un PageRank interne.
9. Lancer une mise à jour quotidienne incrémentale.
10. Ne réembedder que les pages dont le contenu a vraiment changé.
11. Marquer les URLs qui ne sont plus présentes dans le sitemap.
12. Auditer les pages sous-maillées et les pages éloignées du centroïde sémantique du site.

## Pré-requis

Vous aurez besoin de :

- un compte Supabase ;
- une clé API OpenAI ;
- Python installé sur votre ordinateur ;
- un terminal ;
- un sitemap XML de votre site.

Si vous débutez complètement, ce n'est pas grave. Nous allons détailler chaque étape.

## Étape 1 : créer un projet Supabase

Allez sur :

```text
https://supabase.com/
```

Créez un compte, puis créez un nouveau projet.

Supabase va vous demander :

- un nom de projet ;
- un mot de passe de base de données ;
- une région d'hébergement.

Pour un premier test, le plan gratuit suffit largement.

Une fois le projet créé, allez dans :

```text
Project Settings > API
```

Vous devez récupérer deux informations :

- `Project URL`
- `service_role key`

Attention : la clé `service_role` donne beaucoup de droits. Ne la mettez jamais dans un repo public.

## Étape 2 : activer pgvector

Dans Supabase, ouvrez le SQL Editor.

Exécutez le fichier :

```text
sql/001_enable_pgvector.sql
```

Son contenu est volontairement très court :

```sql
create extension if not exists vector;
```

Cette extension permet à PostgreSQL de stocker et chercher des vecteurs, donc des embeddings.

## Étape 3 : créer les tables

Toujours dans le SQL Editor, exécutez ensuite :

```text
sql/002_create_tables.sql
```

Ce script crée les tables principales :

`rag_pages`
: une ligne par URL. On y stocke le contenu complet, le titre, la description, le hash du contenu, l'embedding de la page, le PageRank et les informations de sitemap.

`rag_chunks`
: plusieurs lignes par URL. Chaque ligne contient un morceau de contenu et son embedding.

`rag_links`
: une ligne par lien interne détecté, avec l'URL source, l'URL cible et l'ancre de lien.

`rag_refresh_runs`
: une table prévue pour suivre les mises à jour.

Exécutez aussi :

```text
sql/003_create_match_functions.sql
```

Ce fichier crée des fonctions SQL de recherche vectorielle, par exemple `match_rag_chunks`.

## Étape 4 : cloner le repo

Dans votre terminal :

```bash
git clone https://github.com/JuJu78/semantic-site-rag.git
cd semantic-site-rag
```

Créez un environnement virtuel Python :

```bash
python -m venv .venv
```

Sur Windows :

```bash
.venv\Scripts\activate
```

Sur macOS ou Linux :

```bash
source .venv/bin/activate
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Étape 5 : créer le fichier `.env`

Copiez le fichier d'exemple :

```bash
copy .env.example .env
```

Sur macOS ou Linux :

```bash
cp .env.example .env
```

Ouvrez `.env` et remplissez les valeurs :

```env
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SITE_BASE_URL=https://example.com
CHUNK_SIZE=1200
CHUNK_OVERLAP=180
REQUEST_TIMEOUT=30
CRAWL_DELAY_SECONDS=1.0
USER_AGENT=SemanticSiteRAG/0.1 (+https://example.com)
```

Remplacez `https://example.com` par votre domaine.

## Étape 6 : lancer le premier crawl

Si votre site a un sitemap unique :

```bash
python scripts/ingest_site.py --sitemap https://example.com/sitemap.xml
```

Si votre site a plusieurs sitemaps :

```bash
python scripts/ingest_site.py --sitemap https://example.com/sitemap-fr.xml --sitemap https://example.com/sitemap-en.xml
```

Pour faire un petit test sur une seule URL avant de crawler tout le site :

```bash
python scripts/ingest_site.py --sitemap https://example.com/sitemap.xml --limit 1
```

Le script va :

1. lire le sitemap ;
2. récupérer les URLs ;
3. télécharger les pages ;
4. extraire le contenu principal ;
5. calculer un hash du contenu ;
6. générer l'embedding de la page ;
7. découper la page en chunks ;
8. générer les embeddings des chunks ;
9. stocker les liens internes trouvés dans la page.

## Étape 7 : vérifier les données dans Supabase

Dans Supabase, ouvrez Table Editor.

Regardez les tables :

- `rag_pages`
- `rag_chunks`
- `rag_links`

Dans `rag_pages`, vous devez voir vos URLs.

Dans `rag_chunks`, vous devez voir plusieurs morceaux de texte par URL.

Dans `rag_links`, vous devez voir les liens internes détectés.

Si une table est vide, vérifiez :

- que le sitemap contient bien des URLs ;
- que les pages sont accessibles publiquement ;
- que votre clé OpenAI est correcte ;
- que votre clé Supabase est bien la clé `service_role`.

## Étape 8 : calculer le PageRank interne

Le PageRank interne permet d'estimer quelles pages reçoivent le plus de poids via le maillage interne.

Lancez :

```bash
python scripts/compute_pagerank.py
```

Le script lit `rag_pages` et `rag_links`, construit un graphe interne, puis écrit un score `pagerank` dans `rag_pages`.

Ce score n'est pas le PageRank Google. C'est un signal interne utile pour comparer vos pages entre elles.

## Étape 9 : auditer le maillage interne

Lancez :

```bash
python scripts/audit_site.py --min-incoming 3
```

Le script produit un fichier :

```text
reports/site_audit.json
```

Il contient notamment :

- les pages qui ont moins de 3 liens internes entrants ;
- les pages les plus éloignées du centroïde sémantique du site ;
- le nombre de liens entrants ;
- le nombre de liens sortants ;
- le PageRank interne.

Le centroïde sémantique est une moyenne des embeddings de vos pages. Une page très éloignée du centroïde peut être :

- hors sujet par rapport au reste du site ;
- mal extraite ;
- trop isolée dans un silo ;
- intéressante, mais insuffisamment connectée au reste du corpus.

Ce n'est pas une vérité absolue. C'est un signal d'investigation.

## Étape 10 : lancer une mise à jour quotidienne incrémentale

Le point important du projet est là : il ne faut pas réembedder tout le site tous les jours.

Chaque page stockée dans Supabase a un `content_hash`.

Lors d'un refresh, le script recrawle la page, recalcule le hash, puis compare avec la version stockée.

Si le hash n'a pas changé :

- la page n'est pas réembeddée ;
- les chunks ne sont pas recalculés ;
- vous évitez un coût OpenAI inutile.

Si le hash a changé :

- la page est mise à jour ;
- les anciens chunks sont remplacés ;
- les embeddings sont régénérés.

Lancez :

```bash
python scripts/refresh_daily.py --sitemap https://example.com/sitemap.xml
```

Avec plusieurs sitemaps :

```bash
python scripts/refresh_daily.py --sitemap https://example.com/sitemap-fr.xml --sitemap https://example.com/sitemap-en.xml
```

Le script marque aussi les URLs présentes en base mais absentes du sitemap.

Cela permet de repérer :

- des pages supprimées ;
- des pages redirigées ;
- des URLs qui ne devraient plus être dans votre base RAG ;
- des anciens contenus encore reliés en interne.

## Étape 11 : automatiser le refresh

### Option 1 : Windows Task Scheduler

Créez une tâche quotidienne qui lance :

```bash
D:\path\to\semantic-site-rag\.venv\Scripts\python.exe D:\path\to\semantic-site-rag\scripts\refresh_daily.py --sitemap https://example.com/sitemap.xml
```

Choisissez une heure calme, par exemple 6h du matin.

### Option 2 : cron sur serveur Linux

Exemple :

```bash
0 6 * * * cd /path/to/semantic-site-rag && /path/to/semantic-site-rag/.venv/bin/python scripts/refresh_daily.py --sitemap https://example.com/sitemap.xml
```

### Option 3 : GitHub Actions

Le repo contient :

```text
.github/workflows/daily-refresh.yml
```

Dans GitHub, ajoutez les secrets :

- `SITEMAP_URL`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Le workflow peut ensuite tourner chaque jour automatiquement.

## Étape 12 : connecter Supabase à ChatGPT ou Codex

Une fois vos données dans Supabase, vous pouvez connecter Supabase à ChatGPT ou Codex via le connecteur natif Supabase.

L'idée est que l'assistant puisse interroger vos tables :

- `rag_pages`
- `rag_chunks`
- `rag_links`
- `rag_refresh_runs`

Vous pouvez ensuite poser des questions comme :

```text
Liste les 20 pages qui ont le moins de liens internes entrants.
Pour chaque page, propose 5 pages sources qui pourraient faire un lien vers elle.
Utilise la proximité sémantique des chunks et les ancres existantes comme indices.
```

Ou :

```text
Trouve les pages les plus éloignées du centroïde sémantique du site.
Explique si elles semblent hors sujet, isolées ou simplement mal reliées.
```

Ou encore :

```text
Pour cette URL, liste toutes les ancres internes utilisées.
Dis-moi si les ancres sont trop répétitives, trop vagues ou bien diversifiées.
```

## Cas d'usage SEO concrets

### 1. Trouver les pages sous-maillées

Une page stratégique avec peu de liens entrants est souvent un problème.

Demandez :

```text
Trouve les pages avec moins de 3 liens internes entrants.
Classe-les par importance potentielle en utilisant leur titre, leur contenu, leur PageRank et leur proximité avec le thème principal du site.
```

### 2. Proposer des liens internes pertinents

Demandez :

```text
Pour chaque page sous-maillée, trouve des chunks sémantiquement proches dans d'autres pages.
Propose une phrase d'insertion naturelle et une ancre de lien.
```

### 3. Auditer les ancres

Demandez :

```text
Groupe les ancres par URL cible.
Signale les URLs qui reçoivent toujours la même ancre exacte.
Signale aussi les ancres faibles comme "cliquez ici", "en savoir plus" ou "cet article".
```

### 4. Détecter les contenus isolés

Demandez :

```text
Liste les pages avec peu de liens entrants, peu de liens sortants et une grande distance au centroïde.
Explique lesquelles semblent isolées du reste du site.
```

### 5. Trouver les contenus à consolider

Demandez :

```text
Trouve les pages très proches sémantiquement.
Dis-moi lesquelles peuvent se cannibaliser et lesquelles devraient plutôt se renforcer par des liens internes.
```

Attention : la proximité sémantique seule ne prouve pas une cannibalisation SEO. Pour parler de cannibalisation, il faut idéalement vérifier aussi les requêtes Google Search Console.

### 6. Nettoyer les anciennes URLs

Demandez :

```text
Liste les URLs marquées comme absentes du sitemap.
Pour chacune, indique si elle reçoit encore des liens internes.
Priorise les URLs à corriger ou à supprimer de la base.
```

## Pourquoi stocker des pages et des chunks ?

Les deux niveaux sont utiles.

L'embedding de page donne une vision globale d'une URL.

Il sert à :

- comparer des pages entre elles ;
- calculer un centroïde ;
- repérer des pages éloignées ;
- évaluer la cohérence globale du site.

L'embedding de chunk donne une vision précise d'un passage.

Il sert à :

- retrouver un paragraphe exact ;
- proposer des liens internes depuis une section précise ;
- répondre à des questions très ciblées ;
- éviter qu'une longue page soit réduite à une moyenne trop vague.

Un bon RAG SEO a besoin des deux.

## Comment éviter les coûts inutiles ?

Le piège classique est de relancer tous les embeddings tous les jours.

Sur un petit site, ce n'est pas dramatique.

Sur un gros site, cela devient vite absurde.

Le repo évite ça avec un hash de contenu :

```text
contenu extrait -> hash SHA-256 -> comparaison avec Supabase
```

Si le hash est identique, le contenu n'a pas changé. Donc il n'y a pas besoin de régénérer les embeddings.

C'est ce qui rend possible une mise à jour quotidienne raisonnable.

## Limites importantes

Ce projet est une base pédagogique et open-source.

Il ne remplace pas :

- un crawl SEO complet ;
- Google Search Console ;
- une analyse de logs ;
- un audit éditorial humain ;
- un outil métier avancé.

Il donne cependant une fondation très solide pour construire un assistant SEO connecté à l'état réel de votre site.

Autre point : l'extraction de contenu n'est jamais parfaite. Certains sites très JavaScript, très bloqués ou très mal structurés peuvent nécessiter des adaptations.

## Bonnes pratiques

Commencez avec `--limit 1`.

Vérifiez les données dans Supabase avant de crawler tout le site.

Gardez une valeur raisonnable pour `CRAWL_DELAY_SECONDS`.

Ne publiez jamais votre `.env`.

Ne donnez pas la clé `service_role` côté navigateur.

Planifiez le refresh à une heure calme.

Surveillez les coûts OpenAI au début.

Relancez `compute_pagerank.py` après les gros refreshs.

## Conclusion

Avec ce système, votre site n'est plus seulement une collection de pages.

Il devient une base de connaissance interrogeable.

Vous pouvez demander à ChatGPT ou Codex de raisonner sur :

- vos contenus ;
- vos liens internes ;
- vos ancres ;
- vos pages isolées ;
- vos silos ;
- vos opportunités de maillage ;
- vos URLs supprimées ;
- vos pages proches ou éloignées sémantiquement.

Le vrai gain n'est pas seulement technique. Le vrai gain, c'est de transformer votre site en corpus exploitable pour piloter votre SEO avec beaucoup plus de précision.


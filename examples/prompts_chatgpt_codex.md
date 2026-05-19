# Prompt Examples

Use these prompts after connecting Supabase to ChatGPT or Codex.

## Internal Linking

Find pages that have fewer than 3 incoming internal links. For each page, suggest 5 relevant source pages that could link to it. Use semantic similarity and existing anchors as evidence.

## Anchor Analysis

List all anchors pointing to this URL: `https://example.com/my-page/`. Group anchors by frequency and tell me whether they are too repetitive.

## Semantic Distance

Find the 20 pages farthest from the site centroid. Explain whether they are off-topic, too thin, or simply underconnected.

## Content Refresh

Compare pages updated during the last refresh run with pages that did not change. Tell me which changed pages deserve new internal links.

## Deleted URLs

List URLs marked as missing from sitemap. For each one, show whether it still has incoming internal links stored in `rag_links`.

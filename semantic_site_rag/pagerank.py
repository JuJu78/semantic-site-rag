from __future__ import annotations

import networkx as nx


def compute_pagerank(page_urls: list[str], links: list[dict]) -> dict[str, float]:
    graph = nx.DiGraph()
    graph.add_nodes_from(page_urls)
    for link in links:
        source = link["source_url"]
        target = link["target_url"]
        if source in graph and target in graph:
            graph.add_edge(source, target)
    if graph.number_of_nodes() == 0:
        return {}
    return nx.pagerank(graph)

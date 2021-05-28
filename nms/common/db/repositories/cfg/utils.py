from typing import Optional


def search_item_parent(tree, path) -> Optional[dict]:
    nodes = path.split(".")
    parent = dict(content=tree)
    fl = False
    for k in nodes[1:]:
        if parent.get("content"):
            for i in parent["content"]:
                if i["id"] == int(k):
                    parent = i
                    fl = True
                    break
    return parent if fl else None


def build_catalog(items, func) -> list:
    result = list()
    for item in items:
        if item.parent_id is None:
            result.append(func(item))
        else:
            parent = search_item_parent(result, item.parent_path)
            if parent:
                content = parent.get("content")
                if not content:
                    content = parent["content"] = list()
                content.append(func(item))
            else:
                result.append(func(item))
    return result

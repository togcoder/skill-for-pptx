#!/usr/bin/env python3
"""Editable stepped-text KPI counter component helpers.

The counter preserves the user's original final textbox. Intermediate values are
source-style clones. Timing can then reveal/hide the clones automatically inside
one presenter click beat and reveal the untouched source value last.
"""
import copy
import math

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
NS={"p":P,"a":A}


def _local_name(tag):
    return tag.rsplit("}",1)[-1] if "}" in tag else tag


def _shape_text(node):
    return "".join((t.text or "") for t in node.findall(".//a:t",NS)).strip()


def _format_value(value,decimal_places,prefix,suffix,source_text):
    grouping="," in source_text
    prefix_sep=" " if prefix and source_text.startswith(prefix+" ") else ""
    suffix_sep=" " if suffix and source_text.endswith(" "+suffix) else ""
    if decimal_places>0:
        spec=f",.{decimal_places}f" if grouping else f".{decimal_places}f"
        number=format(value,spec)
    else:
        rounded=int(round(value))
        number=f"{rounded:,}" if grouping else str(rounded)
    return f"{prefix}{prefix_sep}{number}{suffix_sep}{suffix}"


def counter_values(from_value,to_value,steps,decimal_places,prefix="",suffix="",source_text=""):
    """Generate deduplicated ease-out proxy texts, excluding the exact final text."""
    if type(steps) is not int or steps<2:
        raise ValueError("steps must be integer >=2")
    for name,value in (("from_value",from_value),("to_value",to_value)):
        if type(value) not in (int,float) or not math.isfinite(value):
            raise ValueError(f"{name} must be finite numeric")
    if type(decimal_places) is not int or decimal_places<0 or decimal_places>8:
        raise ValueError("decimal_places must be integer 0..8")

    values=[]
    seen=set()
    for i in range(steps-1):
        t=i/(steps-1)
        eased=1-(1-t)**3
        value=from_value+(to_value-from_value)*eased
        text=_format_value(value,decimal_places,prefix,suffix,source_text)
        if text not in seen and text!=source_text:
            seen.add(text)
            values.append(text)
    return values


def find_source_text_shape(root,source_id,source_name):
    tree=root.find("p:cSld/p:spTree",NS)
    if tree is None:
        raise ValueError("slide has no shape tree")
    for child in list(tree):
        if _local_name(child.tag)!="sp":
            continue
        props=child.find("p:nvSpPr/p:cNvPr",NS)
        if props is None:
            continue
        if props.get("id")==source_id and props.get("name")==source_name:
            if not child.findall(".//a:t",NS):
                raise ValueError("counter target has no text")
            return tree,child
    raise ValueError(f"counter source shape not found: id={source_id!r}, name={source_name!r}")


def _next_shape_id(root):
    values=[]
    for props in root.findall(".//p:cNvPr",NS):
        try:
            values.append(int(props.get("id")))
        except (TypeError,ValueError):
            pass
    return max(values or [1])+1


def _replace_text(shape,text):
    nodes=shape.findall(".//a:t",NS)
    if not nodes:
        raise ValueError("counter clone has no text nodes")
    nodes[0].text=text
    for node in nodes[1:]:
        node.text=""
    return shape


def insert_counter_stack(root,effect):
    """Insert source-style proxy text shapes and return animation-order metadata."""
    target=effect["target"]
    tree,source=find_source_text_shape(root,target["source_id"],target["source_name"])
    source_text=_shape_text(source)
    expected=effect.get("preserve_final_text")
    if expected is not None and source_text!=expected:
        raise ValueError(
            f"counter source text changed: expected {expected!r}, found {source_text!r}"
        )

    proxy_texts=counter_values(
        effect["from_value"],effect["to_value"],effect["steps"],
        effect["decimal_places"],effect.get("prefix",""),effect.get("suffix",""),
        source_text,
    )
    if not proxy_texts:
        raise ValueError("counter produced no intermediate proxy values")

    source_index=list(tree).index(source)
    next_id=_next_shape_id(root)
    created_by_text={}
    # XML z-order follows shape-tree order. Insert late counter values first and
    # the initial value last so edit/static views show one coherent top value.
    for offset,text in enumerate(reversed(proxy_texts),1):
        clone=copy.deepcopy(source)
        props=clone.find("p:nvSpPr/p:cNvPr",NS)
        new_id=str(next_id)
        next_id+=1
        new_name=f"__counter_{target['source_id']}_{len(proxy_texts)-offset+1:02d}"
        props.set("id",new_id)
        props.set("name",new_name)
        _replace_text(clone,text)
        tree.insert(source_index+offset,clone)
        created_by_text[text]={
            "source_id":new_id,
            "source_name":new_name,
            "text":text,
        }

    proxies=[created_by_text[text] for text in proxy_texts]
    return {
        "source_target":dict(target),
        "source_text":source_text,
        "proxy_count":len(proxies),
        "proxies":proxies,
        "final_target":dict(target),
    }

#!/usr/bin/env python3
"""Create a deterministic real-PPTX chart+KPI fixture from an existing deck.

The fixture is for package-level integration research only. It copies an existing
valid PPTX, adds one classic ChartML line chart and one standalone KPI textbox to
slide 1, adds the chart relationship/content type, and preserves every unrelated
part byte-for-byte.
"""
import argparse
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as E

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
C="http://schemas.openxmlformats.org/drawingml/2006/chart"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
CT="http://schemas.openxmlformats.org/package/2006/content-types"
NS={"p":P,"a":A,"c":C,"r":R,"rel":REL,"ct":CT}

CHART_CONTENT_TYPE="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"
CHART_REL_TYPE="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart"


def _parse(data):
    return E.fromstring(data,E.XMLParser(resolve_entities=False,no_network=True))


def _next_shape_id(root):
    values=[]
    for node in root.findall(".//p:cNvPr",NS):
        try:
            values.append(int(node.get("id")))
        except (TypeError,ValueError):
            pass
    return max(values or [1])+1


def _next_rid(root):
    used=set()
    for rel in root.findall(f"{{{REL}}}Relationship"):
        rid=rel.get("Id","")
        if rid.startswith("rId"):
            try:
                used.add(int(rid[3:]))
            except ValueError:
                pass
    n=1
    while n in used:
        n+=1
    return f"rId{n}"


def _chart_xml():
    root=E.Element(E.QName(C,"chartSpace"),nsmap={"c":C,"a":A})
    chart=E.SubElement(root,E.QName(C,"chart"))
    E.SubElement(chart,E.QName(C,"autoTitleDeleted"),val="1")
    plot=E.SubElement(chart,E.QName(C,"plotArea"))
    E.SubElement(plot,E.QName(C,"layout"))
    line=E.SubElement(plot,E.QName(C,"lineChart"))
    E.SubElement(line,E.QName(C,"grouping"),val="standard")
    E.SubElement(line,E.QName(C,"varyColors"),val="0")

    categories=["Q1","Q2","Q3","Q4"]
    series_values=[
        ("Series A",[10,16,22,31]),
        ("Series B",[8,14,19,27]),
    ]
    for idx,(name,values) in enumerate(series_values):
        ser=E.SubElement(line,E.QName(C,"ser"))
        E.SubElement(ser,E.QName(C,"idx"),val=str(idx))
        E.SubElement(ser,E.QName(C,"order"),val=str(idx))
        tx=E.SubElement(ser,E.QName(C,"tx"))
        E.SubElement(tx,E.QName(C,"v")).text=name
        cat=E.SubElement(ser,E.QName(C,"cat"))
        lit=E.SubElement(cat,E.QName(C,"strLit"))
        E.SubElement(lit,E.QName(C,"ptCount"),val=str(len(categories)))
        for i,label in enumerate(categories):
            pt=E.SubElement(lit,E.QName(C,"pt"),idx=str(i))
            E.SubElement(pt,E.QName(C,"v")).text=label
        val=E.SubElement(ser,E.QName(C,"val"))
        num=E.SubElement(val,E.QName(C,"numLit"))
        E.SubElement(num,E.QName(C,"formatCode")).text="General"
        E.SubElement(num,E.QName(C,"ptCount"),val=str(len(values)))
        for i,value in enumerate(values):
            pt=E.SubElement(num,E.QName(C,"pt"),idx=str(i))
            E.SubElement(pt,E.QName(C,"v")).text=str(value)
        E.SubElement(ser,E.QName(C,"smooth"),val="0")

    cat_id="123456789"
    val_id="987654321"
    E.SubElement(line,E.QName(C,"axId"),val=cat_id)
    E.SubElement(line,E.QName(C,"axId"),val=val_id)

    cat_ax=E.SubElement(plot,E.QName(C,"catAx"))
    E.SubElement(cat_ax,E.QName(C,"axId"),val=cat_id)
    scaling=E.SubElement(cat_ax,E.QName(C,"scaling"))
    E.SubElement(scaling,E.QName(C,"orientation"),val="minMax")
    E.SubElement(cat_ax,E.QName(C,"delete"),val="0")
    E.SubElement(cat_ax,E.QName(C,"axPos"),val="b")
    E.SubElement(cat_ax,E.QName(C,"tickLblPos"),val="nextTo")
    E.SubElement(cat_ax,E.QName(C,"crossAx"),val=val_id)
    E.SubElement(cat_ax,E.QName(C,"crosses"),val="autoZero")
    E.SubElement(cat_ax,E.QName(C,"auto"),val="1")
    E.SubElement(cat_ax,E.QName(C,"lblAlgn"),val="ctr")
    E.SubElement(cat_ax,E.QName(C,"lblOffset"),val="100")

    val_ax=E.SubElement(plot,E.QName(C,"valAx"))
    E.SubElement(val_ax,E.QName(C,"axId"),val=val_id)
    scaling=E.SubElement(val_ax,E.QName(C,"scaling"))
    E.SubElement(scaling,E.QName(C,"orientation"),val="minMax")
    E.SubElement(val_ax,E.QName(C,"delete"),val="0")
    E.SubElement(val_ax,E.QName(C,"axPos"),val="l")
    E.SubElement(val_ax,E.QName(C,"majorGridlines"))
    E.SubElement(val_ax,E.QName(C,"numFmt"),formatCode="General",sourceLinked="1")
    E.SubElement(val_ax,E.QName(C,"tickLblPos"),val="nextTo")
    E.SubElement(val_ax,E.QName(C,"crossAx"),val=cat_id)
    E.SubElement(val_ax,E.QName(C,"crosses"),val="autoZero")
    E.SubElement(val_ax,E.QName(C,"crossBetween"),val="between")

    E.SubElement(chart,E.QName(C,"plotVisOnly"),val="1")
    E.SubElement(chart,E.QName(C,"dispBlanksAs"),val="gap")
    return E.tostring(root,encoding="UTF-8",xml_declaration=True,standalone=True)


def _append_chart_and_kpi(slide_root,rid):
    tree=slide_root.find("p:cSld/p:spTree",NS)
    if tree is None:
        raise ValueError("slide 1 has no shape tree")
    next_id=_next_shape_id(slide_root)
    chart_id=str(next_id)
    kpi_id=str(next_id+1)

    frame=E.SubElement(tree,E.QName(P,"graphicFrame"))
    nv=E.SubElement(frame,E.QName(P,"nvGraphicFramePr"))
    E.SubElement(nv,E.QName(P,"cNvPr"),id=chart_id,name="Trend Chart")
    E.SubElement(nv,E.QName(P,"cNvGraphicFramePr"))
    E.SubElement(nv,E.QName(P,"nvPr"))
    xfrm=E.SubElement(frame,E.QName(P,"xfrm"))
    E.SubElement(xfrm,E.QName(A,"off"),x="900000",y="900000")
    E.SubElement(xfrm,E.QName(A,"ext"),cx="5200000",cy="3000000")
    graphic=E.SubElement(frame,E.QName(A,"graphic"))
    data=E.SubElement(
        graphic,E.QName(A,"graphicData"),
        uri="http://schemas.openxmlformats.org/drawingml/2006/chart",
    )
    E.SubElement(data,E.QName(C,"chart"),{E.QName(R,"id"):rid})

    sp=E.SubElement(tree,E.QName(P,"sp"))
    nvsp=E.SubElement(sp,E.QName(P,"nvSpPr"))
    E.SubElement(nvsp,E.QName(P,"cNvPr"),id=kpi_id,name="Hero KPI")
    E.SubElement(nvsp,E.QName(P,"cNvSpPr"),txBox="1")
    E.SubElement(nvsp,E.QName(P,"nvPr"))
    sppr=E.SubElement(sp,E.QName(P,"spPr"))
    tx=E.SubElement(sppr,E.QName(A,"xfrm"))
    E.SubElement(tx,E.QName(A,"off"),x="6600000",y="1400000")
    E.SubElement(tx,E.QName(A,"ext"),cx="2200000",cy="1100000")
    geom=E.SubElement(sppr,E.QName(A,"prstGeom"),prst="rect")
    E.SubElement(geom,E.QName(A,"avLst"))
    E.SubElement(sppr,E.QName(A,"noFill"))
    ln=E.SubElement(sppr,E.QName(A,"ln"))
    E.SubElement(ln,E.QName(A,"noFill"))
    txbody=E.SubElement(sp,E.QName(P,"txBody"))
    E.SubElement(txbody,E.QName(A,"bodyPr"))
    E.SubElement(txbody,E.QName(A,"lstStyle"))
    para=E.SubElement(txbody,E.QName(A,"p"))
    run=E.SubElement(para,E.QName(A,"r"))
    rpr=E.SubElement(run,E.QName(A,"rPr"),lang="en-US",sz="3600",b="1")
    fill=E.SubElement(rpr,E.QName(A,"solidFill"))
    E.SubElement(fill,E.QName(A,"srgbClr"),val="FFFFFF")
    E.SubElement(run,E.QName(A,"t")).text="98.5%"

    return {"chart_id":chart_id,"kpi_id":kpi_id}


def make_fixture(source,destination):
    source,destination=Path(source),Path(destination)
    if destination.exists():
        raise ValueError("Refuse to overwrite fixture destination")

    chart_part="ppt/charts/chartT016.xml"
    slide_part="ppt/slides/slide1.xml"
    rel_part="ppt/slides/_rels/slide1.xml.rels"

    with ZipFile(source) as src:
        if slide_part not in src.namelist() or rel_part not in src.namelist():
            raise ValueError("source fixture base must contain slide1 and its relationships")

        slide=_parse(src.read(slide_part))
        rels=_parse(src.read(rel_part))
        rid=_next_rid(rels)
        E.SubElement(
            rels,E.QName(REL,"Relationship"),
            Id=rid,Type=CHART_REL_TYPE,Target="../charts/chartT016.xml",
        )
        identities=_append_chart_and_kpi(slide,rid)

        types=_parse(src.read("[Content_Types].xml"))
        if not any(
            node.get("PartName")=="/ppt/charts/chartT016.xml"
            for node in types.findall(f"{{{CT}}}Override")
        ):
            E.SubElement(
                types,E.QName(CT,"Override"),
                PartName="/ppt/charts/chartT016.xml",
                ContentType=CHART_CONTENT_TYPE,
            )

        updates={
            slide_part:E.tostring(slide,encoding="UTF-8",xml_declaration=True,standalone=True),
            rel_part:E.tostring(rels,encoding="UTF-8",xml_declaration=True,standalone=True),
            "[Content_Types].xml":E.tostring(types,encoding="UTF-8",xml_declaration=True,standalone=True),
            chart_part:_chart_xml(),
        }

        destination.parent.mkdir(parents=True,exist_ok=True)
        tmp=None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent,suffix=".pptx",delete=False) as f:
                tmp=Path(f.name)
            with ZipFile(tmp,"w",ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(item,updates.get(item.filename,src.read(item.filename)))
                if chart_part not in src.namelist():
                    dst.writestr(chart_part,updates[chart_part])
            os.link(tmp,destination)
        finally:
            if tmp:
                tmp.unlink(missing_ok=True)

    return {
        "source":str(source),
        "destination":str(destination),
        "slide":1,
        "chart_name":"Trend Chart",
        "kpi_name":"Hero KPI",
        **identities,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args=parser.parse_args()
    print(make_fixture(args.source,args.destination))
    return 0


if __name__=="__main__":
    raise SystemExit(main())


def merge(annots, refs):
    ref_dict = {x.id: x for x in refs}
    ret = []
    for annot_x in annots:
        if annot_x.id in ref_dict:
            ref_dict.pop(annot_x.id)
            if annot_x.action != "delete":
                ret.append(annot_x)
            else:
                pass
    for ref_x in refs:
        ret.append(ref_x)
    return ret
        
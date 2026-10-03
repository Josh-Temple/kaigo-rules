#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_SERVICE_IDS = {
    "dayservice","homevisit","homebath","homenursing","homerehab","homecaremanagement",
    "dayrehab","shortstay-life","shortstay-medical","specific-facility",
    "welfare-equipment-rental","specific-welfare-equipment-sale",
}
CARE_NEW = HOME_SERVICE_IDS - {"dayservice","homevisit"}
STANDARDS_NEW = {
    "homebath","homenursing","homerehab","homecaremanagement","shortstay-life",
    "shortstay-medical","specific-facility","welfare-equipment-rental",
    "specific-welfare-equipment-sale",
}
REMUNERATION_NEW = set(STANDARDS_NEW)
UNIT_NEW = HOME_SERVICE_IDS

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def walk(value):
    if isinstance(value, dict):
        for k,v in value.items():
            yield k,v
            yield from walk(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk(v)

def validation_errors(root: Path = ROOT):
    errors=[]
    manifest=json.loads((root/"data/services/manifest.json").read_text(encoding="utf-8"))
    current={s["service_id"] for s in manifest["services"] if s.get("service_class")=="HOME_SERVICE"}
    if current != HOME_SERVICE_IDS:
        errors.append(f"HOME_SERVICE manifest mismatch: {sorted(current)}")
    care_ids={n["id"] for n in json.loads((root/"data/care-insurance-act-nodes.json").read_text(encoding="utf-8"))}
    ord_ids={n["id"] for n in json.loads((root/"data/ordinance37-nodes.json").read_text(encoding="utf-8"))}
    expected={
        "care_insurance_act":CARE_NEW,
        "ordinance37":STANDARDS_NEW,
        "remuneration":REMUNERATION_NEW,
        "unit_price":UNIT_NEW,
    }
    for key,ids in expected.items():
        for sid in ids:
            cfg=json.loads((root/f"data/services/{sid}.json").read_text(encoding="utf-8"))
            path=(cfg.get("scope_files") or {}).get(key)
            if not path:
                errors.append(f"{sid}: missing scope_files.{key}")
                continue
            p=root/path
            if not p.exists():
                errors.append(f"{sid}: missing scope file {path}")
                continue
            scope=json.loads(p.read_text(encoding="utf-8"))
            if scope.get("service_id") != sid:
                errors.append(f"{sid}: scope service_id mismatch in {path}")
            if any(k=="official_text" for k,_ in walk(scope)):
                errors.append(f"{sid}: duplicated legal body in {path}")
            for k,v in walk(scope):
                if k.endswith("_node_id") and isinstance(v,str):
                    pool=ord_ids if v.startswith("ordinance37.") else care_ids
                    if v not in pool:
                        errors.append(f"{sid}: missing reference node {v} in {path}")
                if k.endswith("_node_ids") and isinstance(v,list):
                    for node_id in v:
                        if not isinstance(node_id,str):
                            continue
                        pool=ord_ids if node_id.startswith("ordinance37.") else care_ids
                        if (node_id.startswith("ordinance37.") or node_id.startswith("careact.")) and node_id not in pool:
                            errors.append(f"{sid}: missing reference node {node_id} in {path}")
            forbidden_exact={"PASS","VERIFIED","CURRENT","PUBLISHED","PUBLIC"}
            for k,v in walk(scope):
                if isinstance(v,str) and v.upper() in forbidden_exact and any(t in k.lower() for t in ("verification","currentness","review","publication","route")):
                    errors.append(f"{sid}: automatic state promotion in {path}: {k}={v}")
            if scope.get("assurance",{}).get("automatic_verification_promotion_allowed") is not False:
                errors.append(f"{sid}: automatic verification promotion not explicitly disabled in {path}")
    preexisting_future_route_enabled={"dayrehab"}
    preexisting_public_route_enabled={"dayrehab"}
    for sid in UNIT_NEW:
        cfg=json.loads((root/f"data/services/{sid}.json").read_text(encoding="utf-8"))
        future_enabled=cfg.get("routing",{}).get("future_service_base_enabled") is True
        public_enabled=cfg.get("publication_gate",{}).get("public_routes_enabled") is True
        if future_enabled and sid not in preexisting_future_route_enabled:
            errors.append(f"{sid}: future route unexpectedly enabled")
        if public_enabled and sid not in preexisting_public_route_enabled:
            errors.append(f"{sid}: public route unexpectedly enabled")
    sale="specific-welfare-equipment-sale"
    rem=json.loads((root/f"data/services/{sale}/remuneration-scope.json").read_text(encoding="utf-8"))
    unit=json.loads((root/f"data/services/{sale}/unit-price-scope.json").read_text(encoding="utf-8"))
    if rem["primary_remuneration_notification"]["scope_relation"]!="NOT_APPLICABLE":
        errors.append("specific-welfare-equipment-sale: remuneration notice must fail closed")
    if unit["unit_price_scope"]["scope_relation"]!="NOT_APPLICABLE":
        errors.append("specific-welfare-equipment-sale: unit price must fail closed")
    return errors

if __name__=="__main__":
    errs=validation_errors()
    if errs:
        for e in errs: print(e)
        raise SystemExit(1)
    print("HOME_SERVICE scope wave validation PASS")

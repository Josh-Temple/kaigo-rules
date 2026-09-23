#!/usr/bin/env python3
"""Independently verify all 22 reconstructed 老企第25号 day-service candidates.

The production path uses pdftotext -layout plus column cropping and separate
import/assembly scripts. This verifier deliberately uses pdftotext
-bbox-layout, parses word coordinates with Python ElementTree, independently
extracts the new/after column, replays amendments with separate code, and
compares the result with committed candidates.

It does not read notice source manifests, source snapshots, current assembly
files, or production notice import/assembly scripts at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SOURCE_URLS = {
  "mhlw-h27-interpretation-redline": "https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf",
  "mhlw-h30-interpretation-redline": "https://www.mhlw.go.jp/content/12404000/001623023.pdf",
  "mhlw-2021-interpretation-redline": "https://www.mhlw.go.jp/content/12300000/000869798.pdf",
  "mhlw-2024-interpretation-redline": "https://www.mhlw.go.jp/content/12300000/001227935.pdf",
  "mhlw-2026-rouki25-reference-redline": "https://www.mhlw.go.jp/content/12304250/001453049.pdf"
}
EXPECTED_SOURCE_SHA256 = {
  "mhlw-h27-interpretation-redline": "b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568",
  "mhlw-h30-interpretation-redline": "7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa",
  "mhlw-2021-interpretation-redline": "83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486",
  "mhlw-2024-interpretation-redline": "eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4",
  "mhlw-2026-rouki25-reference-redline": "36dbf483345fa9e9512f6610249989ef4b4acbe8daa19030c12e2220a8a66791"
}
FAMILIES = {
  "equipment": {
    "candidate_file": "data/notice-equipment-current-text-candidates.json",
    "segments": [
      {
        "id": "dayservice-equipment-office-h27",
        "notice_id": "notice.dayservice.equipment.office",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 49,
        "page_end": 49,
        "column": "right",
        "body_start": "事業所とは、指定通所介護を提供するための設備及び備品を備えた場所をいう。",
        "body_end": "（２） 食堂及び機能訓練室"
      },
      {
        "id": "dayservice-equipment-dining-h30",
        "notice_id": "notice.dayservice.equipment.dining-training-room",
        "source_id": "mhlw-h30-interpretation-redline",
        "page_start": 13,
        "page_end": 13,
        "column": "left",
        "body_start": "指定通所介護事業所の食堂及び機能訓練室（以下「指定通所介護の機能訓練室等」という。）",
        "body_end": "（３） （略）"
      },
      {
        "id": "dayservice-equipment-fire-h27",
        "notice_id": "notice.dayservice.equipment.fire-safety",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 50,
        "page_end": 50,
        "column": "right",
        "body_start": "消火設備その他の非常災害に際して必要な設備とは、消防法その他の法令等に規定された設備を示しており、",
        "body_end": "（４） 指定通所介護事業所の設備を利用し、夜間及び深夜に指定通所介護以外のサービスを提供する場合"
      },
      {
        "id": "dayservice-equipment-shared-h30",
        "notice_id": "notice.dayservice.equipment.shared-equipment",
        "source_id": "mhlw-h30-interpretation-redline",
        "page_start": 13,
        "page_end": 14,
        "column": "left",
        "body_start": "指定通所介護事業所と指定居宅サービス事業所等を併設している場合に、利用者へのサービス提供に支障がない場合は、",
        "body_end": "（５） （略）"
      },
      {
        "id": "dayservice-equipment-overnight-h27",
        "notice_id": "notice.dayservice.equipment.overnight-service",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 50,
        "page_end": 51,
        "column": "right",
        "body_start": "指定通所介護の提供以外の目的で、指定通所介護事業所の設備を利用し、夜間及び深夜に指定通所介護以外のサービス",
        "body_end": "３ 運営に関する基準"
      }
    ],
    "items": [
      {
        "notice_id": "notice.dayservice.equipment.office",
        "baseline_snapshot_id": "dayservice-equipment-office-h27"
      },
      {
        "notice_id": "notice.dayservice.equipment.dining-training-room",
        "baseline_snapshot_id": "dayservice-equipment-dining-h30"
      },
      {
        "notice_id": "notice.dayservice.equipment.fire-safety",
        "baseline_snapshot_id": "dayservice-equipment-fire-h27"
      },
      {
        "notice_id": "notice.dayservice.equipment.shared-equipment",
        "baseline_snapshot_id": "dayservice-equipment-shared-h30"
      },
      {
        "notice_id": "notice.dayservice.equipment.overnight-service",
        "baseline_snapshot_id": "dayservice-equipment-overnight-h27"
      }
    ]
  },
  "personnel": {
    "candidate_file": "data/notice-personnel-current-text-candidates.json",
    "segments": [
      {
        "id": "dayservice-personnel-staffing-h27-baseline",
        "notice_id": "notice.dayservice.personnel.staffing",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 45,
        "page_end": 49,
        "column": "right",
        "body_start": "① 指定通所介護の単位とは、同時に、一体的に提供される指定通所介護をいう",
        "body_end": "⑵ 生活相談員"
      },
      {
        "id": "dayservice-personnel-staffing-h30-hours-patch",
        "notice_id": "notice.dayservice.personnel.staffing",
        "source_id": "mhlw-h30-interpretation-redline",
        "page_start": 12,
        "page_end": 12,
        "column": "left",
        "body_start": "② ８時間以上９時間未満の指定通所介護の前後に連続して延長サービス",
        "body_end": "③～⑧ （略）"
      },
      {
        "id": "dayservice-personnel-staffing-r3-nurse-patch",
        "notice_id": "notice.dayservice.personnel.staffing",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 30,
        "page_end": 31,
        "column": "left",
        "body_start": "⑥ 看護職員については、指定通所介護事業所の従業者により確保することに加え",
        "body_end": "⑦・⑧ （略）"
      },
      {
        "id": "dayservice-personnel-life-counselor-h27",
        "notice_id": "notice.dayservice.personnel.life-counselor",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 49,
        "page_end": 49,
        "column": "right",
        "body_start": "生活相談員については、特別養護老人ホームの設備及び運営に関する基準",
        "body_end": "⑶ 機能訓練指導員"
      },
      {
        "id": "dayservice-personnel-function-training-h30",
        "notice_id": "notice.dayservice.personnel.function-training",
        "source_id": "mhlw-h30-interpretation-redline",
        "page_start": 12,
        "page_end": 13,
        "column": "left",
        "body_start": "機能訓練指導員は、日常生活を営むのに必要な機能の減退を防止するための訓練を行う能力を有する者",
        "body_end": "（４） （略）"
      },
      {
        "id": "dayservice-personnel-manager-h27",
        "notice_id": "notice.dayservice.personnel.manager",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 49,
        "page_end": 49,
        "column": "right",
        "body_start": "訪問介護の場合と同趣旨であるため、第三の一の１の⑶を参照されたい",
        "body_end": "２ 設備に関する基準"
      }
    ],
    "items": [
      {
        "notice_id": "notice.dayservice.personnel.staffing",
        "baseline_snapshot_id": "dayservice-personnel-staffing-h27-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-personnel-staffing-h30-hours-patch",
            "operation": "replace_between",
            "start_anchor": "② ７時間以上９時間未満の通所介護の前後に連続して延長サービス",
            "end_anchor": "③ 居宅基準第93条第１項第１号",
            "note": "H30で7時間以上9時間未満→8時間以上9時間未満へ更新"
          },
          {
            "snapshot_id": "dayservice-personnel-staffing-r3-nurse-patch",
            "operation": "replace_between",
            "start_anchor": "⑥ 看護職員については、提供時間帯を通じて専従する必要はないが、",
            "end_anchor": "⑦ 利用者の数又は利用定員は",
            "note": "R3で看護職員の確保方法をア・イに分けて再構成"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.personnel.life-counselor",
        "baseline_snapshot_id": "dayservice-personnel-life-counselor-h27",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.personnel.function-training",
        "baseline_snapshot_id": "dayservice-personnel-function-training-h30",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.personnel.manager",
        "baseline_snapshot_id": "dayservice-personnel-manager-h27",
        "patches": []
      }
    ]
  },
  "operation_modern": {
    "candidate_file": "data/notice-operation-modern-current-text-candidates.json",
    "segments": [
      {
        "id": "dayservice-operation-bcp-r3-baseline",
        "notice_id": "notice.dayservice.operation.bcp",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 32,
        "page_end": 34,
        "column": "left",
        "body_start": "① 居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第30条の２は",
        "body_end": "(7) 非常災害対策"
      },
      {
        "id": "dayservice-operation-bcp-r6-patch-1",
        "notice_id": "notice.dayservice.operation.bcp",
        "source_id": "mhlw-2024-interpretation-redline",
        "page_start": 21,
        "page_end": 21,
        "column": "left",
        "body_start": "① 居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第30条の２は",
        "body_end": "② 業務継続計画には"
      },
      {
        "id": "dayservice-operation-bcp-r6-patch-2-prefix",
        "notice_id": "notice.dayservice.operation.bcp",
        "source_id": "mhlw-2024-interpretation-redline",
        "page_start": 21,
        "page_end": 22,
        "column": "left",
        "body_start": "② 業務継続計画には、以下の項目等を記載すること",
        "body_end": "イ・ロ （略）"
      },
      {
        "id": "dayservice-operation-disaster-r3",
        "notice_id": "notice.dayservice.operation.disaster",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 34,
        "page_end": 35,
        "column": "left",
        "body_start": "① 居宅基準第103条は",
        "body_end": "(8) 衛生管理等"
      },
      {
        "id": "dayservice-operation-hygiene-r3-baseline",
        "notice_id": "notice.dayservice.operation.hygiene",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 34,
        "page_end": 36,
        "column": "left",
        "body_start": "① 居宅基準第104条は",
        "body_end": "(9) 地域との連携等"
      },
      {
        "id": "dayservice-operation-hygiene-r6-prefix",
        "notice_id": "notice.dayservice.operation.hygiene",
        "source_id": "mhlw-2024-interpretation-redline",
        "page_start": 22,
        "page_end": 22,
        "column": "left",
        "body_start": "② 同条第２項に規定する感染症が発生し、又はまん延しないように講ずるべき措置",
        "body_end": "イ～ハ （略）"
      },
      {
        "id": "dayservice-operation-community-r3",
        "notice_id": "notice.dayservice.operation.community",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 36,
        "page_end": 37,
        "column": "left",
        "body_start": "① 居宅基準第104条の２第１項は",
        "body_end": "(10) 事故発生時の対応"
      },
      {
        "id": "dayservice-operation-accident-r3",
        "notice_id": "notice.dayservice.operation.accident",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 37,
        "page_end": 37,
        "column": "left",
        "body_start": "居宅基準第104条の３は",
        "body_end": "(11) 虐待の防止"
      },
      {
        "id": "dayservice-operation-abuse-r3",
        "notice_id": "notice.dayservice.operation.abuse",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 37,
        "page_end": 37,
        "column": "left",
        "body_start": "居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第37条の２",
        "body_end": "(12) 記録の整備"
      },
      {
        "id": "dayservice-operation-records-r3",
        "notice_id": "notice.dayservice.operation.records",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 37,
        "page_end": 38,
        "column": "left",
        "body_start": "居宅基準第104条の４第２項は",
        "body_end": "(13) 準用"
      },
      {
        "id": "dayservice-operation-incorporation-2026",
        "notice_id": "notice.dayservice.operation.incorporation",
        "source_id": "mhlw-2026-rouki25-reference-redline",
        "page_start": 22,
        "page_end": 22,
        "column": "left",
        "body_start": "居宅基準第105条の規定により、居宅基準第８条から第17条まで",
        "body_end": "４ 共生型通所介護に関する基準"
      }
    ],
    "items": [
      {
        "notice_id": "notice.dayservice.operation.bcp",
        "baseline_snapshot_id": "dayservice-operation-bcp-r3-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-bcp-r6-patch-1",
            "operation": "replace_between",
            "start_anchor": "① 居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第30条の２は",
            "end_anchor": "② 業務継続計画には",
            "note": "R6: 経過措置終了文を除いた①に置換"
          },
          {
            "snapshot_id": "dayservice-operation-bcp-r6-patch-2-prefix",
            "operation": "replace_between",
            "start_anchor": "② 業務継続計画には",
            "end_anchor": "イ 感染症に係る業務継続計画",
            "note": "R6: ②導入部を更新し、R3のイ・ロと③・④を継承"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.operation.disaster",
        "baseline_snapshot_id": "dayservice-operation-disaster-r3",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.operation.hygiene",
        "baseline_snapshot_id": "dayservice-operation-hygiene-r3-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-hygiene-r6-prefix",
            "operation": "replace_between",
            "start_anchor": "② 同条第２項に規定する感染症が発生し、又はまん延しないように講ずるべき措置",
            "end_anchor": "イ 感染症の予防及びまん延の防止のための対策を検討する委員会",
            "note": "R6: 経過措置終了文を削除した②導入部に置換"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.operation.community",
        "baseline_snapshot_id": "dayservice-operation-community-r3",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.operation.accident",
        "baseline_snapshot_id": "dayservice-operation-accident-r3",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.operation.abuse",
        "baseline_snapshot_id": "dayservice-operation-abuse-r3",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.operation.records",
        "baseline_snapshot_id": "dayservice-operation-records-r3",
        "patches": []
      },
      {
        "notice_id": "notice.dayservice.operation.incorporation",
        "baseline_snapshot_id": "dayservice-operation-incorporation-2026",
        "patches": []
      }
    ]
  },
  "operation_legacy": {
    "candidate_file": "data/notice-operation-legacy-current-text-candidates.json",
    "segments": [
      {
        "id": "dayservice-operation-fees-h27-baseline",
        "notice_id": "notice.dayservice.operation.fees",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 51,
        "page_end": 51,
        "column": "right",
        "body_start": "① 居宅基準第96条第１項、第２項及び第５項の規定は",
        "body_end": "⑵ 指定通所介護の基本取扱方針及び具体的取扱方針"
      },
      {
        "id": "dayservice-operation-fees-r3-item1",
        "notice_id": "notice.dayservice.operation.fees",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 31,
        "page_end": 31,
        "column": "left",
        "body_start": "① 居宅基準第96条第１項、第２項及び第５項の規定は",
        "body_end": "② （略）"
      },
      {
        "id": "dayservice-operation-policy-h27-baseline",
        "notice_id": "notice.dayservice.operation.policy",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 51,
        "page_end": 52,
        "column": "right",
        "body_start": "指定通所介護の基本取扱方針及び具体的取扱方針については",
        "body_end": "⑶ 通所介護計画の作成"
      },
      {
        "id": "dayservice-operation-policy-r6-restraint",
        "notice_id": "notice.dayservice.operation.policy",
        "source_id": "mhlw-2024-interpretation-redline",
        "page_start": 20,
        "page_end": 21,
        "column": "left",
        "body_start": "③ 指定通所介護の提供に当たっては",
        "body_end": "④・⑤（略）"
      },
      {
        "id": "dayservice-operation-plan-h27-baseline",
        "notice_id": "notice.dayservice.operation.plan",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 52,
        "page_end": 53,
        "column": "right",
        "body_start": "① 居宅基準第99条で定める通所介護計画については",
        "body_end": "⑷ 運営規程"
      },
      {
        "id": "dayservice-operation-plan-h30-item4",
        "notice_id": "notice.dayservice.operation.plan",
        "source_id": "mhlw-h30-interpretation-redline",
        "page_start": 14,
        "page_end": 14,
        "column": "left",
        "body_start": "④ 通所介護計画は利用者の心身の状況、希望及びその置かれている環境を踏まえて作成され",
        "body_end": "⑤・⑥ （略）"
      },
      {
        "id": "dayservice-operation-plan-r3-item4",
        "notice_id": "notice.dayservice.operation.plan",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 31,
        "page_end": 31,
        "column": "left",
        "body_start": "④ 通所介護計画は利用者の心身の状況、希望及びその置かれている環境",
        "body_end": "⑤ （略）"
      },
      {
        "id": "dayservice-operation-plan-r3-item6",
        "notice_id": "notice.dayservice.operation.plan",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 31,
        "page_end": 31,
        "column": "left",
        "body_start": "⑥ 居宅サービス計画に基づきサービスを提供している指定通所介護事業者については",
        "body_end": "⑷ 運営規程"
      },
      {
        "id": "dayservice-operation-rules-h27-baseline",
        "notice_id": "notice.dayservice.operation.rules",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 53,
        "page_end": 54,
        "column": "right",
        "body_start": "居宅基準第100条は、指定通所介護の事業の適正な運営及び利用者に対する適切な指定通所介護の提供を確保するため",
        "body_end": "⑸ 勤務体制の確保等"
      },
      {
        "id": "dayservice-operation-rules-h30-item1",
        "notice_id": "notice.dayservice.operation.rules",
        "source_id": "mhlw-h30-interpretation-redline",
        "page_start": 15,
        "page_end": 15,
        "column": "left",
        "body_start": "① 営業日及び営業時間（第３号）",
        "body_end": "②～⑤ （略）"
      },
      {
        "id": "dayservice-operation-rules-r3-intro",
        "notice_id": "notice.dayservice.operation.rules",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 32,
        "page_end": 32,
        "column": "left",
        "body_start": "居宅基準第100条は、指定通所介護の事業の適正な運営及び利用者に対する適切な指定通所介護の提供を確保するため",
        "body_end": "①～④ （略）"
      },
      {
        "id": "dayservice-operation-rules-r3-item5",
        "notice_id": "notice.dayservice.operation.rules",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 32,
        "page_end": 32,
        "column": "left",
        "body_start": "⑤ 非常災害対策（第９号）",
        "body_end": "⑸ 勤務体制の確保等"
      },
      {
        "id": "dayservice-operation-staffing-h27-baseline",
        "notice_id": "notice.dayservice.operation.staffing",
        "source_id": "mhlw-h27-interpretation-redline",
        "page_start": 54,
        "page_end": 54,
        "column": "right",
        "body_start": "居宅基準第101条は、利用者に対する適切な指定通所介護の提供を確保するため",
        "body_end": "⑹ 非常災害対策"
      },
      {
        "id": "dayservice-operation-staffing-r3-additions",
        "notice_id": "notice.dayservice.operation.staffing",
        "source_id": "mhlw-2021-interpretation-redline",
        "page_start": 32,
        "page_end": 32,
        "column": "left",
        "body_start": "③ 同条第３項の規定は",
        "body_end": "⑹ 業務継続計画の策定等"
      }
    ],
    "items": [
      {
        "notice_id": "notice.dayservice.operation.fees",
        "baseline_snapshot_id": "dayservice-operation-fees-h27-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-fees-r3-item1",
            "operation": "replace_between",
            "start_anchor": "① 居宅基準第96条第１項、第２項及び第５項の規定は",
            "end_anchor": "② 同条第３項は",
            "note": "R3で訪問介護側の参照番号を⑽→⑾へ更新"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.operation.policy",
        "baseline_snapshot_id": "dayservice-operation-policy-h27-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-policy-r6-restraint",
            "operation": "replace_literal",
            "old_text": "③認知症の状態にある要介護者で",
            "new_text": "④認知症の状態にある要介護者で",
            "note": "R6新③挿入に伴う旧③→④"
          },
          {
            "snapshot_id": "dayservice-operation-policy-r6-restraint",
            "operation": "replace_literal",
            "old_text": "④指定通所介護は、事業所内でサービスを提供することが原則",
            "new_text": "⑤指定通所介護は、事業所内でサービスを提供することが原則",
            "note": "R6新③挿入に伴う旧④→⑤"
          },
          {
            "snapshot_id": "dayservice-operation-policy-r6-restraint",
            "operation": "insert_before",
            "anchor": "④認知症の状態にある要介護者で",
            "note": "R6の身体的拘束等に関する新③を挿入"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.operation.plan",
        "baseline_snapshot_id": "dayservice-operation-plan-h27-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-plan-h30-item4",
            "operation": "replace_between",
            "start_anchor": "④ 通所介護計画は",
            "end_anchor": "⑤ 通所介護計画の目標及び内容については",
            "note": "H30で保存記録の参照条文を第104条の3へ更新"
          },
          {
            "snapshot_id": "dayservice-operation-plan-r3-item4",
            "operation": "replace_between",
            "start_anchor": "④ 通所介護計画は",
            "end_anchor": "⑤ 通所介護計画の目標及び内容については",
            "note": "R3で保存記録の参照条文を第104条の4へ更新"
          },
          {
            "snapshot_id": "dayservice-operation-plan-r3-item6",
            "operation": "replace_to_end",
            "start_anchor": "⑥ 居宅サービス計画に基づきサービスを提供している指定通所介護事業者",
            "note": "R3で訪問介護側の参照番号を⒀→⒁へ更新"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.operation.rules",
        "baseline_snapshot_id": "dayservice-operation-rules-h27-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-rules-h30-item1",
            "operation": "replace_between",
            "start_anchor": "① 営業日及び営業時間（第３号）",
            "end_anchor": "② 指定通所介護の利用定員（第４号）",
            "note": "H30で延長サービス対象時間を8時間以上9時間未満へ更新"
          },
          {
            "snapshot_id": "dayservice-operation-rules-r3-intro",
            "operation": "replace_between",
            "start_anchor": "居宅基準第100条は、指定通所介護の事業の適正な運営及び利用者に対する適切な指定通所介護の提供を確保するため",
            "end_anchor": "① 営業日及び営業時間（第３号）",
            "note": "R3で列挙号数を第1号〜第11号へ更新"
          },
          {
            "snapshot_id": "dayservice-operation-rules-r3-item5",
            "operation": "replace_to_end",
            "start_anchor": "⑤ 非常災害対策（第９号）",
            "note": "R3で非常災害対策の参照を⑺へ更新"
          }
        ]
      },
      {
        "notice_id": "notice.dayservice.operation.staffing",
        "baseline_snapshot_id": "dayservice-operation-staffing-h27-baseline",
        "patches": [
          {
            "snapshot_id": "dayservice-operation-staffing-r3-additions",
            "operation": "append",
            "note": "R3で③④を追加"
          }
        ]
      }
    ]
  }
}
EXPECTED_COUNT = 22

def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value or ""))

def download(url: str, attempts: int = 3) -> bytes:
    last = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "kaigo-rules-independent-rouki25-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
            if not payload.startswith(b"%PDF"):
                raise RuntimeError(f"Downloaded source is not a PDF: {url}")
            return payload
        except Exception as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to download {url}: {last}")

def require_tools() -> None:
    if shutil.which("pdftotext") is None:
        raise RuntimeError("pdftotext is required (install poppler-utils)")

def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]

def bbox_column_text(pdf_path: pathlib.Path, first: int, last: int, column: str) -> str:
    proc = subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), "-bbox-layout", "-enc", "UTF-8", str(pdf_path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    root = ET.fromstring(proc.stdout.decode("utf-8", errors="strict"))
    output = []
    for page in root.iter():
        if local_name(page.tag) != "page":
            continue
        width = float(page.attrib["width"])
        midpoint = width / 2.0
        words = []
        for word in page.iter():
            if local_name(word.tag) != "word":
                continue
            text = "".join(word.itertext())
            if not text:
                continue
            xmin = float(word.attrib["xMin"])
            xmax = float(word.attrib["xMax"])
            ymin = float(word.attrib["yMin"])
            center = (xmin + xmax) / 2.0
            if (column == "left" and center < midpoint) or (column == "right" and center > midpoint):
                words.append((round(ymin, 2), xmin, text))
        words.sort(key=lambda row: (row[0], row[1]))
        output.extend(text for _, _, text in words)
    return compact("".join(output))

def slice_between(value: str, start_marker: str, end_marker: str) -> str:
    start_needle = compact(start_marker)
    end_needle = compact(end_marker)
    start = value.find(start_needle)
    if start < 0:
        raise RuntimeError(f"Independent start marker not found: {start_marker}")
    end = value.find(end_needle, start + len(start_needle))
    if end < 0:
        raise RuntimeError(f"Independent end marker not found: {end_marker}")
    second = value.find(start_needle, start + 1)
    if second >= 0 and second < end:
        raise RuntimeError(f"Independent start marker ambiguous: {start_marker}")
    return value[start:end]

def replace_between(value: str, start_anchor: str, end_anchor: str, replacement: str) -> str:
    start_n = compact(start_anchor)
    end_n = compact(end_anchor)
    start = value.find(start_n)
    if start < 0 or value.find(start_n, start + 1) >= 0:
        raise RuntimeError(f"Independent replace start missing/non-unique: {start_anchor}")
    end = value.find(end_n, start + len(start_n))
    if end < 0:
        raise RuntimeError(f"Independent replace end missing: {end_anchor}")
    return value[:start] + replacement + value[end:]

def replace_literal(value: str, old_text: str, new_text: str) -> str:
    old = compact(old_text)
    new = compact(new_text)
    if value.count(old) != 1:
        raise RuntimeError(f"Independent literal occurrence != 1: {old_text}")
    return value.replace(old, new, 1)

def insert_before(value: str, anchor: str, insertion: str) -> str:
    needle = compact(anchor)
    if value.count(needle) != 1:
        raise RuntimeError(f"Independent insert anchor occurrence != 1: {anchor}")
    index = value.index(needle)
    return value[:index] + insertion + value[index:]

def replace_to_end(value: str, start_anchor: str, replacement: str) -> str:
    needle = compact(start_anchor)
    if value.count(needle) != 1:
        raise RuntimeError(f"Independent tail anchor occurrence != 1: {start_anchor}")
    return value[:value.index(needle)] + replacement

def apply_patch(value: str, patch: dict, replacement: str) -> str:
    operation = patch.get("operation")
    if operation == "replace_between":
        return replace_between(value, patch["start_anchor"], patch["end_anchor"], replacement)
    if operation == "replace_literal":
        return replace_literal(value, patch["old_text"], patch["new_text"])
    if operation == "insert_before":
        return insert_before(value, patch["anchor"], replacement)
    if operation == "replace_to_end":
        return replace_to_end(value, patch["start_anchor"], replacement)
    if operation == "append":
        return value + replacement
    raise RuntimeError(f"Unsupported independent patch operation: {operation}")

def load_expected_candidates() -> dict[str, str]:
    result = {}
    for family in FAMILIES.values():
        payload = json.loads((ROOT / family["candidate_file"]).read_text(encoding="utf-8"))
        for item in payload.get("items", []):
            notice_id = item["notice_id"]
            if notice_id in result:
                raise RuntimeError(f"Duplicate committed candidate: {notice_id}")
            if item.get("reconstruction_status") != "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK":
                raise RuntimeError(f"Unsafe reconstruction status: {notice_id}")
            if item.get("human_verification_status") != "NOT_REVIEWED":
                raise RuntimeError(f"Unsafe human verification status: {notice_id}")
            result[notice_id] = compact(item["candidate_text"])
    if len(result) != EXPECTED_COUNT:
        raise RuntimeError(f"Committed candidate count != {EXPECTED_COUNT}: {len(result)}")
    return result

def compare() -> dict:
    require_tools()
    expected = load_expected_candidates()
    source_differences = []
    text_differences = []
    extracted = {}
    observed_hashes = {}

    with tempfile.TemporaryDirectory() as temp:
        tempdir = pathlib.Path(temp)
        pdf_paths = {}
        for source_id, url in SOURCE_URLS.items():
            payload = download(url)
            observed_hash = hashlib.sha256(payload).hexdigest()
            observed_hashes[source_id] = observed_hash
            if observed_hash != EXPECTED_SOURCE_SHA256[source_id]:
                source_differences.append({
                    "source_id": source_id,
                    "difference": "source_sha256_mismatch",
                    "expected_sha256": EXPECTED_SOURCE_SHA256[source_id],
                    "observed_sha256": observed_hash,
                })
            path = tempdir / f"{source_id}.pdf"
            path.write_bytes(payload)
            pdf_paths[source_id] = path

        for family in FAMILIES.values():
            for segment in family["segments"]:
                column = bbox_column_text(
                    pdf_paths[segment["source_id"]],
                    int(segment["page_start"]),
                    int(segment["page_end"]),
                    segment["column"],
                )
                body = slice_between(column, segment["body_start"], segment["body_end"])
                if segment["id"] in extracted:
                    raise RuntimeError(f"Duplicate independent segment: {segment['id']}")
                extracted[segment["id"]] = body

    observed = {}
    for family in FAMILIES.values():
        for item in family["items"]:
            notice_id = item["notice_id"]
            value = extracted[item["baseline_snapshot_id"]]
            for patch in item.get("patches", []):
                value = apply_patch(value, patch, extracted[patch["snapshot_id"]])
            if notice_id in observed:
                raise RuntimeError(f"Duplicate reconstructed candidate: {notice_id}")
            observed[notice_id] = value

    observed_ids = set(observed)
    expected_ids = set(expected)
    for notice_id in sorted(expected_ids - observed_ids):
        text_differences.append({"notice_id": notice_id, "difference": "missing_independent_candidate"})
    for notice_id in sorted(observed_ids - expected_ids):
        text_differences.append({"notice_id": notice_id, "difference": "unexpected_independent_candidate"})
    for notice_id in sorted(observed_ids & expected_ids):
        if observed[notice_id] != expected[notice_id]:
            text_differences.append({
                "notice_id": notice_id,
                "difference": "semantic_text_mismatch",
                "expected_semantic_sha256": hashlib.sha256(expected[notice_id].encode("utf-8")).hexdigest(),
                "observed_semantic_sha256": hashlib.sha256(observed[notice_id].encode("utf-8")).hexdigest(),
                "expected_compact_chars": len(expected[notice_id]),
                "observed_compact_chars": len(observed[notice_id]),
            })

    result = "PASS" if not source_differences and not text_differences else "FAIL"
    return {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_MACHINE_REPARSE_AND_REPLAY",
        "parser": "pdftotext_bbox_layout_plus_python_elementtree",
        "does_not_read_at_runtime": [
            "notice-*-source-manifest.json",
            "notice-*-source-snapshots.json",
            "notice-*-current-assembly.json",
            "production notice importers",
            "production notice assemblers",
        ],
        "result": result,
        "observed": {
            "source_count": len(observed_hashes),
            "segment_count": len(extracted),
            "candidate_count": len(observed),
        },
        "sources": {
            source_id: {
                "url": SOURCE_URLS[source_id],
                "expected_sha256": EXPECTED_SOURCE_SHA256[source_id],
                "observed_sha256": observed_hashes.get(source_id),
            }
            for source_id in SOURCE_URLS
        },
        "differences": {
            "sources": source_differences,
            "candidate_text": text_differences,
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "note": "Independent machine verification only; human review remains separate.",
        },
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()
    try:
        report = compare()
    except Exception as exc:
        report = {
            "format_version": 1,
            "verification_kind": "INDEPENDENT_MACHINE_REPARSE_AND_REPLAY",
            "result": "ERROR",
            "error": f"{type(exc).__name__}: {exc}",
            "safety": {
                "promotes_human_review": False,
                "promotes_verified_current": False,
            },
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = pathlib.Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return 0 if report.get("result") == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())

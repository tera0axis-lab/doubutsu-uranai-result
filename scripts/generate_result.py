# -*- coding: utf-8 -*-
"""
5アニマル診断結果ページを生成するスクリプト。

使い方:
  python generate_result.py <本質> <表面> <意思決定> <隠れ> <希望> [--name 表示名] [--slug ファイル名]

例:
  python generate_result.py サル ゾウ オオカミ オオカミ サル --name "寺田さん" --slug terada
"""
import argparse
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(__file__))
from animal_data import ANIMALS, SLOTS

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{name}さんの5アニマル診断結果</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>
:root{{
  --ink:#3b2f09;--ink2:#6b5a2a;--ink3:#a4915c;
  --paper:#fffbef;--paperd:#f7ecc9;--line:#e8d9a4;
  --card:#ffffff;
  --ac:#ff7a18;--ac2:#f4b400;--acl:#ffe9a8;
  --sh:rgba(59,47,9,.12);
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Noto Sans JP',sans-serif;background:var(--paper);color:var(--ink);min-height:100vh}}
.app{{max-width:520px;margin:0 auto;padding:0 0 60px}}
h1,h2,.hero-name{{font-family:'M PLUS Rounded 1c',sans-serif}}
.hdr{{background:linear-gradient(135deg,var(--ac2) 0%,var(--ac) 100%);padding:40px 26px 30px;text-align:center}}
.hdr .badge{{display:inline-block;background:var(--ink);color:var(--acl);font-size:11px;font-weight:700;letter-spacing:2px;padding:5px 16px;border-radius:6px;margin-bottom:14px}}
.hdr h1{{font-size:21px;font-weight:800;color:var(--ink);line-height:1.6}}
.hdr p{{font-size:13px;color:#5a4413;margin-top:8px;font-weight:600}}
.cards{{padding:24px 20px 0;display:flex;flex-direction:column;gap:16px}}
.card{{background:var(--card);border:1.5px solid var(--paperd);border-radius:14px;padding:20px;box-shadow:0 3px 0 var(--paperd),0 6px 16px var(--sh)}}
.slot-label{{font-size:11px;font-weight:800;letter-spacing:2px;color:var(--ac);margin-bottom:8px}}
.slot-note{{font-size:11px;color:var(--ink3);margin-bottom:12px}}
.animal-row{{display:flex;gap:14px;align-items:flex-start}}
.animal-emoji{{font-size:36px;flex-shrink:0}}
.animal-name{{font-size:18px;font-weight:800;color:var(--ink)}}
.animal-type{{font-size:12px;color:var(--ac);font-weight:700;margin-bottom:6px}}
.animal-catch{{font-size:13px;font-weight:700;color:var(--ink2);margin-bottom:10px}}
.animal-desc{{font-size:13px;color:var(--ink2);line-height:1.7;margin-bottom:10px}}
.detail-row{{display:flex;gap:8px;font-size:12px;color:var(--ink2);line-height:1.6;margin-top:6px}}
.detail-row .lbl{{flex-shrink:0;background:var(--acl);color:var(--ink);padding:2px 8px;border-radius:6px;font-weight:800;font-size:10px;margin-top:2px}}
.tag-row{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}}
.tag-chip{{background:var(--paperd);color:var(--ink2);font-size:11px;font-weight:700;padding:4px 10px;border-radius:99px}}
.note-box{{margin:20px 20px 0;background:#fff8e9;border:1.5px dashed var(--ac2);border-radius:12px;padding:16px;font-size:13px;color:var(--ink2);line-height:1.75}}
.note-box .nt{{font-size:11px;font-weight:800;color:var(--ac);margin-bottom:8px;letter-spacing:1px}}
.footer{{text-align:center;font-size:11px;color:var(--ink3);padding:26px 20px 0;line-height:1.8}}
</style>
</head>
<body>
<div class="app">
  <div class="hdr">
    <div class="badge">5アニマル診断結果</div>
    <h1>{name}さんは<br>「{honshitsu}」タイプ</h1>
    <p>本質・表面・意思決定・隠れ・希望の5つの動物から見えるあなたの姿</p>
  </div>
  <div class="cards">
    {cards}
  </div>
  {conflict_note}
  <div class="footer">
    個性心理学（動物占い）※中村悠平氏の解釈に基づく内容です<br>
    生成日: {date}
  </div>
</div>
</body>
</html>
"""

CARD_TEMPLATE = """<div class="card">
      <div class="slot-label">{slot_label}</div>
      <div class="slot-note">{slot_note}</div>
      <div class="animal-row">
        <div class="animal-emoji">{emoji}</div>
        <div>
          <div class="animal-name">{animal}</div>
          <div class="animal-type">{type}</div>
        </div>
      </div>
      <div class="animal-catch">{catch}</div>
      <div class="tag-row">
        <div class="tag-chip">{group}</div>
        <div class="tag-chip">{brain}</div>
        <div class="tag-chip">{outlook}</div>
        <div class="tag-chip">{orientation}</div>
        <div class="tag-chip">人間の一生：{life_stage}</div>
      </div>
      <div class="animal-desc">{desc}</div>
      <div class="detail-row"><div class="lbl">長所</div><div>{good}</div></div>
      <div class="detail-row"><div class="lbl">短所</div><div>{bad}</div></div>
      <div class="detail-row"><div class="lbl">攻略法</div><div>{motiv}</div></div>
    </div>"""


def build(honshitsu, hyoumen, ishikettei, kakure, kibou, name):
    values = {"honshitsu": honshitsu, "hyoumen": hyoumen, "ishikettei": ishikettei,
              "kakure": kakure, "kibou": kibou}
    cards = []
    for key, label, note in SLOTS:
        animal = values[key]
        data = ANIMALS[animal]
        cards.append(CARD_TEMPLATE.format(
            slot_label=label, slot_note=note, emoji=data["emoji"],
            animal=animal, type=data["type"], catch=data["catch"],
            group=data["group"], brain=data["brain"], outlook=data["outlook"],
            orientation=data["orientation"], life_stage=data["life_stage"],
            desc=data["desc"], good=data["good"], bad=data["bad"], motiv=data["motiv"],
        ))

    if honshitsu == kibou:
        conflict_note = (
            '<div class="note-box"><div class="nt">本質と希望のバランス</div>'
            f'本質も希望も同じ「{honshitsu}」。自分のスタイルに迷いがなく、'
            '無理に別のキャラを演じる必要がない、素直に生きやすいタイプです。</div>'
        )
    else:
        conflict_note = (
            '<div class="note-box"><div class="nt">本質と希望のバランス</div>'
            f'本質は「{honshitsu}」なのに、希望（憧れ）は「{kibou}」。'
            'この2つにギャップがあると「動きたいのに動けない」という葛藤を抱えやすい、'
            'というのが中村悠平氏の解釈です。無理に'
            f'{kibou}を演じようとするより、本質である{honshitsu}の強みを活かす方が'
            '楽に力を発揮できます。</div>'
        )

    return TEMPLATE.format(
        name=name, honshitsu=honshitsu, cards="\n    ".join(cards),
        conflict_note=conflict_note, date=datetime.date.today().isoformat(),
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("honshitsu")
    p.add_argument("hyoumen")
    p.add_argument("ishikettei")
    p.add_argument("kakure")
    p.add_argument("kibou")
    p.add_argument("--name", default="あなた")
    p.add_argument("--slug", default=None)
    args = p.parse_args()

    for v in (args.honshitsu, args.hyoumen, args.ishikettei, args.kakure, args.kibou):
        if v not in ANIMALS:
            print(f"未知の動物名です: {v}（{list(ANIMALS.keys())}）", file=sys.stderr)
            sys.exit(1)

    html = build(args.honshitsu, args.hyoumen, args.ishikettei, args.kakure, args.kibou, args.name)

    slug = args.slug or datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(out_path)


if __name__ == "__main__":
    main()

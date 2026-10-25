import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';

const script = `import importlib.util, json, sys
spec=importlib.util.spec_from_file_location("handbook_builder","scripts/build_handbook_site.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
roles=json.load(sys.stdin)
try:
    mod.validate_role_sections("homebath", "staffing", roles)
except ValueError as exc:
    print(str(exc))
    sys.exit(2)
`;
function validate(roles) {
 const r=spawnSync('python',['-B','-c',script],{input:JSON.stringify(roles),encoding:'utf8'});
 assert.equal(r.error,undefined,String(r.error));
 return r;
}
function sample(kind) {
 return [{id:'care-team',title:'介護職員',requirements:[{
  id:'placement',title:'配置',aspect:'placement',description:'条件と例外の記述を保持する。',
  applicability:'指定事業所（詳細は未確認）',verification_state:'EVIDENCE_GAP',
  practical_checks:['勤務表の確認'],evidence:[{
   kind,title:'候補資料（検証用）',issuer:'検証用',locator:'該当箇所は未確認',
   version:'未確認',scope:'未確認',checked_at_jst:'',
   verification_state:'SOURCE_CANDIDATE_UNVERIFIED',
  }],
 }]}];
}
test('national law, form, fee notice, city regulation have distinct allowed evidence kinds',()=>{
 for(const kind of ['national_law','national_form','national_fee_notice','yokohama_regulation']){
   assert.equal(validate(sample(kind)).status,0,kind);
 }
});
test('source kinds remain fail-closed; unchecked links and fake checked timestamps are rejected',()=>{
 const bad=sample('made_up_kind');
 assert.equal(validate(bad).status,2);
 const url=sample('national_form');
 url[0].requirements[0].evidence[0].url='https://www.mhlw.go.jp/sample';
 assert.equal(validate(url).status,2);
 const date=sample('national_fee_notice');
 date[0].requirements[0].evidence[0].checked_at_jst='2026-10-26 06:15 JST';
 assert.equal(validate(date).status,2);
});
test('schema and UI retain exact matching source-kind names',()=>{
 const types=fs.readFileSync('lib/working-handbook.ts','utf8');
 const ui=fs.readFileSync('components/service-handbook.tsx','utf8');
 const validator=fs.readFileSync('scripts/build_handbook_site.py','utf8');
 for(const kind of ['national_law','national_form','national_fee_notice','yokohama_regulation']){
  assert.ok(types.includes('"'+kind+'"'));
  assert.ok(ui.includes(kind+':'));
  assert.ok(validator.includes('"'+kind+'"'));
 }
 assert.ok(ui.includes('evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" && evidence.url'));
});

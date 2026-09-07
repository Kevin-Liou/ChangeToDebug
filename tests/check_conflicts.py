"""conflicts：衝突產物寫出、同檔多規則併筆、.merged 產生、寫回專案的把關。"""
from pathlib import Path

from _common import Checker, quiet_logger, redirect_conflicts, rmtree, sandbox

from changetodebug.core import conflicts, threeway

ck = Checker()
tmp = sandbox("ctd_conf_")
redirect_conflicts(tmp)
quiet = quiet_logger()


class FakeRule:
    def __init__(self, label, rule_id):
        self.label, self.rule_id = label, rule_id


try:
    proj = tmp / "proj"
    (proj / "sub").mkdir(parents=True)
    tgt = proj / "sub" / "X.c"
    tgt.write_text("a\nUPSTREAM\nb\nc\nd\n", encoding="utf-8")
    base = "a\nb\nc\nd"

    ck.section("make_writer 與同檔多規則")
    writer = conflicts.make_writer(str(proj), "20260101000000", quiet)
    r1 = writer(str(tgt), base, "a\nRULE1\nb\nc\nd", "a\nUPSTREAM\nb\nc\nd", FakeRule("規則一", "mod:1"), 1)
    r2 = writer(str(tgt), base, "a\nb\nc\nd\nRULE2", "a\nUPSTREAM\nb\nc\nd", FakeRule("規則二", "mod:2"), 1)
    ck("三方檔案都寫出", all(Path(getattr(r1, k)).is_file() for k in ("base", "profile", "current")))
    ck("兩條規則併成一筆", len(writer.records) == 1 and r1 is r2)
    ck("label / rule_id 累積", r1.label == "規則一、規則二" and r1.rule_id == "mod:1,mod:2")
    prof = Path(r1.profile).read_text(encoding="utf-8")
    ck(".profile 疊加兩條規則的期望", "RULE1" in prof and "RULE2" in prof)
    ck("產物落在導向後的暫存目錄", str(writer.root).startswith(str(tmp)))

    ck.section("build_merged")
    ck("一開始沒有 .merged", not Path(r1.merged).exists())
    failed = conflicts.build_all_merged(writer.records, quiet, overwrite=True)
    m = Path(r1.merged).read_text(encoding="utf-8")
    ck("產生成功且帶標記", not failed and threeway.has_markers(m) and "UPSTREAM" in m and "RULE1" in m)
    Path(r1.merged).write_text("我解好了\n", encoding="utf-8")
    conflicts.build_merged(r1, quiet, overwrite=False)
    ck("overwrite=False 不覆蓋已解好的內容", Path(r1.merged).read_text(encoding="utf-8").strip() == "我解好了")
    conflicts.build_merged(r1, quiet, overwrite=True)
    ck("overwrite=True 重新產生", threeway.has_markers(Path(r1.merged).read_text(encoding="utf-8")))

    ck.section("index 讀寫")
    conflicts.write_index(writer.root, writer.records, quiet)
    back = conflicts.load_index(writer.root)
    ck("index.yaml 讀回一筆且欄位完整", len(back) == 1 and back[0].rule_id == "mod:1,mod:2"
       and back[0].merged == r1.merged)
    ck("latest_run 找得到", conflicts.latest_run(str(proj)) == writer.root)

    ck.section("apply_resolved 的把關")
    rec = r1
    rec.newline = "\r\n"
    ok, why = conflicts.apply_resolved(rec, quiet)
    ck("未解決（仍是標記）-> 拒絕", not ok and "尚未解決" in why, why)
    Path(rec.merged).write_text("   \n", encoding="utf-8")
    ck("空內容 -> 拒絕", not conflicts.apply_resolved(rec, quiet)[0])
    Path(rec.merged).write_text("a\n#=========================================\nRULE1\nUPSTREAM\nb\n", encoding="utf-8")
    ok, why = conflicts.apply_resolved(rec, quiet)
    written = Path(rec.target).read_bytes()
    ck("含 ===== 分隔線的正常內容 -> 寫入", ok, why)
    ck("寫回時還原 CRLF、無落單 LF", b"\r\n" in written and written.replace(b"\r\n", b"").count(b"\n") == 0)
    ok, why = conflicts.apply_resolved(rec, quiet)
    ck("與現況相同 -> 不重複寫", not ok and "相同" in why)
    Path(rec.merged).write_text("﻿BOMTEST\nz\n", encoding="utf-8")
    ok, _ = conflicts.apply_resolved(rec, quiet)
    ck("BOM 被去掉", ok and not Path(rec.target).read_bytes().startswith(b"\xef\xbb\xbf"))
    ck("目標檔的確被改到", "BOMTEST" in Path(rec.target).read_text(encoding="utf-8"))
finally:
    rmtree(tmp)

ck.finish("conflicts")

"""threeway：diff3 合併、衝突標記輸出、標記偵測、added_lines。"""
from _common import Checker

from changetodebug.core import threeway as t

ck = Checker()
ck.section("合併分類")
base = "a\nb\nc\nd\ne"
r = t.merge_text(base, "a\nX\nc\nd\ne", "a\nb\nc\nY\ne")
ck("兩邊改不同區 -> 都保留、無衝突", r.ok and r.text == "a\nX\nc\nY\ne" and r.took_ours == 1 and r.took_theirs == 1)
r = t.merge_text(base, "a\nX\nc\nd\ne", "a\nX\nc\nd\ne")
ck("兩邊改法相同 -> same", r.ok and r.same == 1 and r.text == "a\nX\nc\nd\ne")
r = t.merge_text(base, "a\nX\nc\nd\ne", "a\nY\nc\nd\ne")
ck("同一區改法不同 -> 衝突", not r.ok and len(r.conflicts) == 1
   and r.conflicts[0].ours == ["X"] and r.conflicts[0].theirs == ["Y"] and r.conflicts[0].base == ["b"])
ck("blocks 記錄了 text / conflict 的順序", [k for k, _ in r.blocks] == ["text", "conflict", "text"])

ck.section("衝突標記")
m = t.render_conflicts(r)
ck("四種標記各一", all(m.count(x) == 1 for x in (t.MARK_LEFT, t.MARK_BASE, t.MARK_MID, t.MARK_RIGHT)))
ck("左＝目前 source（theirs）、右＝profile（ours）",
   m.index("Y") < m.index(t.MARK_MID) < m.index("X"))
ck("無衝突時 render == text", t.render_conflicts(t.merge_text("a\nb", "a\nb", "a\nb")) == "a\nb")

ck.section("has_markers 不誤判")
for name, text, expect in [
    ("純 ===== 分隔線", "#================================\nint x;", False),
    ("只有 =======", "=======\nfoo", False),
    ("完整標記", "<<<<<<< a\nx\n=======\ny\n>>>>>>> b", True),
    ("字串裡的標記", 'char *s = "<<<<<<< not a marker";', False),
    ("只有左邊", "<<<<<<< a\nx\n", False),
]:
    ck(name, t.has_markers(text) == expect)

ck.section("added_lines")
ck("只回傳真正新增的非空白行",
   t.added_lines("a\n  b\n\nc", "a\n  b\n  NEW\n\nc\n\n") == ["  NEW"])
ck("純刪除 -> 空", t.added_lines("a\nb\nc", "a\nc") == [])

ck.finish("threeway")
